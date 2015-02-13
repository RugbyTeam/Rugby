# internal
from rugby import Rugby
import config 

# stdlib
import logging

# Set up logger
logger = logging.getLogger(config.LOGGER_NAME)
logger.setLevel(logging.DEBUG)
# Create console transport
ct = logging.StreamHandler()
ct.setLevel(logging.DEBUG)
# Create a formatter
formatter = logging.Formatter('%(levelname)s: %(filename)s line %(lineno)d: %(message)s')
ct.setFormatter(formatter)
# Add transports to logger
logger.addHandler(ct)

