__author__ = 'nmg'

import random

class NoValidSessionError(Exception):
    def __init__(self):
        self.msg = "No more session available!"

    def __str__(self):
        return "{}".format(self.msg)

class Random(object):
    """
    Get random session from specfied session list
    """
    @staticmethod
    def get(session_list):
        try:
            return random.choice(session_list)
        except IndexError:
            raise NoValidSessionError()

