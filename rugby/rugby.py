import os

class Rugby:
    """
    Rugby Globals
        - vagrant_cwd = directory for vagrant to look for Vagrantfile
        - tests = dictionary that holds all the tests and how to run them

    """
    vagrant_cwd = os.getcwd()
   
    #TODO: Rethink this file referencing... This is hacky
    run_test_script = "run_tests.sh"
    up_script = "run_playbooks.sh"

    tests = {}


    """
    Rugby Methods

    """
    def __init__(self, directory):
        self.vagrant_cwd = directory

    def up(self):
        # Execute vagrant up scripts here
        print "Running vagrant up on ... %s" % self.vagrant_cwd

    def run_test(self, test):
        # Execute ansible-playbook commands to run individual tests.
        print "run_test"

    def run_all_tests(self):
        # Executs all tests in tests dictionary
        print "run_all_tests"
