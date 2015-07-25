__author__ = 'nmg'


from autobahn.asyncio.websocket import WebSocketClientProtocol, \
    WebSocketClientFactory

import json
import random

import asyncio
import websockets

# @asyncio.coroutine
# def hello():
#     ws = yield from websockets.connect('ws://localhost:9000/')
#
#     message = {'type': 'register', 'uid': 'client-1'}
#
#     yield from ws.send(json.dumps(message).encode('utf8'))
#
#     while True:
#         data = input(">")
#         message = {'type': 'text', 'sender': 'client-1', 'receiver': 'client-2', 'content': data}
#         yield from ws.send(json.dumps(message).encode('utf8'))
# #
#     message = yield from ws.recv()
#     print("< {}".format(message))
#
# asyncio.get_event_loop().run_until_complete(hello())

class SlowSquareClientProtocol(WebSocketClientProtocol):

    def onOpen(self):
        message = {'type': 'register', 'body': {'uid': 'client-1', 'role': '10'}}
        self.sendMessage(json.dumps(message).encode('utf8'))
        # #self.sendMessage(bytes(message, encoding='utf8'))
        # self.sendMessage(bytes('hello', encoding='utf8'))

        print('connected')

        # while True:
        #     data = input(">")
        #     message = {'type': 'text', 'sender': 'client-1', 'receiver': 'zhangsan', 'content': data}
        #     self.sendMessage(json.dumps(message).encode('utf8'))

    def onMessage(self, payload, isBinary):
        pass
        # if not isBinary:
        #     res = json.loads(payload.decode('utf8'))
        #     print("< {}".format(res))
        #     self.sendClose()
        #res = json.loads(payload.decode('utf8'))
        #print(res)
        # print(payload)
        #
        # #print('< {}'.format(res['content']))
        #
        # data = input(">")
        # message = {'type': 'text', 'sender': 'client-1', 'receiver': 'client-2', 'content': data}
        # self.sendMessage(json.dumps(message).encode('utf8'))

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
