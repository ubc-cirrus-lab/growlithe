import logging.config

logging.config.dictConfig({"version": 1, "disable_existing_loggers": True})
logging.basicConfig(
    format="[%(asctime)s] [%(levelname)s] %(message)s", level=logging.INFO
)
logger = logging.getLogger("main")
