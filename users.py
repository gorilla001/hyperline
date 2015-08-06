__author__ = 'nmg'

from enum import Enum
import json
import pickle

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
    def __init__(self, uid=None, name=None, role=None, head_img=None):
        self._uid = uid
        self._name = name
        self._role = role
        self._head_img = head_img
        self._server = None

    def serialize(self):
        return pickle.dumps(self)

    def deserialize(self):
        return pickle.loads(self)

    @property
    def uid(self):
        return self._uid

    @property
    def name(self):
        return self._name

    @property
    def role(self):
        return self._role

    @property
    def head_img(self):
        return self._head_img


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
