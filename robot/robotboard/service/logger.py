import sys

from logging.handlers import SysLogHandler
import logging


def setup_logger():
    formatter = logging.Formatter(
        fmt=(
            "%(asctime)s "
            "[robotboard:%(process)d] "
            "[%(levelname)s] "
            "%(message)s"
        ), datefmt="%Y-%m-%dT%H:%M:%S%z")
    
    logger = logging.getLogger("robot")
    logger.setLevel(logging.DEBUG)

    #syslog_handler = SysLogHandler('/var/log')
    #syslog_handler.setFormatter(formatter)

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)

    #logger.addHandler(syslog_handler)
    logger.addHandler(console_handler)

LOGGER = logging.getLogger("robot")

