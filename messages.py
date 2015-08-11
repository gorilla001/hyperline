__author__ = 'nmg'

from meta import MetaMessage
import time
from enum import Enum
import log as logging
import traceback
from validators import validate_int, validate_str, ValidatedError

__all__ = ['MessageType',
           'MessageFormatError',
           'RegisterMessage',
           'RegisterSucceed',
           'RegisterFailed',
           'RequestForService',
           'RequestForServiceResponse',
           'ReadyMessage',
           'HistoryMessage']

logger = logging.getLogger(__name__)

class MessageType(Enum):
    """
    Message type
    """
    LOGIN = 'login'
    LOGIN_ACK = 'login_ack'
    CUSTOM_SERVICE = 'custom_service'
    CUSTOM_SERVICE_ACK = 'custom_service_ack'
    CUSTOM_SERVICE_READY = 'custom_service_ready'
    HISTORY_MESSAGE = 'history'
    HISTORY_MESSAGE_ACK = 'history_ack'
    TEXT_MESSAGE = 'txt'
    TEXT_MESSAGE_ACK = 'txt_ack'
    SESSION_LIST = 'session_list'
    SESSION_LIST_ACK = 'session_list_ack'
    HEARTBEAT = 'heartbeat'
    HEARTBEAT_ACK = 'heartbeat_ack'
    LOGOUT = 'logout'
    # UNREGISTER = '2'
    # READY = '3'
    # REPLY = '4'
    # HEARTBEAT = '5'
    #
    # REGISTER_RESPONSE = '11'
    # REQUEST_SERVICE = '12'
    # REQUEST_SERVICE_RESPONSE = '13'
    # ASSOCIATED_USERS = '14'
    # HISTORY_MESSAGE = '15'

    UNKNOWN = '404'

class MessageFormatError(Exception):
    """raise when message format is incorrect"""

class Message(metaclass=MetaMessage):
    """
    Base class for message class
    """
    def __call__(self, msg):

        try:
            return self._msg_factories[msg['type']].factory(msg)
        except (TypeError, KeyError):
            traceback.print_exc()
            raise MessageFormatError()

class LoginMessage(Message):
    """
    Used for user login

    Message Format:

    {'type':'login', 'body': {'uid': '1234', 'name': 'name'}}

    @ type: message type
    @ uid: user ID
    @name: user name

    """

    __msgtype__ = MessageType.LOGIN

    def __init__(self, uid, name):
        self.uid = uid
        self.name = name

    @classmethod
    def factory(cls, msg):
        msg = msg['body']
        try:
            uid = msg['uid']
            name = msg['name']
        except KeyError:
            raise MessageFormatError("Malformed msg {}".format(msg))

        if not validate_int()(uid):
            raise ValidatedError('uid must be integer')

        if not validate_str()(name):
            raise ValidatedError("name must be string")

        return cls(uid, name)

    @property
    def json(self):
        return {'type': self.__msgtype__, 'uid': self.uid, 'name': self.name}

# Internal message
class LoginSucceed(object):
    """
    Used for indicated user login succeed

    Message Format:

    {'type': 'login_ack', body: {'status': 200}}

    @type: message type
    @status: login status

    """
    __msgtype__ = MessageType.LOGIN_ACK

    def __init__(self, status=200):
        self.status = status

    @property
    def json(self):
        return {'type': self.__msgtype__.value, 'body': {'status': self.status}}

# Internal message
class LoginFailed(object):
    """
    Used for reply while login failed.

    Message Format:

    {'type': 'login_ack', 'body': {'status': 500, 'reason': ''}}

    @type: message type
    @status: login status
    @reason: the reason for login failed

    """
    __msgtype__ = MessageType.LOGIN_ACK

    def __init__(self, status=500, reason=''):
        self.status = status
        self.reason = reason

    @property
    def json(self):
        return {'type': self.__msgtype__.value, 'body': {'status': 500, 'reason': self.reason}}


class CustomService(Message):
    """
    Ask for specified service, such as custom service or sports man service.

    Message Format:

    {'type': 'custom_service'}

    @type: message type
    """
    __msgtype__ = MessageType.CUSTOM_SERVICE

    @classmethod
    def factory(cls, _):
        return cls()

    @property
    def json(self):
        return {'type': self.__msgtype__.value}

