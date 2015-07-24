__author__ = 'nmg'

import asyncio
import json
import websockets
import ast
import six
import logging

from protocol import HyperLineProtocol
from protocol import WSProtocol
from handlers import MessageHandler
from session import SessionManager
from messages import Message

logger = logging.getLogger(__name__)

class HyperLine(HyperLineProtocol):
    """
    Every new clients connection will create one HyperLine object for message handling.

        new connection -> HyperLine()
    """

    def __init__(self):

        self.handler = MessageHandler()  # singleton

        self.transport = None

    def connection_made(self, transport):

        self.transport = transport

    def message_received(self, msg):
        """
        The real message handler
        @param msg: a full message without prefix length
        @return: None
        """
        # Convert bytes msg to python dictionary
        msg = json.loads(msg.decode("utf-8"))

        # Handler msg
        return self.handler.handle(msg, self.transport)


class WSHyperLine(WSProtocol):

    def __init__(self):

        self.handler = MessageHandler()  # singleton
        self.session_manager = SessionManager()  # singleton
        self.message = Message()

    @asyncio.coroutine
    def connection_made(self, connection):
        # """
        # Every connection will create one new Session
        # """
        """
        Populated session attribute `transport` with `ws` from connection
        """
        connection.session.transport = connection.ws

        yield from connection.ws.send('welcome')

    @asyncio.coroutine
    def message_received(self, message, connection):
        """
        Decoding Json object to python dictionary. If it failed, send back the message and close connection.
        """
        try:
            message = json.loads(message)  # If message is json object
        except ValueError:
            yield from connection.ws.send("Malformed message {}".format(message))
            yield from connection.ws.close()
            return

        # Message format validate
        # if ('type', 'body') not in message:
        #     yield from connection.ws.send("Malformed message {}".format(message))
        #     yield from connection.ws.close()
        #     return

        #     # if isinstance(message, six.text_type):
        #     #     message = ast.literal_eval(message)
        #     #
        #     # if isinstance(message, six.binary_type):
        #     #     message = json.loads(message.decode("utf-8"))

        return self.handler.handle(self.message(message), connection.session)

    @asyncio.coroutine
    def connection_lost(self, connection):
        """Close connection and delete session from SessionManager"""
        print('connection lost')
        yield from connection.ws.close()

        self.session_manager.pop_session(connection.session)


class HyperLineServer(object):
    def __init__(self, protocol_factory, host, port, ws_host, ws_port):

        self.host = host
        self.port = port
        self.ws_host = ws_host
        self.ws_port = ws_port
        self.protocol_factory = protocol_factory

    def start(self):
        loop = asyncio.get_event_loop()
        logger.info('Socket server listened on {}:{}'.format(self.host, self.port))
        loop.run_until_complete(loop.create_server(self.protocol_factory, self.host, self.port))
        logger.info('Websocket server listened on {}:{}'.format(self.ws_host, self.ws_port))
        loop.run_until_complete(websockets.serve(WSHyperLine(), self.ws_host, self.ws_port))

        loop.run_forever()

