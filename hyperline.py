__author__ = 'nmg'

import asyncio
import json
import websockets
import ast
import six

from protocol import HyperLineProtocol
from protocol import WSProtocol
from handlers import MessageHandler

class HyperLine(HyperLineProtocol):

    def __init__(self):

        self.handler = MessageHandler()

        self.transport = None

    def connection_made(self, transport):

        self.transport = transport

    def message_received(self, msg):
        """
        The real message handler
        :param msg: a full message without prefix length
        :return: None
        """
        # Convert bytes msg to python dictionary
        msg = json.loads(msg.decode("utf-8"))

        # Handler msg
        return self.handler.handle(msg, self.transport)


class WSHyperLine(WSProtocol):

    def __init__(self):

        self.handler = MessageHandler()

        self.transport = None

    @asyncio.coroutine
    def connection_made(self, ws):
        self.transport = ws

    @asyncio.coroutine
    def message_received(self, message):

        if isinstance(message, six.text_type):
            message = ast.literal_eval(message)

        if isinstance(message, six.binary_type):
            message = json.loads(message.decode("utf-8"))

        return self.handler.handle(message, self.transport)


class HyperLineServer(object):
    def __init__(self, protocol_factory, host, port):

        self.host = host
        self.port = port
        self.protocol_factory = protocol_factory

    def start(self):
        loop = asyncio.get_event_loop()
        print('Socket server listened on {}:{}'.format(self.host, self.port))
        loop.run_until_complete(loop.create_server(self.protocol_factory, self.host, self.port))
        print('Websocket server listened on {}:{}'.format(self.host, '9000'))
        loop.run_until_complete(websockets.serve(WSHyperLine(), self.host, 9000))

        loop.run_forever()

if __name__ == '__main__':

    server = HyperLineServer(HyperLine, 'localhost', 2222)
    server.start()
