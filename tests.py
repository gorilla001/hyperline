__author__ = 'nmg'

import socket

from struct import pack

import json

import random

import time

import threading

_MESSAGE = {
    "sender": "niuminguo",
    "receiver": "niuminguo",
}

def send_msg():
    s = socket.socket()
    s.settimeout(60)
    s.connect(('localhost', 8060))
    _MESSAGE.update( {'content': random.randint(0, 1000000000)} )
    msg = json.dumps(_MESSAGE)
    msg_len = len(msg)
    packed_msg = pack("!i%ds" % msg_len, msg_len, bytes(msg, encoding='utf-8'))

    time.sleep(10.0)

    s.send(packed_msg)

import threading
import time

class Test(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        s = socket.socket()
        s.settimeout(60)
        s.connect(('localhost', 8060))
        _MESSAGE.update( {'content': random.randint(0, 1000000000)} )
        msg = json.dumps(_MESSAGE)
        msg_len = len(msg)
        packed_msg = pack("!i%ds" % msg_len, msg_len, bytes(msg, encoding='utf-8'))

        time.sleep(10.0)

        s.send(packed_msg)

if __name__ == '__main__':
    threads = []
    for x in range(0, 20):
        threads.append(Test())
    # 启动线程
    for t in threads:
        t.start()
    # 等待子线程结束
    for t in threads:
        t.join()

# for i in range(10000):
#
#     s = socket.socket()
#
#     s.connect(('localhost', 8060))
#
#     _MESSAGE.update( {'content': i} )
#
#     msg = json.dumps(_MESSAGE)
#
#     msg_len = len(msg)
#
#     packed_msg = pack("!i%ds" % msg_len, msg_len, bytes(msg, encoding='utf-8'))
#
#     s.send(packed_msg)

