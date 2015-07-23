__author__ = 'nmg'

from enum import Enum

class User(Enum):
    """
    Identified user type
    """
    normal_user = 0
    custom_service = 1
    sport_man = 2


class NormalUser(object):
    """
    Every connection user map to one User object
    """
    __usertype__ = User.normal_user

    def __init__(self, uid=None, name=None, role=None, session=None):
        self.uid = uid
        self.name = name
        self.role = role
        self.session = session


class CustomService(object):
    """
    Every custom service map to one CustomService object
    """
    __usertype__ = User.custom_service

    def __init__(self, uid=None, name=None):
        self.uid = uid
        self.name = name

    def __eq__(self, other):
        return self.uid == other

    def __hash__(self):
        return id(self)









if __name__ == '__main__':
    cs = CustomService(uid='1234')
    print(cs.__usertype__.value)

    d = { cs : 'test'}

    print(d)

    print(d.get(cs))
    print(cs == '1234')
