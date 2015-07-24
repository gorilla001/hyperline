__author__ = 'nmg'

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
    """
    Register message, message body should like this:

        {'type': 'register', 'uid': 'unique-user-id', 'role': 'user-role', 'service': 'the service will be called'}

        @type: message type
        @uid:  message sender uid
        @role: message sender role
               0 - normal user
               1 - custom service
               2 - sport man
        @service: which service will be called
                  0 - chat with normal user
                  1 - chat with custom service
                  2 - chat which sports man
    """

    __msgtype__ = 'register'

    def __init__(self, uid, role, service):
        self.uid = uid
        self.role = role
        self.service = service

    @classmethod
    def factory(cls, msg):
        try:
            uid = msg['uid']
            role = msg['role']
            service = msg['service']
        except KeyError:
            raise MessageFormatError("Malformed msg {}".format(msg))

        return cls(uid, role, service)

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
    _msg = {'type': 'register', 'uid': '123456', 'role': '0'}
    M = Message()(_msg)
    print(M.uid, M.role)



