__author__ = 'nmg'

import json

class MessageWrapper(object):
    """
    Message instance for handling message
    """
    def __init__(self, msg):
        self.msg = self.bytes_to_dict(msg)
        # self.type       = None
        # self.sender     = None
        # self.receiver   = None
        # self.content    = None


    @property
    def type(self):
        return self.msg.get('type')

    @property
    def sender(self):
        return self.msg.get('sender')

    @property
    def receiver(self):
        return self.msg.get('receiver')

    @property
    def content(self):
        return self.msg.get('content')

    @staticmethod
    def bytes_to_dict(msg):
        # Transfer bytes msg to python dictionary
        str_msg = msg.decode("utf-8")

        return json.loads((str_msg))

    @staticmethod
    def dict_to_bytes(msg):
        json_msg = json.dumps(msg)

        return bytes(json_msg, encoding='utf-8')

    @property
    def transport(self):
        pass

    def __repr__(self):
        return '%s' % self.dict_to_bytes(self.msg)

    __str__ = __repr__

