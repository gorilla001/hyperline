__author__ = 'nmg'

import sys
import logging

_DEFAULT_LOG_FORMAT = "%(asctime)s %(levelname)2s [%(name)s] %(message)s"
_DEFAULT_LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

LOG_FILE = None

DEBUG = True

_loggers = {}

def setup():
    _setup_logging_from_conf()

def _setup_logging_from_conf():
    log_root = getLogger()
    if LOG_FILE is not None:
        handler = logging.FileHandler(LOG_FILE)
    else:
        handler = logging.StreamHandler(sys.stdout)
    log_root.addHandler(handler)

    fmt = _DEFAULT_LOG_FORMAT
    datefmt = _DEFAULT_LOG_DATE_FORMAT
    handler.setFormatter(logging.Formatter(fmt=fmt,
                                           datefmt=datefmt))

    if DEBUG:
        log_root.setLevel(logging.DEBUG)
    else:
        log_root.setLevel(logging.INFO)

def getLogger(name=None):
    if name not in _loggers:
        _loggers[name] = logging.getLogger(name)
    return _loggers[name]
