__author__ = 'nmg'


from twisted.internet.protocol import Factory

from twisted.internet import reactor

import json

from handlers import MessageHandler

from protocol import HyperLineProtocol

from twisted.internet.defer import Deferred


# class HyperLine(HyperLineProtocol):
#
#     def __init__(self):
#         super().__init__()
#         self.deferred = None
#
#     def connection_made(self):
#         #self.deferred = Deferred()
#         #self.deferred.addCallback(self.handler_msg)
#         pass
#
#     def message_received(self, msg):
#         """
#         The real message handler
#         :param msg: a full message without prefix length
#         :return: None
#         """
#         #self.deferred.callback(msg)
#         print(msg)
#
#     def handler_msg(self, msg):
#         # Convert bytes msg to python dictionary
#         msg = json.loads(msg.decode("utf-8"))
#         # Handler msg
#         msg['transport'] = self.transport
#
#         return self.factory.handler(msg)
#
#     def connection_lost(self, reason):
#         self.deferred = None
#
# class HyperLineFactory(Factory):
#     def __init__(self):
#         self.handler = MessageHandler()
#         #self.deferred = Deferred()
#
#     def buildProtocol(self, addr):
#         protocol = HyperLine()
#         protocol.factory = self
#
#         return protocol
#
#     # @property
#     # def deferred(self):
#     #     return self.deferred
#
#
# class HyperLineServer(object):
#     def __init__(self, port, factory, backlog=50, interface=''):
#         self.port = port
#         self.interface = interface
#         self.factory = factory
#         self.backlog = backlog
#
#         reactor.listenTCP(self.port, self.factory, self.backlog, self.interface)
#
#     @staticmethod
#     def start():
#         reactor.run()
#
# if __name__ == '__main__':
#     server = HyperLineServer(port=3333,
#                              factory=HyperLineFactory())
#     server.start()

import asyncio
from protocol import HyperLineTestProtocol
import json
from handlers import MessageHandler

class HyperLine(HyperLineTestProtocol):

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
        #msg = json.loads(msg.decode("utf-8"))
        # Handler msg
        #msg['transport'] = self.transport

        #return self.handler(msg)
        print(msg)

class HyperLineServer(object):
    def __init__(self, protocol_factory, host, port):

        self.host = host
        self.port = port
        self.protocol_factory = protocol_factory

    def start(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(loop.create_server(self.protocol_factory, self.host, self.port))
        loop.run_forever()

# loop = asyncio.get_event_loop()
# server = loop.run_until_complete(loop.create_server(HyperLine, 'localhost', 2222))
# loop.run_until_complete(server.wait_closed())

if __name__ == '__main__':

    server = HyperLineServer(HyperLine, 'localhost', 2222)
    server.start()
