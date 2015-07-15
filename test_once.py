__author__ = 'nmg'


import socket
import json
import random
from struct import pack


_MESSAGE_TEXT = {
   'type': 'text',
    'sender': 'niuminguo',
    'receiver': 'niuminguo',
    'content': 'love',
}

_MESSAGE_REG = {
    'uid': 'niuminguo',
    'type': 'register',
}
content = """
    hello
"""


s = socket.socket()
s.settimeout(60)
s.connect(('localhost', 2222))
msg = json.dumps(_MESSAGE_REG)
msg_len = len(msg)
packed_msg = pack("!i%ds" % msg_len, msg_len, bytes(msg, encoding='utf-8'))
s.send(packed_msg)
s.close()
