import logging.config
from common.app_config import *
from common.file_utils import create_dir_if_not_exists

create_dir_if_not_exists(growlithe_path)

logging.config.dictConfig({
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "console_formatter": {
            "format": "[%(asctime)s] [%(levelname)s] %(message)s"
        },
        "file_formatter": {
            "format": "[%(asctime)s] [%(levelname)s] %(message)s"
        }
    },
    "handlers": {
        "console_handler": {
            "class": "logging.StreamHandler",
            "formatter": "console_formatter",
            "level": "INFO"
        },
        "file_handler": {
            "class": "logging.FileHandler",
            "formatter": "file_formatter",
            "filename": profiler_log_path,
            "level": "INFO"
        }
    },
    "loggers": {
        "main": {
            "handlers": ["console_handler"],
            "level": "INFO"
        },
        "profiler": {
            "handlers": ["file_handler"],
            "level": "INFO"
        }
    }
})

# Get the loggers
logger = logging.getLogger("main")
profiler_logger = logging.getLogger("profiler")
