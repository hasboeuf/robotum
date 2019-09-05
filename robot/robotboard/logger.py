import sys

from logging.handlers import RotatingFileHandler
import logging


def setup_logger():
    formatter = logging.Formatter(
        fmt=("%(asctime)s " "[robotboard:%(process)d] " "[%(levelname)s] " "%(message)s"), datefmt="%Y-%m-%dT%H:%M:%S%z"
    )

    logger = logging.getLogger("robot")
    logger.setLevel(logging.DEBUG)

    file_handler = RotatingFileHandler("/var/log/robot/robot.log", maxBytes=10 * 1024 * 1024, backupCount=5)
    file_handler.setFormatter(formatter)

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)


LOGGER = logging.getLogger("robot")
