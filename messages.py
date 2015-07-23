__author__ = 'nmg'

from struct import pack
from meta import MetaMessage
import time

class MessageFormatError(Exception):
    def __init__(self, err_msg):
        self.err_msg = err_msg

    def __str__(self):
        return self.err_msg

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
            raise MessageFormatError("Malformed msg {}.".format(msg))

class RegisterMessage(Message):

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

        return cls(uid, role )

class TextMessage(Message):
    __msgtype__ = 'text'  # Text message

    def __init__(self, sender, receiver, content, timestamp=None):
        self.sender = sender
        self.receiver = receiver
        self.content = content
        self.timestamp = timestamp

    @classmethod
    def factory(cls, msg):
        try:
            sender = msg['sender']
            receiver = msg['receiver']
            content = msg['content']
            timestamp = time.now()
        except KeyError:
            raise MessageFormatError('Malformed msg {}'.format(msg))

        return cls(sender, receiver, content, timestamp)

    @property
    def json(self):
        return {
            'sender': self.sender,
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
    msg = {'type': 'register', 'uid': '123456', 'role': '0'}
    M = Message()(msg)
    print(M.uid, M.role)



