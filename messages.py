__author__ = 'nmg'

from meta import MetaMessage
import time

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
            print("Malformed msg {}.".format(msg))
        except KeyError:
            print("Malformed msg {}.".format(msg))
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

    __msgtype__ = 'register'

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

    {'type': 'message', 'body': {'receiver': '5678', 'content': 'hello'}}
    """
    __msgtype__ = 'message'  # Text message

    def __init__(self, receiver, content, timestamp=None):
        # self.sender = sender
        self.receiver = receiver
        self.content = content
        self.timestamp = timestamp

    @classmethod
    def factory(cls, msg):
        try:
            # sender = msg['sender']
            receiver = msg['receiver']
            content = msg['content']
            timestamp = time.now()
        except KeyError:
            raise MessageFormatError('Malformed msg {}'.format(msg))

        return cls(receiver, content, timestamp)

    @property
    def json(self):
        return {
            'receiver': self.receiver,
            'content': self.content,
            'timestamp': self.timestamp,
        }

class UnregisterMessage(Message):
    __msgtype__ = 'unregister'

    def __init__(self, uid):
        self.uid = uid

    @classmethod
    def factory(cls, msg):
        try:
            uid = msg['uid']
        except KeyError:
            raise MessageFormatError("Malformed msg {}".format(msg))

        return cls(uid)

if __name__ == '__main__':
    _msg = {'type': 'register', 'uid': '123456', 'role': '0'}
    M = Message()(_msg)
    print(M.uid, M.role)



