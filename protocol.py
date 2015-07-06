__author__ = 'nmg'

from pulsar import Protocol
from pulsar.async.futures import Future
from pulsar.async.mixins import Timeout
from pulsar.async.events import EventHandler

_MESSAGE_PREFIX_LENGTH = 4

_BYTE_ORDER = 'big'

class HyperLineConsumer(EventHandler):

    _buffer = b''   # data buffer
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

    def process_data(self, data):
        # Called by Connection, it updates the counters and invoke
        # the high level data_received method which must be implemented
        # by subclasses

        return self.data_received(data)

    def connection_made(self, connection):
        """
        Called when connection is made.

        This method must be implemented by subclasses

        The argument is current connection

        :param connection:  the current connection
        :return: None
        """
        raise NotImplementedError()

    def connection_lost(self, connection):
        """
        Called when connection is lost.

        This method must be implemented by subclass

        The argument is current connection

        :param connection:  the current connection
        :return: None
        """
        raise NotImplementedError()

class HyperLineProtocol(Protocol, Timeout):
    def __init__(self, **kw):
        super().__init__(**kw)


class HyperLineConnection(HyperLineProtocol):
    """
    Connection used for every new client connection.

    When connection made, a consumer will be build for data processing.
    """
    def __init__(self, consumer_factory=None, timeout=None, **kw):
        super().__init__(**kw)

        # Bind `connection_made` event which will be fired when connection made
        self.bind_event('connection_made', self._connection_made)

        # Bind `connection_lost` event which will be fired whe connection lost
        self.bind_event('connection_lost', self._connection_lost)

        self._current_consumer = None
        self._consumer_factory = consumer_factory

        # Bind `Timeout._add_timeout` for `data_received` event and
        # `Timeout._cancel_timeout` for `data_processed` event.
        # If not do this, connection timeout will never be set.

        self.timeout = timeout

    def current_consumer(self):
        """The :class:`ProtocolConsumer` currently handling incoming data.

        This instance will receive data when this connection get data
        from the :attr:`~PulsarProtocol.transport` via the
        :meth:`data_received` method.

        If no consumer is available, build a new one and return it.
        """
        if self._current_consumer is None:
            self._build_consumer()
        return self._current_consumer

    def data_received(self, data):
        """
        Handling data received from clients.

        Once done set a timeout for idle connections
        """
        # call `HyperLineConnection._cancel_timeout` for cancel `Timeout`
        self.fire_event('data_received', data=data)
        # Circularly handling message until finished
        # while data:
        #     #data = self.current_consumer().process_data(data)
        #     data = self._current_consumer.process_data(data)
        #     if isinstance(data, Future):
        #         break
        while data:
            data = self._current_consumer.process_data(data)

        # Call `HyperLineConnection._add_timeout` for set `Timeout` again
        self.fire_event('data_processed', data=data)

    def _build_consumer(self):
        """
        Build consumer when data received
        """
        consumer = self._consumer_factory(loop=self._loop)
        assert self._current_consumer is None, 'Consumer is not None'
        self._current_consumer = consumer
        self._current_consumer._connection = self

    def _connection_lost(self, _, exc=None):
        """It performs these actions in the following order:

        * Fires the ``connection_lost`` :ref:`one time event <one-time-event>`
          if not fired before, with ``exc`` as event data.
        * Cancel the idle timeout if set.
        * Invokes the :meth:`ProtocolConsumer.connection_lost` method in the
          :meth:`current_consumer`.
        """
        if self._current_consumer:
            self._current_consumer.connection_lost(self)

    def _connection_made(self, _, exc=None):
        """Handler connection_made event in ProtocolConsumer
           or in its subclass"""

        self.current_consumer()
        if self._current_consumer:
            self._current_consumer.connection_made(self)
