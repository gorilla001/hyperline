__author__ = 'nmg'

__all__ = ['MessageHandler']

import asyncio

from struct import pack
from asyncio import Future

from session import Session

class MetaHandler(type):
    """Metaclass for MessageHandler"""
    def __init__(cls, name, bases, _dict):
        try:
            cls._msg_handlers[cls.__msgtype__] = cls
        except AttributeError:
            cls._msg_handlers = {}

class MessageHandler(metaclass=MetaHandler):

    _session = Session()

    def handle(self, msg, transport):
        try:
            _handler = self._msg_handlers[msg['type']]
        except KeyError:
            return ErrorHandler().handler(msg)

        return _handler().handler(msg, transport)

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

    def handler(self, msg, transport):

        self.current_uid = msg['uid']
        self.transport = transport

        # Register user in global session
        self._session.register(self.current_uid, self.transport)

        # Get offline msgs from db
        offline_msgs = self.get_offline_msg(msg)

        # Send offline msgs
        self.send_offline_msgs(offline_msgs)

    @asyncio.coroutine
    def get_offline_msg(self, msg):

        # Get offline msg from mongodb. This will be block
        result = yield from self.get_offline_msg_from_db(self.current_uid)

        return result

    def send_offline_msgs(self, msgs):
        """
        Send offline msgs to current user
        """
        for msg in msgs:
            msg = msg.decode("utf-8")
            self.transport.write(pack("!I", len(msg)) + msg)

    @asyncio.coroutine
    def get_offline_msg_from_db(self, uid):
        # Get offline msg from mongodb. This must return a `Future`.
        return [{'type': 'text',
                 'sender': 'niuminguo',
                 'receiver': 'niuminguo',
                 'content': 'hello'
                }]

class SendTextMsg(MessageHandler):
    """
    Send message to others.

    Message body should like this:

        {'type': 'text', 'sender': 'Jack', 'receiver': 'Rose', 'content': 'I love you forever'}

    """
    __msgtype__ = 'text'  # Text message

    def handler(self, msg, _):
        """
        Send message to receiver if receiver is online, and
        save message to mongodb. Otherwise save
        message to mongodb as offline message.
        :param msg:
        :return: None
        """
        transport = self._session.get(msg['receiver'], None)
        if transport:
            # Pack message as length-prifixed and send to receiver.
            transport.write(pack("!I", len(msg)) + msg)
            return self.save_message(msg)

        return self.save_message(msg, online=False)

    def save_message(self, online=True):
        pass

class Unregister(MessageHandler):
    """
    Unregister user from global session

    Message body should like this:

        {'type': 'unregister', 'uid': 'unique-user-id'}

    """
    __msgtype__ = 'unregister'

    def handler(self, msg, transport):
        """Unregister user record from global session"""
        self._session.unregister(msg['uid'])

class ErrorHandler(MessageHandler):
    """
    Unknown message type
    """
    __msgtype__ = 'unknown'

    def handler(self, msg):
        print("Unknown message type: {}".format(msg))


handler = MessageHandler()
