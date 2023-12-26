import logging
from logging import config as logging_config

LOG_CONFIG = {
    "version": 1,
    "root": {
        "handlers": ["console", "file"],
        "level": "INFO"
    },
    "handlers": {
        "console": {
            "formatter": "std_out",
            "class": "logging.StreamHandler",
            "level": "INFO"
        },
        "file": {
            "level": "INFO",
            "class": "logging.FileHandler",
            "filename": "log.log",
            "formatter": "fileformat",
        },
    },
    "formatters": {
        "std_out": {
            "format": "%(asctime)s : %(levelname)s  %(module)s : %(lineno)d - %(message)s",
            "datefmt": "%d-%m-%Y %I:%M:%S"

        },
        "fileformat": {
            "format": "%(asctime)s : %(levelname)s  %(module)s  %(funcName)s : %(lineno)d - %(message)s",
            "datefmt": "%d-%m-%Y %I:%M:%S"
        }
    },
}

logging_config.dictConfig(LOG_CONFIG)
logger = logging.getLogger()
