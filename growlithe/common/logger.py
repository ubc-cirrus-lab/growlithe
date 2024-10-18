"""
Logging configuration module for Growlithe.

This module sets up logging for the Growlithe application, configuring both console
and file logging with different formatters and log levels.
"""

import logging.config
from growlithe.common.dev_config import CONSOLE_LOG_LEVEL, FILE_LOG_LEVEL


def init_logger(profiler_log_path):
    """
    Initialize the logging configuration for Growlithe.

    This function sets up two loggers:
    1. A console logger with colored output for general application logging.
    2. A file logger for profiling information.

    Args:
        profiler_log_path (str): The file path where profiler logs will be written.

    The function uses dictConfig to set up logging with the following features:
    - Console logging with colored output and customizable log level.
    - File logging for profiler data with a separate log level.
    - Different formatters for console and file logging.
    - Two separate loggers: 'main' for console output and 'profiler' for file output.
    """
    logging.config.dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "console_formatter": {
                    "()": "colorlog.ColoredFormatter",
                    "format": "%(log_color)s[%(asctime)s] [%(levelname)s] %(message)s",
                    "log_colors": {
                        "DEBUG": "cyan",
                        "INFO": "green",
                        "WARNING": "yellow",
                        "ERROR": "red",
                        "CRITICAL": "red,bg_white",
                    },
                },
                "file_formatter": {
                    "format": "[%(asctime)s] [%(levelname)s] %(message)s"
                },
            },
            "handlers": {
                "console_handler": {
                    "class": "logging.StreamHandler",
                    "formatter": "console_formatter",
                    "level": CONSOLE_LOG_LEVEL,
                },
                "file_handler": {
                    "class": "logging.FileHandler",
                    "formatter": "file_formatter",
                    "filename": profiler_log_path,
                    "level": FILE_LOG_LEVEL,
                },
            },
            "loggers": {
                "main": {"handlers": ["console_handler"], "level": CONSOLE_LOG_LEVEL},
                "profiler": {"handlers": ["file_handler"], "level": FILE_LOG_LEVEL},
            },
        }
    )


# Get the loggers
logger = logging.getLogger("main")
profiler_logger = logging.getLogger("profiler")
