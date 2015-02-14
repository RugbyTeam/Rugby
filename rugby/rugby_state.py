# external
from enum import Enum

class RugbyState(Enum):
    STANDBY = 1
    INITIALIZING = 2
    SPAWNING_VMS = 3
    PROVISIONING = 4
    TESTS_RUNNING = 6
    CLEANING_UP = 7
    ERROR = 8
    SUCCESS = 9
