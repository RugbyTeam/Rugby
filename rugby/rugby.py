# internal
from rugby_loader import RugbyLoader
import config

# external
from enum import Enum

# stdlib
from subprocess import Popen
import logging
import threading
import os

logger = logging.getLogger(config.LOGGER_NAME)

class RugbyState(Enum):
    standby = 1
    provisioning = 2
    running = 3
    success = 4
    fail = 5

class Rugby:
    """
    Rugby Globals
        - tasks: dictionary that holds all Rugby tasks referenced by commit ID 
    """
    tasks = {}

    """
    Rugby Methods
    """
    def __init__(self, rugby_root):
        self.rugby_root = rugby_root

    def up(self, commit_id, rugby_config):
        rt = RugbyTask(commit_id, self.rugby_root, rugby_config)
        Rugby.tasks[commit_id] = rt
        rt.provision()

    def status(self):
        return Rugby.tasks

class RugbyTask:
    """
    RugbyTask Globals
        - task_pool: list that holds currently running task subprocesses
    """
    task_pool = []

    """
    RugbyTask Methods
    """
    def __init__(self, commit_id, rugby_root, rugby_config):
        self.commit_id = commit_id
        self.vagrant_cwd = os.path.join(rugby_root, commit_id)
        self.rugby_config = rugby_config
        self.state = RugbyState.standby

    def provision(self):
        self.state = RugbyState.provisioning

        try:
            if not os.path.exists(self.vagrant_cwd):
                os.makedirs(self.vagrant_cwd)

            #TODO: Parse rugby_config here and place in vagrant_cwd
            # set state to fail if parse failed
            
            rugby_load = RugbyLoader(self.rugby_config)
            rugby_load.render_vagrant(self.vagrant_cwd)
        except OSError:
            logger.error("RugbyTask Provisioning OSError")

        # Start the VMs
        logfile = os.path.join(self.vagrant_cwd, '%s.log' % self.commit_id)
        with open(logfile, 'a') as f:
            self.pproc = Popen([config.VAGRANT_WRAPPER_SCRIPT, self.vagrant_cwd, "up"], stdout=f, stderr=f)
            RugbyTask.task_pool.append(self)

    def notify(self):
        # Analyze provisioning status
        if self.pproc.poll() != 0:
            self.state = RugbyState.fail
            logger.error("Provisioning Process Failed")
        else:
            self.run_all_tests()

    #TODO: Define how tests work... how they are referenced and run
    def run_test(self, test):
        logger.info("{} running test {}".format(self.commit_id, test))

    def run_all_tests(self):
        logger.info("{} running all tests".format(self.commit_id))

# Start up subprocess poller
def task_poller():
    while True:
        for task in RugbyTask.task_pool:
            if task.pproc.poll() != None:
                logger.debug("Process Terminated... {} Exit code: {}".format(task.pproc.poll(), task.pproc))
                RugbyTask.task_pool.remove(task)
                task.notify()

t = threading.Thread(target=task_poller)
t.daemon = True
t.start()


