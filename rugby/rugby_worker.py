# internal
from rugby_state import RugbyState
from rugby_loader import RugbyLoader
import config

# external
from vagrant import Vagrant

# stdlib
import errno
import os
import time
import sys

class RugbyWorker:
    def __init__(self, commit_id, rugby_root_dir, rugby_config_path):
        """
        commit_id = Unique identifier for worker
        root_dir  = Base directory where worker should
                    create its own worker directory
        conf_path = Path to rugby configuration file
        """
        self.commit_id = str(commit_id)
        self.root_dir = os.path.join(str(rugby_root_dir), self.commit_id)
        self.conf_path = str(rugby_config_path)
        
        """
        Private member variables
            _state    = Current state of worker
            _vagrant  = Vagrant Object which we use to interface
                        with VMs
            _msg_pipe = Connection Object which is used to send/recieve messages
                        with process that spawned this worker
        """
        self._state = RugbyState.STANDBY
        self._vagrant = None
        self._msg_pipe = None

    def __call__(self, msg_pipe):
        # Set pipe (multiprocessing.Connection) which will
        # be used to talk to parent process who spawned this
        # worker
        self._msg_pipe = msg_pipe

        # Initialize
        self._state = RugbyState.INITIALIZING
        self._initialization()
        
        # Spawn VMs
        self._state = RugbyState.SPAWNING_VMS
        self._spawn_vms()

    def _initialization(self):
        """
        Helper function for running initialization
        tasks. 
            - Create Directory for VMs
            - Generate Vagrantfile from rugby conf
        """
        self._send_msg("Creating VM Directory")
        
        # Create directory for storing VM data
        try:
            os.makedirs(self.root_dir)
        except OSError as e:
            # Directory shouldn't already have existed,
            # but if it did, worker should still be able
            # to continue
            if e.errno == errno.EEXIST and os.path.isdir(self.root_dir):
                pass    
            
            self._suicide("Failed to create root directory")
            
        # Parse rugby config and generate
        # Vagrantfile into root dir
        try:
            rugby_loader = RugbyLoader(self.conf_path)
            rugby_loader.render_vagrant(self.root_dir)
        except Exception:
            self._suicide("Failed to generate Vagrantfile from config")

        # Set internal vagrant object, initializing
        # it to self.root_dir
        try:
            self._vagrant = Vagrant(self.root_dir)
        except Exception:
            self._suicide("Failed to instantiate internal vagrant object")

    def _spawn_vms(self):
        """
        Helper function which executes vagrant
        to bring up VM's and provisions them with 
        our basic packages (defined in Vagrantfile)
        """
        self._send_msg("Starting up VMs and performing initial provisioning")

        # Start VMs
        try:
            self._vagrant.up()
        except Exception:
            self._suicide("Failed to complete vagrant up")

    def _send_msg(self, msg):
        """
        Helper function for writing to self.msg_pipe.
        Appends meta data needed to identify worker

        Format:
            <commit_id> <state> <msg>
        """
        complete_msg = "{} {} {}".format(self.commit_id, self._state, msg)
        self._msg_pipe.send(complete_msg)

    @staticmethod
    def extract_id_and_state(msg):
        """
        This method takes a message sent using RugbyWorker._send_msg
        in the following format
            <commit_id> <state> <msg>
        and returns the first 2 components.
            [commit_id, state]
        """
        split_msg = msg.split(' ')
        return split_msg[0], split_msg[1]

    def _suicide(self, msg):
        """
        Helper function which will set error state, send
        message to parent process, then kill the process
        """
        self._state = RugbyState.ERROR
        self._send_msg(msg)
        sys.exit(1)
