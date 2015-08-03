__author__ = 'nmg'

from meta import MetaMessage
import time
from enum import Enum
import log as logging
import traceback

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
    REGISTER = '0'
    MESSAGE = '1'
    UNREGISTER = '2'
    READY = '3'
    REPLY = '4'
    HEARTBEAT = '5'

    REGISTER_RESPONSE = '11'
    REQUEST_SERVICE = '12'
    REQUEST_SERVICE_RESPONSE = '13'
    ASSOCIATED_USERS = '14'
    HISTORY_MESSAGE = '15'

    UNKNOWN = '404'

class MessageFormatError(Exception):
    def __init__(self, err_msg=None):
        self.err_msg = err_msg if not None else "Malformed msg"

    def __str__(self):
        return 'MessageFormatError: {}'.format(self.err_msg)

class Message(metaclass=MetaMessage):
    """
    Base class for message class
    """
    # _struct_format = "!I"
    #
    # def pack(self, msg):
    #     return pack("!I", len(msg)) + bytes(msg, encoding='utf-8')
    def __call__(self, msg):

        try:
            return self._msg_factories[msg['type']].factory(msg)
        except (TypeError, KeyError):
            traceback.print_exc()
            raise MessageFormatError()

class RegisterMessage(Message):
    """
    Register message, message body should like this:

        # # {'type': 'register', 'uid': 'unique-user-id', 'role': 'user-role', 'service': 'the service will be called'}
        # {'type': 'register', 'uid': 'unique-user-id', 'role': 'user-role'}
        #
        # @type: message type
        # @uid:  message sender uid
        # @role: message sender role
        #        0 - normal user
        #        1 - custom service
        #        2 - sport man
        # # @service: which service will be called
        # #           0 - chat with normal user
        # #           1 - chat with custom service
        # #           2 - chat which sports man

        # {'type':'register', 'body': { 'uid': '1234', 'name': 'name', 'role': '0'}}
        {'type':'register', 'body': {'uid': '1234', 'name': 'name'}}
    """

    __msgtype__ = MessageType.REGISTER

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

        return cls(uid, name)

    @property
    def json(self):
        return {'type': self.__msgtype__, 'uid': self.uid, 'name': self.name}

class RequestForService(Message):
    """
    Ask for specified service, such as custom service or sports man service.

    Message should like this:

    # {'type': '12', 'body': {'content': '10'}}
    {'type': '12'}
    """
    __msgtype__ = MessageType.REQUEST_SERVICE

    # def __init__(self, content):
    #     self.content = content

    @classmethod
    def factory(cls, _):
        # try:
        #     content = msg['content']
        # except KeyError:
        #     raise MessageFormatError("Malformed msg {}".format(msg))

        # return cls(content)
        return cls()

    @property
    def json(self):
        # return {'type': self.__msgtype__.value, 'body': {'content': self.content}}
        return {'type': self.__msgtype__.value}

class RequestForServiceResponse(object):
    """
    Message: {'type': '13', body: {'status': 200, 'uid': self.uid, 'name': self.name}}
    """
    __msgtype__ = MessageType.REQUEST_SERVICE_RESPONSE

    def __init__(self, status=None, uid=None, name=None):
        self.status = status
        self.uid = uid
        self.name = name

    @property
    def json(self):
        return {'type': self.__msgtype__.value, 'body': {'status': self.status, 'uid': self.uid, 'name': self.name}}

class TextMessage(Message):
    """
    Message should like this:

    # {'type': 'message', 'body': {'receiver': '5678', 'content': 'hello'}}
    # {'type': 'message', 'body': {'recipient': 'recipient','role': 'role', 'content': 'content'}}
    # {'type': '1', 'body': { 'recv': ' ', 'content': ' '}}
    {'type': '1', 'body': { 'from': '', 'recv': ' ', 'content': ' '}}
    """
    __msgtype__ = MessageType.MESSAGE

    def __init__(self, uid, recv, content, timestamp=None):
        self.uid = uid
        self.recv = recv
        self.content = content
        self.timestamp = timestamp

    @classmethod
    def factory(cls, msg):
        msg = msg['body']
        try:
            uid = msg['uid']
            recv = msg['recv']
            content = msg['content']
            timestamp = round(time.time() * 1000)
        except KeyError:
            raise MessageFormatError('Malformed msg {}'.format(msg))

        return cls(uid, recv, content, timestamp)

    @property
    def json(self):
        return {'type': self.__msgtype__.value,
                'body': {'uid': self.uid, 'recv': self.recv, 'content': self.content, 'timestamp': self.timestamp}}

