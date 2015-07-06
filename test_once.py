__author__ = 'nmg'


import socket
import json
import random
from struct import pack


_MESSAGE = {
    "sender": "niuminguo",
    "receiver": "niuminguo",
}


s = socket.socket()
s.settimeout(60)
s.connect(('localhost', 8060))
_MESSAGE.update( {'content': random.randint(0, 1000000000)} )
msg = json.dumps(_MESSAGE)
msg_len = len(msg)
packed_msg = pack("!i%ds" % msg_len, msg_len, bytes(msg, encoding='utf-8'))
s.send(packed_msg)
