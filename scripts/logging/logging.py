import logging
import os
from logging import StreamHandler
from logging.handlers import RotatingFileHandler, SocketHandler

import yaml
from scripts.config.app_configurations import Logging


def read_configuration(file_name):
    """
    Reads configuration from a YAML file.

    :param file_name: Path to the configuration file.
    :return: Dictionary containing configuration constants.
    """
    try:
        with open(file_name) as stream:
            return yaml.safe_load(stream)
    except Exception as e:
        print(f"Failed to load configuration. Error: {e}")
        return {}


config = read_configuration("scripts/logging/logger_conf.yml")
logging_config = config.get("logger", {})

# Ensure 'level' and 'handlers' keys are present in configuration
logging_config["level"] = Logging.level if Logging.level else logging.INFO
enable_traceback = Logging.LOG_ENABLE_TRACEBACK


def get_logger():
    """
    Creates and configures a logger with specified handlers.

    :return: Configured logger instance.
    """
    logger = logging.getLogger("")
    logger.setLevel(logging_config["level"].upper())

    log_formatter = "%(asctime)s - %(levelname)-6s - [%(threadName)5s:%(funcName)5s():%(lineno)s] - %(message)s"
    time_format = "%Y-%m-%d %H:%M:%S"
    formatter = logging.Formatter(log_formatter, time_format)

    for handler_config in logging_config.get("handlers", []):
        handler_type = handler_config.get("type")
        if handler_type == "RotatingFileHandler" and Logging.ENABLE_FILE_LOG:
            log_file = os.path.join(
                handler_config["file_path"], logging_config.get("name", "log") + ".log"
            )
            os.makedirs(handler_config["file_path"], exist_ok=True)

            handler = RotatingFileHandler(
                log_file,
                maxBytes=handler_config.get("max_bytes", 10000000),
                backupCount=handler_config.get("back_up_count", 5),
            )
            handler.setFormatter(formatter)
        elif handler_type == "SocketHandler":
            handler = SocketHandler(handler_config["host"], handler_config["port"])
        elif handler_type == "StreamHandler" and Logging.ENABLE_CONSOLE_LOG:
            handler = StreamHandler()
            handler.setFormatter(formatter)
        else:
            continue

        logger.addHandler(handler)

    return logger


logger = get_logger()
