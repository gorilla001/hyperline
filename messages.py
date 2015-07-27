__author__ = 'nmg'

from meta import MetaMessage
import time
from enum import Enum
import log as logging

logger = logging.getLogger(__name__)

class MessageType(Enum):
    """
    Message type
    """
    register = '0'
    message = '1'
    unregister = '2'
    ready = '3'
    reply = '4'

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
            return self._msg_factories[msg['type']].factory(msg['body'])
        except TypeError:
            logging.error("Malformed msg {}.".format(msg))
        except KeyError:
            logging.error("Malformed msg {}.".format(msg))
            # raise MessageFormatError("Malformed msg {}.".format(msg))

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

        {'type':'register', 'body': { 'uid': '1234', 'role': '0'}}
    """

    # __msgtype__ = 'register'
    __msgtype__ = MessageType.register

    def __init__(self, uid, role):
        self.uid = uid
        self.role = role

    @classmethod
    def factory(cls, msg):
        try:
            uid = msg['uid']
            role = msg['role']
        except KeyError:
            raise MessageFormatError("Malformed msg {}".format(msg))

        return cls(uid, role)

    @property
    def json(self):
        return {'type': self.__msgtype__, 'uid': self.uid, 'role': self.role}

# class RequestMessage(Message):
#     """
#     Ask for specified service, such as custom service or sports man service.
#
#     Message should like this:
#
#     {'type': 'request', 'body': {'content':
#     """

class TextMessage(Message):
    """
    Message should like this:

    # {'type': 'message', 'body': {'receiver': '5678', 'content': 'hello'}}
    # {'type': 'message', 'body': {'recipient': 'recipient','role': 'role', 'content': 'content'}}
    {'type': 'message', 'body': { 'recv': ' ', 'content': ' '}}
    """
    # __msgtype__ = 'message'  # Text message
    __msgtype__ = MessageType.message

    def __init__(self, recv, content, timestamp=None):
        self.recv = recv
        self.content = content
        self.timestamp = timestamp

    @classmethod
    def factory(cls, msg):
        try:
            recv = msg['recv']
            content = msg['content']
            timestamp = time.time()
        except KeyError:
            raise MessageFormatError('Malformed msg {}'.format(msg))

        return cls(recv, content, timestamp)

    @property
    def json(self):
        return {
            'content': self.content,
            'timestamp': self.timestamp,
        }

class UnregisterMessage(Message):
    # __msgtype__ = 'unregister'
    __msgtype__ = MessageType.unregister

    def __init__(self, uid):
        self.uid = uid

    @classmethod
    def factory(cls, msg):
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
    # __msgtype__ = 'reply'
    __msgtype__ = MessageType.reply

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


class ReadyMessage(object):
    """
    Used for telling custom service and normal user start conversation.
    """
    __msgtype__ = MessageType.ready

    def __init__(self, status=None, uid=None, name=None):
        self.status = status
        self.uid = uid
        self.name = name

    @property
    def json(self):
        return {'type': self.__msgtype__, 'body': {'status': self.status, 'uid': self.uid, 'name': self.name}}

if __name__ == '__main__':
    _msg = {'type': 'register', 'uid': '123456', 'role': '0'}
    M = Message()(_msg)
    print(M.uid, M.role)



