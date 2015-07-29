__author__ = 'nmg'

from enum import Enum
import json

class UserType(Enum):
    """
    Identified user type
    """
    normal_user = 0
    custom_service = 10
    sport_man = 2


class User(object):
    """
    Every connection user map to one User object
    """
    def __init__(self, uid=None, name=None, role=None):
        self._uid = uid
        self._name = name
        self._role = role


class CustomService(object):
    """
    Every custom service map to one CustomService object
    """
    __usertype__ = UserType.custom_service

    def __init__(self, uid=None, name=None):
        self.uid = uid
        self.name = name

    def __eq__(self, other):
        return self.uid == other

    def __hash__(self):
        return id(self)

if __name__ == '__main__':
    user = User()
    print(json.loads(user))
