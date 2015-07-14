__author__ = 'nmg'

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

    def __call__(self, msg):
        try:
            _handler = self._msg_handlers[msg['type']]
            return _handler().handler(msg)
        except KeyError:
            return ErrorHandler().handler(msg)

class Register(MessageHandler):
    """
    Registry handler for handling clients registry.

    message body should like this:

        {'type': 'register', 'uid': 'unique-user-id'}

    """
    __msgtype__ = 'register'

    def __init__(self):
        self.current_uid = None
        self.transport = None

    def handler(self, msg):

        self.current_uid = msg['uid']
        self.transport = msg['transport']

        # Register user in global session
        self._session.register(self.current_uid, self.transport)

        # Get offline msgs from db
        offline_msgs = self.get_offline_msg(msg)

        # Send offline msgs
        self.send_offline_msgs(offline_msgs)

    @asyncio.coroutine
    def get_offline_msg(self, msg):

        # Get offline msg from mongodb. This will be block
        result = yield from self.get_offline_msg_from_db(msg['sender'])

        return result

    def send_offline_msgs(self, msgs):
        """
        Send offline msgs to current user
        """
        if self.transport:
            for msg in msgs:
                self.transport.write(pack("!I", len(msg)) + msg)

    @staticmethod
    def get_offline_msg_from_db(user):
        # Get offline msg from mongodb. This must return a `Future`.
        return Future()

class SendTextMsg(MessageHandler):
    """
    Send message to others.
    """
    __msgtype__ = 'text'  # Text message

    def handler(self, msg):
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
    """Unregister user from global session"""
    __msgtype__ = 'unregister'

    def handler(self, msg):
        """Unregister user record from global session"""
        del self.session[msg['sender']]

class ErrorHandler(MessageHandler):
    """
    Unknown message type
    """
    __msgtype__ = 'unknown'

    def handler(self, msg):
        print("Unknown message type: {}".format(msg))


handler = MessageHandler()
