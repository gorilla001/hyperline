__author__ = 'nmg'

import asyncio
import json

from protocol import HyperLineProtocol
from handlers import MessageHandler

class HyperLine(HyperLineProtocol):

    def __init__(self, message_handler=None):

        self.handler = message_handler
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
        msg['transport'] = self.transport

        return self.handler(msg)

class HyperLineServer(object):
    def __init__(self, protocol_factory, host, port):

        self.host = host
        self.port = port
        self.protocol_factory = protocol_factory

    def start(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(loop.create_server(self.protocol_factory, self.host, self.port))
        loop.run_forever()

if __name__ == '__main__':

    server = HyperLineServer(HyperLine(MessageHandler), 'localhost', 2222)
    server.start()
