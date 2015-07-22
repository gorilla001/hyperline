"""
This files contains all meta-class that will be used in this project.
"""
__author__ = 'nmg'

class MetaHandler(type):
    """Metaclass for MessageHandler"""
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(MetaHandler, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

    def __init__(cls, *_):
        try:
            cls._msg_handlers[cls.__msgtype__] = cls
        except AttributeError:
            cls._msg_handlers = {}


class MetaSession(type):
    """Metaclass for SessionManager"""
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(MetaSession, cls).__call__(*args, **kwargs)
        return cls._instances[cls]
