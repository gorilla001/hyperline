__author__ = 'nmg'


__all__ = ['MongoProxy']

from pymongo import MongoClient

_MONGO_HOST = '192.168.99.100'
_MONGO_PORT = 32771
_MONGO_DB = 'hyperline'

class MongoProxy(object):
    def __init__(self):
        self.host = _MONGO_HOST
        self.port = _MONGO_PORT
        self.db = _MONGO_DB
        self.connection = None

        self.connect()

    def connect(self):
        self.connection = MongoClient(self.host, self.port)

    def save_msg(self, msg, coll='messages'):
        """
        Insert message in collection.

        @param coll: the collection, default to `messages`
        @param msg: the message be saved

        @return: a WriteResult object that contains the status of the operation(not used currently)
        """
        coll = self.connection[self.db][coll]

        return coll.insert(msg)

    def get_msgs(self, invent='messages', receiver=None, status=0):
        """
        Get messages from collection.

        @param invent: the collection
        @param receiver: message receiver
        @param status: message status, 0-offline, 1-online

        @return: `pymongo.cursor.Cursor object`
        """

        coll = self.connection[self.db][invent]
        if not receiver:
            return coll.find({'status': 0})

        return coll.find({"$and": [{'receiver': receiver}, {'status': status}]})
