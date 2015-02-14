# internal
from rugby_state import RugbyState
from rugby_loader import RugbyLoader
import config

# external
import vagrant

# stdlib
import os
import time

class RugbyWorker:
    def __init__(self, commit_id, rugby_root_dir, rugby_config_path, msg_pipe):
        """
        commit_id = Unique identifier for job
        root_dir = Base directory where workers should
                   create directories
        conf_path = Path to rugby configuration file
        state = Current worker state
        msg_pipe = Messaging connection to parent process
        log_file_paths = List of paths to all logfiles 
                         generated by tasks
        """
        self.commit_id = commit_id
        self.root_dir = os.path.join(rugby_root_dir, commit_id)
        self.conf_path = rugby_config_path
        self.state = rugby_state.STANDBY
        self.msg_pipe = msg_pipe
        self.log_file_paths = []

    def __call__(self):
        self._initialization()
        self._spawn_vms()

    def _initialization(self):
        """
        Helper function for running initialization
        tasks. 
            - Create Directory for VMs
            - Generate Vagrantfile
        """
        self.state = rugby_state.INITIALIZATION
        
        # Create directory for storing VM data
        try:
            os.makedirs(self.root_dir)
        except OSError:
            self._error_state("Failed to create root directory")

        # Parse rugby config and generate
        # Vagrantfile into root dir
        try:
            rugby_load = RugbyLoader(self.conf_path)
            rugby_load.render_vagrant(self.root_dir)
        except Exception:
            self._error_state("Failed to generate vagrantfile from config")

    def _spawn_vms(self):
       """
       Helper function which executes vagrant
       to bring up VM's
       """

    def _send_msg(self, msg):
        """
        Helper function for writting to self.msg_pipe.
        Appends meta data needed to identify worker
        """
        complete_msg = "{} {} {}".format(self.commit_id, self.state, msg)
        self.msg_pipe.send(complete_msg)
    
    def _error_state(self, msg):
        """
        Helper function. Sets worker state to error,
        notifies parent, and suspends worker
        """
        self.state = RugbyState.ERROR
        self._send_msg(msg)
        self._wait_for_response

    def _wait_for_response(self):
        """
        Helper function. Should be called anytime the process
        needs to wait for a response from the parent process
        """
        # Busy waiting
        while 1:
            time.sleep(5)

