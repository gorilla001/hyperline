__author__ = 'nmg'


import socket
import json
import random
from struct import pack


_MESSAGE = {
    "sender": 'abc',
    "receiver": "abc",
    "type": "register",
    "content": "hello"
}


content = """
    hello
"""


s = socket.socket()
s.settimeout(60)
s.connect(('localhost', 9999))
msg = json.dumps(_MESSAGE)
msg_len = len(msg)
packed_msg = pack("!i%ds" % msg_len, msg_len, bytes(msg, encoding='utf-8'))
s.send(packed_msg)
s.close()
