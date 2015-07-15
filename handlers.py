__author__ = 'nmg'

__all__ = ['MessageHandler']

_MONGO_HOST = '192.168.99.100'
_MONGO_PORT = 32768
_MONGO_DB = 'hyperline'

import asyncio
import json
from struct import pack

from session import Session
from mongodb import MongoProxy

class MetaHandler(type):
    """Metaclass for MessageHandler"""
    def __init__(cls, name, bases, _dict):
        try:
            cls._msg_handlers[cls.__msgtype__] = cls
        except AttributeError:
            cls._msg_handlers = {}

class MessageHandler(metaclass=MetaHandler):

    _session = Session()
    _mongodb = MongoProxy(host=_MONGO_HOST,
                          port=_MONGO_PORT,
                          db=_MONGO_DB)

    def handle(self, msg, transport):
        try:
            _handler = self._msg_handlers[msg['type']]
        except KeyError:
            return ErrorHandler().handler(msg)

        # Handling messages in a asyncio-Task
        # Don’t directly create Task instances: use the async() function
        # or the BaseEventLoop.create_task() method.

        #return _handler().handle(msg, transport)

        return asyncio.async(_handler().handle(msg, transport))

class Register(MessageHandler):
    """
    Registry handler for handling clients registry.

    Message body should like this:

        {'type': 'register', 'uid': 'unique-user-id'}

    """
    __msgtype__ = 'register'

    def __init__(self):
        self.current_uid = None
        self.transport = None

    @asyncio.coroutine
    def handle(self, msg, transport):

        self.current_uid = msg['uid']
        self.transport = transport

        # Register user in global session
        self._session.register(self.current_uid, self.transport)

        # Get offline msgs from db
        offline_msgs = yield from self.get_offline_msgs()

        # Send offline msgs
        yield from self.send_offline_msgs(offline_msgs)

    @asyncio.coroutine
    def get_offline_msgs(self):
        # Get offline msg from mongodb.
        return self._mongodb.get_msgs(receiver=self.current_uid)

    @asyncio.coroutine
    def send_offline_msgs(self, offline_msgs):
        """
        Send offline msgs to current user
        """
        for msg in offline_msgs:
            del msg['_id']
            msg = json.dumps(msg)
            try:
                self.transport.write(pack("!I", len(msg)) + bytes(msg, encoding='utf-8'))
            except Exception:
                raise

class SendTextMsg(MessageHandler):
    """
    Send message to others.

    Message body should like this:

        {'type': 'text', 'sender': 'Jack', 'receiver': 'Rose', 'content': 'I love you forever'}

    """
    __msgtype__ = 'text'  # Text message

    @asyncio.coroutine
    def handle(self, msg, _):
        """
        Send message to receiver if receiver is online, and
        save message to mongodb. Otherwise save
        message to mongodb as offline message.
        :param msg:
        :return: None
        """
        transport = self._session.get(msg['receiver'])
        if transport:
            # Pack message as length-prifixed and send to receiver.
            transport.write(pack("!I", len(msg)) + msg)

            return asyncio.async(self.save_message(msg))

        return asyncio.async(self.save_message(msg, online=False))

    @asyncio.coroutine
    def save_message(self, msg, online=True):
        """
        Save message to mongodb.

        If online is True, message status is 1(True, online), otherwise
        message status is 0(False, offline).
        """
        status = {'status': int(online)}
        msg.update(status)

        self._mongodb.save_msg('messages', msg)

class Unregister(MessageHandler):
    """
    Unregister user from global session

    Message body should like this:

        {'type': 'unregister', 'uid': 'unique-user-id'}

    """
    __msgtype__ = 'unregister'

    @asyncio.coroutine
    def handle(self, msg, _):
        """Unregister user record from global session"""
        self._session.unregister(msg['uid'])

class ErrorHandler(MessageHandler):
    """
    Unknown message type
    """
    __msgtype__ = 'unknown'

    def handle(self, msg):
        print("Unknown message type: {}".format(msg))

