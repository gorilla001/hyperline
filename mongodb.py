__author__ = 'nmg'


__all__ = ['MongoProxy']

from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
import log as logging
import sys
import redis
import asyncio


logger = logging.getLogger(__name__)

class MongoProxy(object):
    def __init__(self, host, port, db):
        self.host = host
        self.port = port
        self.db = db
        self.connection = None
        self.max_retries = 5
        self.retry_interval = 5

        asyncio.async(self.connect())

    @asyncio.coroutine
    def connect(self):
        attempt = 0
        while True:
            attempt += 1
            try:
                yield from self._connect()
                logger.info("Connecting to MongoDB server on {}:{} succeed".format(self.host, self.port))
                return
            except ConnectionFailure:
                logger.error("Connecting to MongoDB failed...retry after {} seconds".format(self.retry_interval))

            if attempt >= self.max_retries:
                logger.error("Connecting to MongoDB server on {}:{} falied".format(self.host, self.port))
                sys.exit(1)
            yield from asyncio.sleep(self.retry_interval)
            # time.sleep(self.retry_interval)

    @asyncio.coroutine
    def _connect(self):
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

    def get_msgs(self, invent='messages', recv=None, status=0):
        """
        Get messages from collection.

        @param invent: the collection
        @param recv: message receiver
        @param status: message status, 0-offline, 1-online

        @return: `pymongo.cursor.Cursor object`
        """

        coll = self.connection[self.db][invent]
        if not recv:
            return coll.find({'status': 0})

        return coll.find({"$and": [{'recv': recv}, {'status': status}]})

    def get_msgs_by_count(self, recv, offset=0, count=0, invent='messages'):
        """
        Get messages by offset and messages count.
        @param offset: control where MongoDB begins returning results
        @param count: specify the maximum number of documents the cursor will return
        @param invent: the collection
        @param recv: message receiver
        @return: history messages
        """
        coll = self.connection[self.db][invent]
        return coll.find({'body.recv': recv}).sort([('body.timestamp', 1)]).skip(offset).limit(count)

    def total_message(self, recv, invent='messages'):
        """
        Get messages total count
        """
        coll = self.connection[self.db][invent]
        return coll.find({'body.recv': recv}).count()


class RedisProxy(object):
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.connection = None
        self.max_retries = 5
        self.retry_interval = 5

        asyncio.async(self.connect())

    @asyncio.coroutine
    def connect(self):
        attempt = 0
        while True:
            attempt += 1
            try:
                yield from self._connect()
                logger.info("Connecting to Redis server on {}:{} succeed".format(self.host, self.port))
                return
            except ConnectionFailure:
                logger.error("Connecting to Redis failed...retry after {} seconds".format(self.retry_interval))

            if attempt >= self.max_retries:
                logger.error("Connecting to Redis server on {}:{} falied".format(self.host, self.port))
                sys.exit(1)
            yield from asyncio.sleep(self.retry_interval)

    @asyncio.coroutine
    def _connect(self):
        self.connection = redis.StrictRedis(host=self.host, port=self.port, db=0)

    def set(self, key, value):
        self.connection.set(key, value)

    def get(self, key):
        return self.connection.get(key)

if __name__ == '__main__':
    import constant as cfg
    _proxy = MongoClient(cfg.mongo_host, cfg.mongo_port)
    _coll = _proxy['hyperline']['messages']
    _coll.remove()
    # result = _coll.find({'body.recv': 100})
    # for res in result:
    #     print(res)
    # print(result)

