__author__ = 'nmg'

import asyncio

_MESSAGE_PREFIX_LENGTH = 4

_BYTE_ORDER = 'big'

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


class WSProtocol(object):
    """
    Web socket protocol. Handling message data.

    The `ws.recv` method always recv entire message. If recv None, indicated that
    the connection is lost.

    Method `__call__` must accept two arguments, one is a `websockets.WebSocketServerProtocol` and
    the other is request URI.(ignored in this place)
    """
    @asyncio.coroutine
    def __call__(self, ws, _):

        yield from self.connection_made(ws)

        while True:
            # Recv message from websocket
            message = yield from ws.recv()

            if message is None:
                # When None received, seems connection has lost. close it and break the loop.
                yield from self.connection_lost()
                break
            # Consuming message in a coroutine.
            yield from self.message_received(message)

    @asyncio.coroutine
    def connection_made(self, ws):
        """
        Must override in subclass
        @param ws: `websockets.WebSocketServerProtocol`
        @return: None
        """
        raise NotImplementedError()

    @asyncio.coroutine
    def message_received(self, message):
        """
        Must override in subclass
        @param message: entire message
        @return: None
        """
        raise NotImplementedError()

    @asyncio.coroutine
    def connection_lost(self):
        """
        Must override in subclass
        @return: None
        """
        print('connection lost')
