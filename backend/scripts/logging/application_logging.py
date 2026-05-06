"""
logger utility
"""

import logging
import os
import time
from functools import wraps
from logging.handlers import RotatingFileHandler

from scripts.config import logging_details

complete_log_path = os.path.join(
    logging_details.log_base_path, logging_details.log_file_name
)
if not os.path.exists(logging_details.log_base_path):
    os.mkdir(logging_details.log_base_path)


def timed(func):
    """This decorator prints the execution time for the decorated function."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        logger.debug("{} ran in {}s".format(func.__name__, round(end - start, 5)))
        return result

    return wrapper


def get_logger(
    log_file_name=complete_log_path,
    log_level=logging_details.log_level,
    time_format="%Y-%m-%d %H:%M:%S",
    handler_type=logging_details.handler_type,
    max_bytes=logging_details.log_max_bytes,
    backup_count=logging_details.backup_count,
):
    """
    Creates a rotating log
    """
    log_file = os.path.join(log_file_name + ".log")
    __logger__ = logging.getLogger(log_file_name)
    __logger__.setLevel(log_level.strip().upper())
    debug_formatter = (
        "%(asctime)s - %(levelname)-6s - %(name)s - "
        "[%(threadName)5s:%(filename)5s:%(funcName)5s():"
        "%(lineno)s] - %(message)s"
    )
    formatter_string = (
        "%(asctime)s - %(levelname)-6s - %(name)s - %(levelname)3s - %(message)s"
    )
    if log_level.strip().upper() == log_level:
        formatter_string = debug_formatter
    formatter = logging.Formatter(formatter_string, time_format)
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    __logger__.addHandler(console_handler)
    if str(handler_type).lower() == "rotating_file_handler":
        # Rotating File Handler
        handler = RotatingFileHandler(
            log_file, maxBytes=max_bytes, backupCount=backup_count
        )
        handler.setFormatter(formatter)
        __logger__.addHandler(handler)
    return __logger__


logger = get_logger()
