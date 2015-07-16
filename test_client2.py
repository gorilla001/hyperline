__author__ = 'nmg'


from autobahn.asyncio.websocket import WebSocketClientProtocol, \
    WebSocketClientFactory

import json
import random


#!/usr/bin/env python

import asyncio
import websockets
from asyncio import iscoroutine

# from concurrent.futures import ProcessPoolExecutor
#
# @asyncio.coroutine
# def hello():
#     ws = yield from websockets.connect('ws://localhost:9000/')
#
#     message = {'type': 'register', 'uid': 'client-2'}
#
#     yield from ws.send(json.dumps(message).encode('utf8'))
#
#     @asyncio.coroutine
#     def producer():
#         print('producer')
#         while True:
#             data = input(">")
#             message = {'type': 'text', 'sender': 'client-2', 'receiver': 'client-1', 'content': data}
#             yield from ws.send(json.dumps(message).encode('utf8'))
#
#     @asyncio.coroutine
#     def consumer():
#         print('consumer')
#         while True:
#             message = yield from ws.recv()
#             print("< {}".format(message))
#
#     tasks = [asyncio.async(producer()),
#              asyncio.async(consumer())]
#
#     asyncio.get_event_loop().run_until_complete(asyncio.wait(tasks))
#     #.async(asyncio.get_event_loop().run_in_executor(None, lambda: producer()))
#     #asyncio.async(asyncio.get_event_loop().run_in_executor(None, lambda: consumer()))
#     with ProcessPoolExecutor() as executor:
#         executor.submit(producer)
#         executor.submit(consumer)
#
#
#
# asyncio.get_event_loop().run_until_complete(hello())


class SlowSquareClientProtocol(WebSocketClientProtocol):

    def onOpen(self):
        message = {'type': 'register', 'uid': 'client-2'}
        self.sendMessage(json.dumps(message).encode('utf8'))

    def onMessage(self, payload, isBinary):
        res = json.loads(payload.decode('utf8'))
        print('< {}'.format(res['content']))

    def onClose(self, wasClean, code, reason):
        if reason:
            print(reason)
        loop.stop()


if __name__ == '__main__':

    import asyncio

    factory = WebSocketClientFactory("wss://localhost:9000", debug=False)
    factory.protocol = SlowSquareClientProtocol

    loop = asyncio.get_event_loop()
    coro = loop.create_connection(factory, '127.0.0.1', 9000)
    loop.run_until_complete(coro)
    loop.run_forever()
    loop.close()
