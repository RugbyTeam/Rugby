# internal
from rugby_worker import RugbyWorker
import config

# stdlib
from multiprocessing import Process, Pipe
from threading import Thread
import time
import logging

logger = logging.getLogger(config.LOGGER_NAME)

class WorkerInfo:
    """
    Struct to hold all the info we need about a RugbyWorker
    """
    def __init__(self, worker_pid, worker_msg_pipe):
        self.pid = worker_pid
        self.msg_pipe = worker_msg_pipe

        # Will be set as Worker starts to work (haha)
        self.state = None

class Rugby:
    """
    Rugby Globals
        - workers: Dictionary of all rugby workers
            { "<commit_id>" : {"worker" : <WorkerInfo>} }
    """
    workers = {}

    def __init__(self, rugby_root=config.BASE_DIR):
        """
        rugby_root = Directory where all rugby generated files
                     should be placed
        """
        self.rugby_root = rugby_root

    def start_runner(self, commit_id, rugby_config):
        """
        Method takes a unique commit_id and a path (rugby_config)
        to a rugby config file and creates a rugby worker which will 
        execute all the instructions in the config
        """
        # Instantiate a worker
        rw = RugbyWorker(commit_id, self.rugby_root, rugby_config)
        
        # Create pipe for interprocess communication
        my_end, their_end = Pipe()

        # Start worker process
        worker_process = Process(target=rw, args=(their_end,))
        worker_process.start()

        # Record worker info
        worker_info = WorkerInfo(worker_process.pid, my_end)
        Rugby.workers[commit_id] = worker_info

def worker_poller():
    """
    This function continuously polls every rugby worker in 
    Rugby.workers to see if they have a message to share 
    with us. Actions are performed based on those messages.
    """
    while True:
        for worker_id, worker in Rugby.workers.iteritems():
            # If worker has sent a message
            if worker.msg_pipe.poll():
                # Fetch message from pipe
                msg = str(worker.msg_pipe.recv()) 
                logger.debug(msg)   

        # Wait a bit before checking again
        time.sleep(5)

# Start polling workers 
t = Thread(target=worker_poller)
t.daemon = True
t.start()
