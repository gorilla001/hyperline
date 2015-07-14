__author__ = 'nmg'

import asyncio

_MESSAGE_PREFIX_LENGTH = 4

_BYTE_ORDER = 'big'

class HyperLineConsumer(object):

    _buffer = b''     # data buffer
    _msg_len = None   # message length

    def data_received(self, data):
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

class HyperLineProtocol(asyncio.Protocol):

    def __init__(self, consumer_factory=None, **kwargs):
        super().__init__(**kwargs)

        self._current_consumer = None
        self._consumer_factory = consumer_factory

    def connection_made(self, transport):
        """
        When connection made, build consumer for currently handling incoming data.
        :param transport:
        :return:
        """
        self._current_consumer = self.build_consumer()

    def data_received(self, data):

        while data:
            data = self._current_consumer.data_received(data)

    def _build_consumer(self):
        """
        Build consumer from factory.

        :return: the new build consumer
        """
        consumer = self._consumer_factory()
        assert self._current_consumer is None, 'Consumer is not None'
        self._current_consumer = consumer

        return self._current_consumer

    def build_consumer(self):
        """
        The :class:`HyperlineConsumer` currently handling incoming data.

        If no consumer is available, build a new one and return it.
        """
        if self._current_consumer is None:
            return self._build_consumer()

        return self._current_consumer
