__author__ = 'nmg'

from meta import MetaHandler

__all__ = ['MessageHandler']

import asyncio
import json
import logging

# from session import SessionManager
from managers import NormalUserConnectionManager, CustomServiceConnectionManager
from mongodb import MongoProxy, RedisProxy
from messages import MessageType, RegisterSucceed, RegisterFailed, ReadyMessage, RequestForServiceResponse, UserMessage


logger = logging.getLogger(__name__)

class MessageHandler(metaclass=MetaHandler):

    """
    Variables `_session` and `_mongodb` are all class variable. This ensure
    that only one copy between instances that were instantiated from `MessageHandler`
    for many times. These variables are shared between these instances.

    The points is that the class variables are shared between instances. so don't worried
    for different session and mongodb.
    """
    # _session_manager = SessionManager()
    _mongodb = MongoProxy()
    _redis = RedisProxy()

    def handle(self, msg, connection):
        try:
            _handler = self._msg_handlers[msg.__msgtype__.value]
        except KeyError as exc:
            return ErrorHandler().handle(exc)
        except AttributeError as exc:
            return ErrorHandler().handle(exc)

        # Handling messages in a asyncio-Task
        # Don’t directly create Task instances: use the async() function
        # or the BaseEventLoop.create_task() method.

        return asyncio.async(_handler().handle(msg, connection))

class Register(MessageHandler):
    """
    Registry handler for handling clients registry.

    Message body should like this:

        {'type': 'register', 'uid': 'unique-user-id'}

    """
    __msgtype__ = MessageType.REGISTER

    @asyncio.coroutine
    def handle(self, msg, connection):

        """
        Register user in session manager.

        If user role is normal, the session will be added into NormalUserSessionManager,
        if user role is custom service, the session will be added into CustomServiceSessionManager,
        if user role is sports man, the session will be added into SportsManSessionManager.

        """
        connection.uid = msg.uid
        connection.name = msg.name

        if connection.path == '/service':
            _connection_manager = CustomServiceConnectionManager()
        else:
            _connection_manager = NormalUserConnectionManager()

        try:
            yield from self.register(_connection_manager, connection)
            yield from self.register_succeed(connection)
        except KeyError as exc:
            yield from self.register_failed(connection, exc)

        yield from self.send_associated_users(connection)

        # # Get offline msgs from db
        # offline_msgs = yield from self.get_offline_msgs(session)
        #
        # # Send offline msgs
        # yield from self.send_offline_msgs(offline_msgs, session)

    @asyncio.coroutine
    def register(self, connection_manager, connection):
        # Register user in connection manager
        try:
            connection_manager.add_connection(connection)
            # Start connection timer
            connection.add_timeout()
        except KeyError:
            raise

    @asyncio.coroutine
    def register_succeed(self, connection):
        # Send successful reply
        yield from connection.send(RegisterSucceed())

    @asyncio.coroutine
    def register_failed(self, connection, exc):
        # Send successful failed
        yield from connection.send(RegisterFailed(reason=str(exc)))

    @asyncio.coroutine
    def send_associated_users(self, connection):
        # Get associated users of current user from redis
        message = UserMessage()
        users = self._redis.get(connection.uid)
        if users is not None:
            for user in eval(users):
                message.append(user[0], user[1])

        yield from connection.send(message)

    @asyncio.coroutine
    def get_offline_msgs(self, connection):
        # Get offline msg from mongodb.
        return self._mongodb.get_msgs(receiver=connection.uid)

    @asyncio.coroutine
    def send_offline_msgs(self, offline_msgs, connection):
        """
        Send offline msgs to current user
        """
        for msg in offline_msgs:
            del msg['_id']
            msg = json.dumps(msg)
            try:
                # Normal Socket use method `write` to send message, while Web Socket use method `send`
                # For Web Socket, just send raw message
                # FIXME: try to determine connection type by connection attribute
                if hasattr(connection.transport, 'write'):
                    # Pack message as length-prifixed and send to receiver.
                    connection.write(msg)
                else:
                    # Send raw message directly
                    connection.send(msg)
            except Exception:
                raise

