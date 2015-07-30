__author__ = 'nmg'

import asyncio
import websockets
from struct import pack
import json

import log as logging
# from session import Session
from messages import MessageFormatError
# from collections import namedtuple
from managers import NormalUserConnectionManager, CustomServiceConnectionManager

_MESSAGE_PREFIX_LENGTH = 4

_BYTE_ORDER = 'big'

logger = logging.getLogger(__name__)


class HyperLineProtocol(asyncio.Protocol):
    """
    Normal socket protocol. Handling stream data.
    """

    _buffer = b''     # data buffer
    _msg_len = None   # message length

    def data_received(self, data):

        while data:
            data = self.process_data(data)

    def process_data(self, data):
        """
        Called when some data is received.

        This method must be implemented by subclasses

        The argument is a bytes object.
        """
        self._buffer += data

        # For store the rest data out-of a full message
        _buffer = None

        if self._msg_len is None:
            # If buffer length < _MESSAGE_PREFIX_LENGTH return for more data
            if len(self._buffer) < _MESSAGE_PREFIX_LENGTH:
                return

            # If buffer length >= _MESSAGE_PREFIX_LENGTH
            self._msg_len = int.from_bytes(self._buffer[:_MESSAGE_PREFIX_LENGTH], byteorder=_BYTE_ORDER)

            # The left bytes will be the message body
            self._buffer = self._buffer[_MESSAGE_PREFIX_LENGTH:]

        # Received full message
        if len(self._buffer) >= self._msg_len:
            # Call message_received to handler message
            self.message_received(self._buffer[:self._msg_len])

            # Left the rest of the buffer for next message
            _buffer = self._buffer[self._msg_len:]

            # Clean data buffer for next message
            self._buffer = b''

            # Set message length to None for next message
            self._msg_len = None

        return _buffer

    def message_received(self, msg):
        """
        Must override in subclass

        :param msg: the full message
        :return: None
        """
        raise NotImplementedError()

class Connection(object):
    """
    Connection object is used for managing connection(transport). After `timeout` seconds, and
    has no `touch` called, the connection will be closed.
    """
    __slots__ = ['uid', 'name', 'role', 'path', 'transport', 'associated_sessions',
                 'timeout', '_loop', '_timeout_handler', 'manager']

    def __init__(self, ws, path, timeout=1800):
        self.uid = None  # client id
        self.name = None  # client name

        self.path = path
        self.transport = ws  # client connection

        # self.associated_sessions = {}

        self.timeout = timeout
        self._loop = asyncio.get_event_loop()
        self._timeout_handler = None

    def add_timeout(self, timeout=None):
        if timeout is None:
            timeout = self.timeout

        self._timeout_handler = self._loop.call_later(timeout, self.timeout_handler)

    def timeout_handler(self):
        # Close connection
        asyncio.async(self.transport.close())

        # Delete self from SessionManager
        self.explode()

    def cancel_timeout(self):
        """
        Cancel timeout handler. So the close_connection action will not be acted.
        """
        self._timeout_handler.cancel()
        self._timeout_handler = None

    def touch(self):
        """
        Cancel timeout handler and re-add handler. The client will call `touch` for
        next timeout.

        Every `heartbeat` message received or every `chat` message received, the session
        will be touched.
        """
        self.cancel_timeout()
        self.add_timeout()

    def explode(self):
        """
        When session explode, it will delete itself from SessionManager.
        """
        if self.path == '/service':
            _connection_manager = CustomServiceConnectionManager()
        else:
            _connection_manager = NormalUserConnectionManager()

        _connection_manager.pop_connection(self.uid)

    @asyncio.coroutine
    def close(self):
        """
        Close Session connection
        """
        asyncio.async(self.transport.close())
        self.transport = None

    @asyncio.coroutine
    def send(self, msg):
        # yield from self.transport.send(json.dumps(msg))
        try:
            yield from self.transport.send(json.dumps(msg.json))
        except websockets.exceptions.InvalidState as exc:
            logger.error("Send message failed! {}".format(exc))

    def write(self, msg):
        self.transport.write(pack("!I", len(msg)) + bytes(msg, encoding='utf-8'))

    @property
    def is_websocket(self):
        return hasattr(self.transport, 'send')


# class Connection(object):
#     def __init__(self, ws, session):
#         self.ws = ws
#         self.session = session
#
#     @property
#     def address(self):
#         return "{}:{}".format(self.ws.host, self.ws.port)
# Connection = namedtuple('Connection', ['ws', 'path', 'session'])

class WSProtocol(object):
    """
    Web socket protocol. Handling message data.

    The `ws.recv` method always recv entire message. If recv None, indicated that
    the connection is lost.

    Method `__call__` must accept two arguments, one is a `websockets.server.WebSocketServerProtocol` and
    the other is request URI.(ignored in this place)
    """
    @asyncio.coroutine
    def __call__(self, ws, path):

        connection = Connection(ws, path)

        yield from self.connection_made(connection)

        while True:
            # Recv message from websocket
            message = yield from ws.recv()

            if message is None:
                # When None received, seems connection has lost. close it and break the loop.
                yield from self.connection_lost(connection)
                break
            # Consuming message in a coroutine.
            try:
                yield from self.message_received(message, connection)
            except MessageFormatError as exc:
                logger.warn(exc)
                # yield from self.connection_lost(connection)
                # break

    @asyncio.coroutine
    def connection_made(self, connection):
        """
        Must override in subclass
        @param connection: Connection object
        @return: None
        """
        raise NotImplementedError()

    @asyncio.coroutine
    def message_received(self, message, connection):
        """
        Must override in subclass
        @param message: entire message
        @param connection: Connection object
        @return: None
        """
        raise NotImplementedError()

    @asyncio.coroutine
    def connection_lost(self, connection):
        """
        Must override in subclass
        @return: None
        """
        logger.info('connection lost')

        yield from connection.close()

        if connection.path == '/service':
            CustomServiceConnectionManager().pop_connection(connection.uid)
        else:
            NormalUserConnectionManager().pop_connection(connection.uid)
