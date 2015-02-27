# external
from enum import Enum

class RugbyState(Enum):
    STANDBY = 1
    INITIALIZING = 2
    SPAWNING_VMS = 3
    CLONING_SOURCE = 4
    RUNNING_INSTALL = 5
    RUNNING_TESTS = 6
    CLEANING_UP = 7
    ERROR = 8
    SUCCESS = 9
