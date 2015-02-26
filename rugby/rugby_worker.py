# internal
from rugby_state import RugbyState
from rugby_loader import RugbyLoader
import config

# external
from vagrant import Vagrant
from fabric.api import settings, env, sudo, hide

# stdlib
import errno
import os
import time
import sys
import shutil

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
            _log_fd   = File descriptor where output to be logged should go
            _conf_obj = Dict representation of rugby config 
        """
        self._state = RugbyState.STANDBY
        self._vagrant = None
        self._msg_pipe = None
        self._log_fd = None
        self._conf_obj = None

    def __call__(self, msg_pipe, log_path=os.devnull):
        # Set pipe (multiprocessing.Connection) which will
        # be used to talk to parent process who spawned this
        # worker
        self._msg_pipe = msg_pipe

        # Create fd from log_path which is where select output
        # from worker will be sent. Output is unbuffered
        try:
            self._log_fd = open(log_path, 'a', 0)
        except Exception:
            self._suicide("Couldn't open {} for piping worker output".format(log_path))

        # Save orginal stdout and stderr
        orig_stdout = sys.stdout
        orig_stderr = sys.stderr 

        # Initialize
        self._state = RugbyState.INITIALIZING
        self._initialization()
        
        # If we are in DEBUG_MODE, we probably also want to log the
        # initial bring up of VMs, eventhough this is info our user
        # would not want to see
        if config.DEBUG_MODE == True:
            sys.stdout = sys.stderr = self._log_fd
        
        # Spawn VMs
        self._state = RugbyState.SPAWNING_VMS
        self._spawn_vms()

        # Log output from user defined actions. If DEBUG_MODE is on,
        # then output is already being logged and we don't have to do
        # anything
        if config.DEBUG_MODE == False:
            sys.stdout = sys.stderr = self._log_fd

        # Run any install commands
        self._state = RugbyState.RUNNING_INSTALL
        self._install()

        # Set stdout and stderr back to what they were originally
        sys.stdout = orig_stdout
        sys.stderr = orig_stderr

        # Cleanup
        self._state = RugbyState.CLEANING_UP
        self._cleanup()

        # Done! If we made it to here, there were no errors
        self._state = RugbyState.SUCCESS
        self._send_msg("Finished")

        # Close message pipe, we do it here and not in the 
        # cleanup function because we still needed to notify
        # the parent that we have finished
        self._msg_pipe.close()

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

        # Set internal conf_obj to Dict version of rugby config
        self._conf_obj = rugby_loader.rugby_obj

        # Set internal vagrant object, initializing
        # it to self.root_dir
        try:
            self._vagrant = Vagrant(self.root_dir, quiet_stdout=False, quiet_stderr=False)
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

    def _install(self):
        """
        Helper function which executes all user defined
        install commands
        """
        self._send_msg("Running install commands")

        for vm in self._conf_obj:
            if 'install' in vm.keys():
                # VM info needed to run command through fabric
                keyfile = self._vagrant.keyfile(vm['name'])
                user = self._vagrant.user(vm['name'])
                port = self._vagrant.port(vm['name'])
                host = self._vagrant.hostname(vm['name'])

                # Set passphrase/sudo password so we arn't prompted
                # should be default by 'vagrant'
                env.password = 'vagrant' 

                # Disable fabric output prefixes IE ip and output stream info
                env.output_prefix = False

                # Prevent fabric from kicking us out from the script when
                # a command fails
                env.warn_only = True

                for cmd in vm['install']:
                    with settings(hide('aborts','warnings'),
                                  key=keyfile,
                                  user=user, 
                                  port=port, 
                                  host_string=host, 
                                  disable_known_hosts='True', 
                                  forward_agent='True',
                                  abort_on_prompts='True'):
                        
                        return_obj = sudo(cmd)

                        # If command failed, we should bail
                        if return_obj.failed == True:
                            self._suicide('Command \'{}\' failed to run'.format(cmd))

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
        message to parent process, cleanup, then kill the process
        """
        self._state = RugbyState.ERROR
        self._send_msg(msg)
        self._cleanup()
        sys.exit(1)

    def _cleanup(self):
        """
        Helper function which will delete any files generated
        by worker (except log file), and close open file descriptor
        """
        self._send_msg("Cleaning up")
        if os.path.isdir(self.root_dir):
            # Destroy VMs
            self._vagrant.destroy()
            # Remove root directory
            try:
                shutil.rmtree(self.root_dir, ignore_errors=True)
            except Exception:
                pass

        # Close log fd
        if self._log_fd != None:
            self._log_fd.close()
