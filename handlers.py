__author__ = 'nmg'

from decorator import singleton
from meta import MetaHandler

__all__ = ['MessageHandler']

import asyncio
import json
from struct import pack
import logging

from session import Session
from session import SessionManager
from mongodb import MongoProxy

logger = logging.getLogger(__name__)

class MessageHandler(metaclass=MetaHandler):

    """
    Variables `_session` and `_mongodb` are all class variable. This ensure
    that only one copy between instances that were instantiated from `MessageHandler`
    for many times. These variables are shared between these instances.

    The points is that the class variables are shared between instances. so don't worried
    for different session and mongodb.
    """
    _session_manager = SessionManager()
    _mongodb = MongoProxy()

    def handle(self, msg, session):
        try:
            _handler = self._msg_handlers[msg['type']]
        except KeyError:
            return ErrorHandler().handle(msg)

        # Handling messages in a asyncio-Task
        # Don’t directly create Task instances: use the async() function
        # or the BaseEventLoop.create_task() method.

        return asyncio.async(_handler().handle(msg, session))

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
    def handle(self, msg, session):

        try:
            self.current_uid = msg['uid']
        except KeyError:
            logger.error("Message format is not correct: message uid must be specified")
            return

        session.client = self.current_uid
        self.transport = session.transport

        # Register user in global session
        self._session_manager.add_session(self.current_uid, session)

        # Start session timer

        self._session_manager.add_timeout(self.current_uid)

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
                # Normal Socket use method `write` to send message, while Web Socket use method `send`
                # For Web Socket, just send raw message
                if hasattr(self.transport, 'write'):
                    # Pack message as length-prifixed and send to receiver.
                    self.transport.write(pack("!I", len(msg)) + bytes(msg, encoding='utf-8'))
                else:
                    # Send raw message directly
                    self.transport.send(msg)
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
        :param msg: message to send
        :return: None
        """
        try:
            session = self._session_manager.get_session(msg['receiver'])
        except KeyError:
            logger.error("Message format is not correct: message receiver must be specified")
            return

        if session:
                # Normal Socket use method `write` to send message, while Web Socket use method `send`
                # For Web Socket, just send raw message
                if hasattr(session.transport, 'write'):
                    # Pack message as length-prifixed and send to receiver.
                    session.transport.write(pack("!I", len(msg)) + bytes(msg, encoding='utf-8'))
                else:
                    # Send raw message directly
                    yield from session.transport.send(json.dumps(msg))

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

        self._mongodb.save_msg(msg)

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
        self._session_manager.pop_session(msg['uid'])

class HeartBeat(MessageHandler):
    """
    Handling heartbeat message from client

    Message body should like this:

        {'type': 'heartbeat', 'uid': 'unique-user-id'}
    """
    __msgtype__ = 'heartbeat'

    @asyncio.coroutine
    def handle(self, msg, _):
        self._session_manager.touch(msg['uid'])

class ErrorHandler(MessageHandler):
    """
    Unknown message type
    """
    __msgtype__ = 'unknown'

    def handle(self, msg):
        logger.info("Unknown message type: {}".format(msg))

