__author__ = 'nmg'

from decorator import singleton
from meta import MetaHandler

__all__ = ['MessageHandler']

import asyncio
import json
import logging

from session import SessionManager
from mongodb import MongoProxy
from messages import Message

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
    _message = Message()

    def handle(self, msg, session):
        try:
            _handler = self._msg_handlers[msg.__msgtype__]
        except KeyError:
            return ErrorHandler().handle(msg)
        except AttributeError:
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

    @asyncio.coroutine
    def handle(self, msg, session):

        """
        Register user in session manager.

        If user role is normal, the session will be added into NormalUserSessionManager,
        if user role is custom service, the session will be added into CustomServiceSessionManager,
        if user role is sports man, the session will be added into SportsManSessionManager.

        """
        session.client = msg.uid
        session.role = msg.role
        # session.service = msg.service

        # Register user in global session
        self._session_manager.add_session(session)

        # Start session timer
        session.add_timeout()

        """
        Choose service man from service session manager, and send back
        service man's name and id to client.
        """
        try:
            custom_service = self._session_manager.get_sessions().pop()
            message = {'type': 'reply', 'body': {'status': 200, 'cs_id': custom_service}}

            # custom_service_session = self._session_manager.get_session(custom_service)
            # session.target, custom_service_session.target = custom_service_session, session
        except IndexError:
            message = {'type': 'reply', 'body': {'status': 404, 'cs_id': ''}}

        yield from session.send(self._message(message))

        # # Get offline msgs from db
        # offline_msgs = yield from self.get_offline_msgs(session)
        #
        # # Send offline msgs
        # yield from self.send_offline_msgs(offline_msgs, session)

    @asyncio.coroutine
    def get_offline_msgs(self, session):
        # Get offline msg from mongodb.
        return self._mongodb.get_msgs(receiver=session.client)

    @asyncio.coroutine
    def send_offline_msgs(self, offline_msgs, session):
        """
        Send offline msgs to current user
        """
        for msg in offline_msgs:
            del msg['_id']
            msg = json.dumps(msg)
            try:
                # Normal Socket use method `write` to send message, while Web Socket use method `send`
                # For Web Socket, just send raw message
                # FIXME
                if hasattr(session.transport, 'write'):
                    # Pack message as length-prifixed and send to receiver.
                    session.write(msg)
                else:
                    # Send raw message directly
                    session.send(msg)
            except Exception:
                raise

class SendTextMsg(MessageHandler):
    """
    Send message to others.

    Message body should like this:

        {'type': 'text', 'sender': 'Jack', 'receiver': 'Rose', 'content': 'I love you forever'}

    """
    __msgtype__ = 'message'  # Text message

    @asyncio.coroutine
    def handle(self, msg, session):
        """
        Send message to receiver if receiver is online, and
        save message to mongodb. Otherwise save
        message to mongodb as offline message.
        :param msg: message to send
        :return: None
        """
        try:
            _session = self._session_manager.get_session(msg.recipient)
        except KeyError:
            logger.error("Message format is not correct: message receiver must be specified")
            return

        if _session:
                # Normal Socket use method `write` to send message, while Web Socket use method `send`
                # For Web Socket, just send raw message
                if hasattr(_session.transport, 'write'):
                    # Pack message as length-prifixed and send to receiver.
                    _session.write(msg)
                else:
                    # Send raw message directly
                    yield from _session.send(msg)

        #         return asyncio.async(self.save_message(msg))
        #
        # return asyncio.async(self.save_message(msg, online=False))

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
    def handle(self, msg, session):
        """Unregister user record from global session"""
        self._session_manager.pop_session(session)

class HeartBeat(MessageHandler):
    """
    Handling heartbeat message from client

    Message body should like this:

        {'type': 'heartbeat', 'uid': 'unique-user-id'}
    """
    __msgtype__ = 'heartbeat'

    @asyncio.coroutine
    def handle(self, msg, _):
        session = self._session_manager.get_session(msg.uid)
        session.touch()

class ErrorHandler(MessageHandler):
    """
    Unknown message type
    """
    __msgtype__ = 'unknown'

    def handle(self, msg):
        print("Unknown message type: {}".format(msg))

