# external
from ansible.runner import Runner

# stdlib
import os

class RugbyCommand:
    """
    This class is a wrapper around ansible.runner.Runner. It makes
    it easier to run ansible modules on Vagrant VMs and prints any
    resulting output to stdout/stderr
    """
    def __init__(self, remote_user, host_list_path, private_key_path):
        """
        remote_user     = Target remote user name. Should be just vagrant by
                          default
        host_list_path  = Path to generated Vagrant host file
        private_key_path = Path to ssh key used to remote into VM 
        """
        self.remote_user = remote_user
        self.host_list_path = host_list_path
        self.private_key_path = private_key_path

    def run(self, **kwargs):
        """
        Main function which will run Ansible Runner with necessary
        arguments and environment
        """
        # Needed to skip ssh host identification which causes
        # ansible to fail normally.
        # See https://github.com/ansible/ansible/issues/9442
        os.environ['ANSIBLE_HOST_KEY_CHECKING'] = 'False'

        # Run task
        cmd = Runner(host_list=self.host_list_path,
                     private_key=self.private_key_path,
                     remote_user=self.remote_user,
                     *kwargs)

        results = cmd.run()

        # Print any error that may have occured, and throw exception