class CustomServiceAck(object):
    """
    Used for custom service reply for client

    Message Format:

    {'type': 'custom_service_ack', body: {'status': 200, 'uid': self.uid, 'name': self.name}}

    @type: message type
    @status: indicated if has found a custom service, 200 means found, 404 means not found.
    @uid: custom service's ID, if not found, value will be null.
    @name: custom service's Name, if not found, value will be null.

    """
    __msgtype__ = MessageType.CUSTOM_SERVICE_ACK

    def __init__(self, status=None, uid=None, name=None):
        self.status = status
        self.uid = uid
        self.name = name

    @property
    def json(self):
        return {'type': self.__msgtype__.value, 'body': {'status': self.status, 'uid': self.uid, 'name': self.name}}

# Internal message
class CustomServiceReady(object):
    """
    Used for telling custom service for reading to start conversation.

    Message format:

    {'type': 'custom_service_ready', 'body': {'uid': 1234, 'name': 'jack'}}

    @type: message type
    @uid: client user ID
    @name: client user Name
    """
    __msgtype__ = MessageType.CUSTOM_SERVICE_READY

    def __init__(self, uid=None, name=None):
        self.uid = uid
        self.name = name

    @property
    def json(self):
        return {'type': self.__msgtype__.value, 'body': {'uid': self.uid, 'name': self.name}}

class HistoryMessage(Message):
    """
    Get user history message

    Message Format:

    {'type': 'history', 'body': {'sndr': 200, 'recv': 100, 'offset': 0, 'count': 10}}

    @type: message type
    @sndr: the current user's id
    @recv: receiver user's id
    @offset: indicated where to get messages
    @count: how many messages will be retrieved
    """
    __msgtype__ = MessageType.HISTORY_MESSAGE

    def __init__(self, sndr, recv, offset, count):
        self.sndr = sndr
        self.recv = recv
        self.offset = offset
        self.count = count

    @classmethod
    def factory(cls, msg):
        msg = msg['body']
        try:
            sndr = msg['sndr']
            recv = msg['recv']
            offset = msg['offset']
            count = msg['count']
        except KeyError:
            traceback.print_exc()
            raise MessageFormatError()

        return cls(sndr, recv, offset, count)

# Internal message
class HistoryMessageAck(object):
    """
    History messages

    Message Format:

    {'type':'history_ack', 'body': {'msgs': [...], 'total': 9999}}

    @type: message type
    @msgs: messages as dictionary
    @total: total message count
    """
    __msgtype__ = MessageType.HISTORY_MESSAGE_ACK

    def __init__(self):
        self.messages = []
        self._total = 0

    def append(self, msg):
        if msg not in self.messages:
            self.messages.append(msg)

    @property
    def total(self):
        return self._total

    @total.setter
    def total(self, val):
        self._total = val

    @property
    def json(self):
        return {'type': self.__msgtype__.value, 'body': {'msgs': self.messages, 'total': self._total}}

class SessionList(Message):
    """
    Get current session list

    Message Format:

    {'type': 'session_list', 'body': {'uid': 100}}

    @type: message type
    @uid: user id
    """
    __msgtype__ = MessageType.SESSION_LIST

    def __init__(self, uid):
        self.uid = uid

    @classmethod
    def factory(cls, msg):
        msg = msg['body']
        try:
            uid = msg['uid']
        except KeyError:
            raise MessageFormatError('uid is not specified')

        if not validate_int()(uid):
            raise ValidatedError('uid must be integer')

        return cls(uid)

    @property
    def json(self):
        return {'type': self.__msgtype__.value, 'body': {'uid': self.uid}}

# internal message
class SessionListAck(object):
    """
     Used for return current session list
    """

    __msgtype__ = MessageType.SESSION_LIST_ACK

    def __init__(self):
        self.users = []

    def append(self, uid, name):
        user = {'uid': uid, 'name': name}
        if user not in self.users:
            self.users.append(user)

    @property
    def json(self):
        return {'type': self.__msgtype__.value, 'body': self.users}

