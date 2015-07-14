__author__ = 'nmg'

import json
from decorator import singleton
import redis
import pickle
# # Global uid-connection pairs for store client  and its associated connection
# sessions = {}
# @singleton

class Session(object):

    # _instance = None
    #
    # def __new__(cls, *args, **kwargs):
    #     if cls._instance is None:
    #         cls._instance = object.__new__(cls, *args, **kwargs)
    #
    #     return cls._instance

    def __init__(self):
        # self.redis = redis.StrictRedis(host='192.168.99.100', port=32768, db=0)
        # #self.sessions = Manager().dict()
        # try:
        #     self.clients = self.clients.deepcopy()
        # except AttributeError:
        #     self.clients = {}
        self.clients = {}

    # def __setitem__(self, client, transport):
    #     # Add client-transport pairs
    #     if client not in self.clients:
    #         self.clients[client] = transport
    #
    # def __getitem__(self, client):
    #     # Get transport associated by client if exists.
    #     if client not in self.clients:
    #         return None
    #     return self.clients[client]
    #
    # def __delitem__(self, client):
    #     # Delete client-transport pairs
    #     if client in self.clients:
    #         del self.clients[client]
    #
    def __contains__(self, client):
        # Decide if client is online
        return client in self.clients

    def __repr__(self):
        return "{}".format(self.clients)
    __str__ = __repr__

    def register(self, client, transport):
        # Register client on session
        self.clients[client] = transport
        # try:
        #     connection = pickle.dumps(connection)
        # except:
        #     raise

        #self.redis.set(client, connection)


if __name__ == '__main__':
    Session()
