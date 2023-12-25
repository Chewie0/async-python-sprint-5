import logging
from logging import config as logging_config
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
LOG_DEFAULT_HANDLERS = ['console', ]

LOG_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': LOG_FORMAT
        },
        'default': {
            '()': 'uvicorn.logging.DefaultFormatter',
            'fmt': '%(levelprefix)s %(message)s',
            'use_colors': None,
        },
        'access': {
            '()': 'uvicorn.logging.AccessFormatter',
            'fmt': "%(levelprefix)s %(client_addr)s - '%(request_line)s' %(status_code)s",
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'default': {
            'formatter': 'default',
            'class': 'logging.StreamHandler',
            'stream': 'ext://sys.stdout',
        },
        'access': {
            'formatter': 'access',
            'class': 'logging.StreamHandler',
            'stream': 'ext://sys.stdout',
        },
    },
    'loggers': {
        '': {
            'handlers': LOG_DEFAULT_HANDLERS,
            'level': 'INFO',
        },
        'uvicorn.error': {
            'level': 'INFO',
        },
        'uvicorn.access': {
            'handlers': ['access'],
            'level': 'INFO',
            'propagate': False,
        },
        'api_logger': {
            'level': 'INFO',
        },
        'tools': {
            'level': 'INFO',
        },
        'test_logger': {
            'level': 'INFO',
        },
        'black_list': {
            'level': 'INFO',
        },
    },
    'root': {
        'level': 'INFO',
        'formatter': 'verbose',
        'handlers': LOG_DEFAULT_HANDLERS,
    },
}

LOG_CONFIG2 = {
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