class UnregisterMessage(Message):
    """
    For user logout or connection lost
    """
    __msgtype__ = MessageType.UNREGISTER

    def __init__(self, uid):
        self.uid = uid

    @classmethod
    def factory(cls, msg):
        msg = msg['body']
        try:
            uid = msg['uid']
        except KeyError:
            raise MessageFormatError("Malformed msg {}".format(msg))

        return cls(uid)

class ReplyMessage(Message):
    """
    Used for sender back to client with custom service id

    Message should like this:

    {'type': 'reply', 'body': {'status': 200, 'content': 'message-content'}

    """
    __msgtype__ = MessageType.REPLY

    def __init__(self, status, content):
        self.status = status
        self.content = content

    @classmethod
    def factory(cls, msg):
        try:
            status = msg['status']
            content = msg['content']
        except KeyError:
            raise MessageFormatError("Malformed msg {}".format(msg))

        return cls(status, content)

    @property
    def json(self):
        return {'type': self.__msgtype__, 'body': {'status': self.status, 'cs_id': self.cs_id}}

# Internal message
class ReadyMessage(object):
    """
    Used for telling custom service and normal user start conversation.
    """
    __msgtype__ = MessageType.READY

    def __init__(self, uid=None, name=None):
        self.uid = uid
        self.name = name

    @property
    def json(self):
        return {'type': self.__msgtype__.value, 'body': {'uid': self.uid, 'name': self.name}}

# Internal message
class RegisterSucceed(object):
    """
    Used for register reply while register succeed.

    Message: {'type': '5', body: {'status': 200}}
    """
    __msgtype__ = MessageType.REGISTER_RESPONSE

    def __init__(self, status=200):
        self.status = status

    @property
    def json(self):
        return {'type': self.__msgtype__.value, 'body': {'status': self.status}}

# Internal message
class RegisterFailed(object):
    """
    Used for reply while register failed.

    Message: {'type': '5', 'body': {'status': 500, 'reason': ''}}

    """
    __msgtype__ = MessageType.REGISTER_RESPONSE

    def __init__(self, status=500, reason=''):
        self.status = status
        self.reason = reason

    @property
    def json(self):
        return {'type': self.__msgtype__.value, 'body': {'status': 500, 'reason': self.reason}}

# Internal message
class UserMessage(object):
    """

    """
    __msgtype__ = MessageType.ASSOCIATED_USERS

    def __init__(self):
        self.users = []

    def append(self, uid, name):
        user = {'uid': uid, 'name': name}
        if user not in self.users:
            self.users.append(user)

    @property
    def json(self):
        return {'type': self.__msgtype__.value, 'body': self.users}

class GetHistoryMessage(Message):
    """
    Get user history message

    {'type': '15', 'body': {'recv': 100, 'offset': 0, 'count': 10}}
    """
    __msgtype__ = MessageType.HISTORY_MESSAGE

    def __init__(self, recv, offset, count):
        self.recv = recv
        self.offset = offset
        self.count = count

    @classmethod
    def factory(cls, msg):
        msg = msg['body']
        try:
            recv = msg['recv']
            offset = msg['offset']
            count = msg['count']
        except KeyError:
            traceback.print_exc()
            raise MessageFormatError()

        return cls(recv, offset, count)

# Internal message
class HistoryMessage(object):
    """
    History message send to uers
    """
    __msgtype__ = MessageType.HISTORY_MESSAGE

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

if __name__ == '__main__':
    _msg = {'type': 'register', 'uid': '123456', 'role': '0'}
    M = Message()(_msg)
    print(M.uid, M.role)



