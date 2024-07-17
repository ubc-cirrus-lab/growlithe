import logging.config
import colorlog
from common.app_config import *
from common.file_utils import create_dir_if_not_exists
from common.tasks_config import CONSOLE_LOG_LEVEL, FILE_LOG_LEVEL

create_dir_if_not_exists(growlithe_path)

logging.config.dictConfig({
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
        }
    },
    "handlers": {
        "console_handler": {
            "class": "logging.StreamHandler",
            "formatter": "console_formatter",
            "level": CONSOLE_LOG_LEVEL
        },
        "file_handler": {
            "class": "logging.FileHandler",
            "formatter": "file_formatter",
            "filename": profiler_log_path,
            "level": FILE_LOG_LEVEL
        }
    },
    "loggers": {
        "main": {
            "handlers": ["console_handler"],
            "level": CONSOLE_LOG_LEVEL
        },
        "profiler": {
            "handlers": ["file_handler"],
            "level": FILE_LOG_LEVEL
        }
    }
})

# Get the loggers
logger = logging.getLogger("main")
profiler_logger = logging.getLogger("profiler")