class SendTextMsg(MessageHandler):
    """
    Send message to others.

    Message body should like this:

        {'type': 'text', 'sender': 'Jack', 'receiver': 'Rose', 'content': 'I love you forever'}

    """
    __msgtype__ = MessageType.MESSAGE

    @asyncio.coroutine
    def handle(self, msg, connection):
        """
        Send message to receiver if receiver is online, and
        save message to mongodb. Otherwise save
        message to mongodb as offline message.
        :param msg: message to send
        :return: None
        """
        current_connection = connection
        _session = current_connection.associated_sessions.get(int(msg.recv), None)
        if _session is not None:
            if _session.is_websocket:
                # Send raw message directly
                yield from _session.send(msg)
            else:
                # Pack message as length-prifixed and send to receiver.
                _session.write(msg)

        # try:
        #     _session = self._session_manager.get_session(msg.recv)
        # except KeyError:
        #     logger.error("Message format is not correct: message receiver must be specified")
        #     return
        #
        # if _session:
        #         # Normal Socket use method `write` to send message, while Web Socket use method `send`
        #         # For Web Socket, just send raw message
        #         if hasattr(_session.transport, 'write'):
        #             # Pack message as length-prifixed and send to receiver.
        #             _session.write(msg)
        #         else:
        #             # Send raw message directly
        #             yield from _session.send(msg)

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
    __msgtype__ = MessageType.UNREGISTER

    @asyncio.coroutine
    def handle(self, msg, connection):
        """Unregister user record from global session"""
        if connection.path == '/service':
            _connection_manager = CustomServiceConnectionManager()
        else:
            _connection_manager = NormalUserConnectionManager()

        _connection_manager.pop_connection(connection.uid)

class HeartBeat(MessageHandler):
    """
    Handling heartbeat message from client

    Message body should like this:

        {'type': 'heartbeat', 'uid': 'unique-user-id'}
    """
    __msgtype__ = MessageType.HEARTBEAT

    @asyncio.coroutine
    def handle(self, msg, _):
        session = self._session_manager.get_session(msg.uid)
        session.touch()

class RequestForService(MessageHandler):

    __msgtype__ = MessageType.REQUEST_SERVICE

    @asyncio.coroutine
    def handle(self, msg, connection):
        try:
            current_connection = connection
            custom_service = CustomServiceConnectionManager().get_connections().pop()
            # message = {'type': 'reply', 'body': {'status': 200, 'content': custom_service}}
            ready_message = ReadyMessage()
            ready_message.uid = current_connection.uid
            ready_message.name = current_connection.name

            # Send ready message to custom service
            yield from custom_service.send(ready_message)

            # Send ready message to current user
            response_message = RequestForServiceResponse()
            response_message.status = 200
            response_message.uid = custom_service.uid
            response_message.name = custom_service.name

            yield from current_connection.send(response_message)

            # Session bind
            custom_service.associated_sessions[current_connection.uid] = current_connection
            current_connection.associated_sessions[custom_service.uid] = custom_service

            # Store relationship in redis
            users = self._redis.get(current_connection.uid)
            users = eval(users) if users is not None else []
            users.append((custom_service.uid, custom_service.name))
            self._redis.set(current_connection.uid, users)

            users = self._redis.get(custom_service.uid)
            users = eval(users) if users is not None else []
            users.append((current_connection.uid, current_connection.name))
            self._redis.set(custom_service.uid, users)

        except IndexError:
            response_message = RequestForServiceResponse()
            response_message.status = 404

            # Send error message to current user
            yield from current_connection.send(response_message)


class ErrorHandler(MessageHandler):
    """
    Unknown message type
    """
    __msgtype__ = MessageType.UNKNOWN

    def handle(self, msg):
        logger.info("Unknown message type: {}".format(msg))

