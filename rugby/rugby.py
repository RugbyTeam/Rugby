# internal
from rugby_worker import RugbyWorker
from rugby_state import RugbyState
from rugby_database import RugbyDatabase
import config

# stdlib
from multiprocessing import Process, Pipe
from threading import Thread
import time
import logging
import sys
import signal
import os

logger = logging.getLogger(config.LOGGER_NAME)

class BuildInfo:
    """
    Holding all the information needed for a build
    """
    def __init__(self, commit_obj):
        self.commit_id = commit_obj["commit_id"]
        self.commit_message = commit_obj["commit_message"]
        self.commit_url = commit_obj["commit_url"]
        self.commit_timestamp = commit_obj["commit_timestamp"]
        self.finish_timestamp = None
        self.author_login = commit_obj["author_login"]
        self.author_email = commit_obj["author_email"]
        self.author_avatar_url = commit_obj["author_avatar_url"]
        self.contributors_email = commit_obj["contributors_email"]
        self.clone_url = commit_obj["clone_url"]
        self.raw_url = commit_obj["raw_url"]

class WorkerInfo:
    """
    Struct to hold all the info we need about a RugbyWorker
    """
    def __init__(self, worker_pid, worker_msg_pipe, worker_callbacks):
        self.pid = worker_pid
        self.msg_pipe = worker_msg_pipe
        # List of callback functions to call when worker state
        # changes
        #
        # Format of callback
        #   func_name('<commit_id>, '<RugbyState>')
        self.callbacks = worker_callbacks
        
        # Will be set as Worker starts to work (haha)
        self.state = None

    def __del__(self):
        """
        Close msg_pipe when reference to worker is lost
        """
        self.msg_pipe.close()

class Rugby:
    """
    Rugby Globals
        - workers: Dictionary of all rugby workers
            { "<commit_id>" : {"worker" : <WorkerInfo>} }
        - defunct_workers: Array of commit_id's which should be removed from
                           workers dict.
    """
    workers = {}
    defunct_workers = []

    def __init__(self, rugby_root=config.BASE_DIR, rugby_log_dir=config.LOG_DIR):
        """
        rugby_root    = Directory where all rugby generated files
                        should be placed
        rugby_log_dir = Directory where all rugby worker logs should
                        be placed
        """
        self.rugby_root = rugby_root
        self.rugby_log_dir = rugby_log_dir
        self.rugby_db = RugbyDatabase(rugby_root)

    def get_builds(self):
        return self.rugby_db.get_builds()

    def get_info(self, commit_id):
        """
        Method takes a unique commit_id and returns a dictionary containing 
        all the information related to it.
        """
        return self.rugby_db.get_info(commit_id) 

    def start_runner(self, build_info, rugby_config, *args):
        """
        Method takes a unique commit_id, clone_url for the repo with the commit id,
        a path (rugby_config) to a rugby config file, and any number of callback functions 
        and creates a rugby worker which will execute all the instructions 
        in the config. The callback functions will be called everytime there 
        is a state change in the worker.

        Format of a callback:

            func_name(<commit_id>, <RugbyState>)

        Where commit_id is the unique id used to spawn the worker, and RugbyState is
        the workers current state, which can be found in rugby_state.py
        """
        commit_id = build_info.commit_id
        clone_url = build_info.clone_url
        raw_url = build_info.raw_url

        # Instantiate a worker
        rw = RugbyWorker(commit_id, clone_url, raw_url, self.rugby_root, rugby_config)
        
        # Create pipe for interprocess communication
        my_end, their_end = Pipe()

        # Create a log file for Worker to send output to
        worker_log_path = os.path.join(self.rugby_log_dir, commit_id)
        with open(worker_log_path, 'a') as f:
            f.write('Starting job with commit id {}... \n\n'.format(commit_id)) 

        # Start worker process
        worker_process = Process(target=rw, args=(their_end, worker_log_path))
        worker_process.start()
        
        # Record database entry
        self.rugby_db.insert_build(build_info)

        # Set callbacks
        callbacks = (self.rugby_db.update_build,) + args

        # Record worker info
        worker_info = WorkerInfo(worker_process.pid, my_end, callbacks)
        Rugby.workers[commit_id] = worker_info

    @staticmethod
    def state_change(commit_id, worker_state):
        """
        Method takes a commit_id and worker_state, and sets the corresponding
        Worker's state appropriatly. If the worker's state is ERROR or
        SUCCESS, we add the worker to defunct_workers so they can be reaped
        """
        Rugby.workers[commit_id].state = worker_state
        if worker_state == str(RugbyState.SUCCESS) or worker_state == str(RugbyState.ERROR):
            # Add worker to defunct list
            Rugby.defunct_workers.append(commit_id)

    @staticmethod
    def reap_defunct():
        """
        Method removes each defunct_workers from workers, initiating
        their destructor
        """
        for i in Rugby.defunct_workers:
            # Delete worker from workers
            del Rugby.workers[i]

        # Clear defunct list
        Rugby.defunct_workers = []

def worker_poller():
    """
    This function continuously polls every rugby worker in 
    Rugby.workers to see if they have a message to share 
    with us. State is changed based on the message. 
    """
    while True:
        for worker_id, worker in Rugby.workers.iteritems():
            # If worker has sent a message
            if worker.msg_pipe.poll():
                # Fetch message from pipe
                recv_msg = str(worker.msg_pipe.recv()) 
                logger.debug(recv_msg)
                # Extract info from recv_msg
                # NOTE: commit_id and worker_id should be equal
                # to each other
                commit_id, state = RugbyWorker.extract_id_and_state(recv_msg)
                # Run worker callback functions with the new state
                # information
                for cb in worker.callbacks:
                    # Run each callback
                    t = Thread(target=cb, args=(commit_id, state))
                    t.start()
                # Perform state change. State might not always change
                # if current worker state is already set to what is present
                # in the message
                Rugby.state_change(commit_id, state)

        # Reap all defunct workers
        Rugby.reap_defunct()

        # Wait a bit before iterating through workers again
        time.sleep(5)

# Start polling workers 
t = Thread(target=worker_poller)
t.daemon = True
t.start()

def sigint_handler(sig_num, frame):
    """
    Handler for when Ctrl-C, or SIGINT is sent. This
    function will perform proper cleanup if necessary
    """

    if len(Rugby.workers) > 0:
        logger.debug("Performing cleanup tasks, don't spam Ctrl-C")
        # Delete workers. Doing this calls the __del__ method on each
        # worker which should perform cleanup
        Rugby.workers = {}

    sys.exit(1)

# Install sigint handler
signal.signal(signal.SIGINT, sigint_handler)
