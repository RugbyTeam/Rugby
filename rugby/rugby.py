import config

from subprocess import Popen
from enum import Enum
import threading
import os

import logging

rugby_log = logging.getLogger('rugby_log')
rugby_log.setLevel(logging.DEBUG)

class RugbyState(Enum):
    standby = 1
    provisioning = 2
    running = 3
    success = 4
    fail = 5

class Rugby:
    """
    Rugby Globals
        - tasks: dictionary that holds current Rugby tasks and the commit ID 

    """
    tasks = {}

    """
    Rugby Methods

    """
    def __init__(self, rugby_root):
        self.rugby_root = rugby_root

    def up(self, commit_id, clone_url):
        rt = RugbyTask(commit_id, self.rugby_root, clone_url)
        Rugby.tasks[commit_id] = rt
        rt.provision()

    def status(self):
        return Rugby.tasks

class RugbyTask:
    """
    RugbyTask Globals
        - process_pool: list that holds currently running subprocesses
    """
    task_pool = []

    def __init__(self, commit_id, rugby_root, clone_url):
        self.commit_id = commit_id
        self.vagrant_cwd = rugby_root + ("/%s" % commit_id)

        if not os.path.exists(self.vagrant_cwd):
            os.makedirs(self.vagrant_cwd)

        self.clone_url = clone_url
        self.state = RugbyState.standby

    def provision(self):
        self.state = RugbyState.provisioning
        #print "Running vagrant up on... %s" % self.vagrant_cwd
        #rugby_log.debug("Running vagrant up on... %s" % self.vagrant_cwd)

        # Start the VMs
        logfile = self.vagrant_cwd + ("/%s.log" % self.commit_id)
        with open(logfile, 'a') as f:
            self.pproc = Popen([config.SCRIPTS_DIR + '/vagrant_wrapper.sh'], stdout=f)
            RugbyTask.task_pool.append(self)

    def notify(self):
        # Analyze provisioning status
        if self.pproc.poll() != 0:
            self.state = RugbyState.fail
            print "Provisioning Process Failed"
        else:
            self.run_all_tests()

    def run_test(self, test):
        print "%s running test %s" % (self.commit_id, test)

    def run_all_tests(self):
        print "%s running all tests" % self.commit_id

# Start up subprocess poller
def task_poller():
    while True:
        for task in RugbyTask.task_pool:
            if task.pproc.poll() != None:
                print "Process Terminated... ", task.pproc, " Exit code: %d" % task.pproc.poll()
                RugbyTask.task_pool.remove(task)
                task.notify()

t = threading.Thread(target=task_poller)
t.daemon = True
t.start()