class TextMessage(Message):
    """
    Message should like this:

    {'type': '1', 'body': { 'sndr': '', 'recv': ' ', 'content': ' '}}
    """
    __msgtype__ = MessageType.TEXT_MESSAGE

    def __init__(self, sndr, recv, content, timestamp=None):
        self.sndr = sndr
        self.recv = recv
        self.content = content
        self.timestamp = timestamp

    @classmethod
    def factory(cls, msg):
        msg = msg['body']
        try:
            sndr = msg['sndr']
            recv = msg['recv']
            content = msg['content']
            timestamp = round(time.time() * 1000)
        except KeyError:
            raise MessageFormatError('Malformed msg {}'.format(msg))

        if not validate_int()(sndr):
            raise ValidatedError("sndr must be integer")

        if not validate_int()(recv):
            raise ValidatedError("recv must be integer")

        if not validate_str()(content):
            raise ValidatedError("content must be string!!!")

        return cls(sndr, recv, content, timestamp)

    @property
    def json(self):
        return {'type': self.__msgtype__.value,
                'body': {'sndr': self.sndr, 'recv': self.recv, 'content': self.content, 'timestamp': self.timestamp}}

class HeartBeat(Message):
    """
    Clients will send heartbeat messages every 5 minutes. If didn't get heartbeat after 5 minutes, the client maybe
    lost, so we should clean it from connection manager, and notify others if is necessary.

    When server received heartbeat from clients, the client connection should be touched for delaying timed-out.
    If the client connection didn't touched after 5 minutes, it will be explored, means it will be timed-out from
    connection manager and will be cleaned up.

    The message format is like this: {'type': 'heartbeat', 'uid': 'unique-user-id'}
    """
    __msgtype__ = MessageType.HEARTBEAT

    def __init__(self, uid):
        self.uid = uid

    @classmethod
    def factory(cls, msg):
        msg = msg['body']
        try:
            uid = msg['uid']
        except KeyError:
            raise MessageFormatError("Malformed msg {}".format(msg))

        if not validate_int()(uid):
            raise ValidatedError("uid must be integer")

        return cls(uid)

# internal message
class HeartBeatAck(object):
    """
    When server received heartbeat message from client, it will send heartbeat-ack message back.
    If client didn't received heartbeat-ack messages after 5 minutes, it will means that the server
    has lost. The client should reconnect the server for conversation.
    """
    __msgtype__ = MessageType.HEARTBEAT_ACK

    # def __init__(self):
    #     self._uid = None
    #
    # @property
    # def uid(self):
    #     return self._uid
    #
    # @uid.setter
    # def uid(self, uid):
    #     self._uid = uid

    @property
    def json(self):
        return {'type': self.__msgtype__}

    
class LogoutMessage(Message):
    """
    For user logout or connection lost

    {'type': 'logout', 'body': {'uid': ''}}

    @type: message type
    @uid: user id
    """
    __msgtype__ = MessageType.LOGOUT

    def __init__(self, uid):
        self.uid = uid

    @classmethod
    def factory(cls, msg):
        msg = msg['body']
        try:
            uid = msg['uid']
        except KeyError:
            raise MessageFormatError("Malformed msg {}".format(msg))

        if not validate_int()(uid):
            raise ValidatedError("uid must be integer")

        return cls(uid)

# class ReplyMessage(Message):
#     """
#     Used for sender back to client with custom service id
#
#     Message should like this:
#
#     {'type': 'reply', 'body': {'status': 200, 'content': 'message-content'}
#
#     """
#     __msgtype__ = MessageType.REPLY
#
#     def __init__(self, status, content):
#         self.status = status
#         self.content = content
#
#     @classmethod
#     def factory(cls, msg):
#         try:
#             status = msg['status']
#             content = msg['content']
#         except KeyError:
#             raise MessageFormatError("Malformed msg {}".format(msg))
#
#         return cls(status, content)
#
#     @property
#     def json(self):
#         return {'type': self.__msgtype__, 'body': {'status': self.status, 'cs_id': self.cs_id}}


if __name__ == '__main__':
    _msg = {'type': 'register', 'uid': '123456', 'role': '0'}
    M = Message()(_msg)
    print(M.uid, M.role)



