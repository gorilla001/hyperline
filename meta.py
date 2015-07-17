"""
This files contains all meta-class that will be used in this project.
"""
__author__ = 'nmg'

class MetaHandler(type):
    """Metaclass for MessageHandler"""
    def __init__(cls, name, bases, dict):
        try:
            cls._msg_handlers[cls.__msgtype__] = cls
        except AttributeError:
            cls._msg_handlers = {}
