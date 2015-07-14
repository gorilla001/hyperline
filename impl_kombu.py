__author__ = 'nmg'

import kombu
import kombu.entity
import kombu.messaging
import sys
import time
import itertools

class PublisherBase(object):
    """Base class for message publisher"""

    def __init__(self, channel, exchange_name, routing_key, **kwargs):
        """
        Initialise the publisher class with exchange_name and routing_key
        """
        self.channel = channel
        self.exchange_name = exchange_name
        self.routing_key = routing_key
        self.kwargs = kwargs
        self.exchange = None
        self.producer = None
        self.connect()

    def connect(self):
        self.exchange = kombu.entity.Exchange(name=self.exchange_name, **self.kwargs)

        self.producer = kombu.messaging.Producer(exchange=self.exchange,
                                                 channel=self.channel,
                                                 routing_key=self.routing_key)

    def send(self, msg):
        self.producer.publish(msg)

class TopicPublisher(PublisherBase):
    """
    A TopicPublisher is a publisher which sending message to AMQP according to it's topic,
    and here topic is message receiver.
    """
    def __init__(self, channel, topic, **kwargs):
        """
        Kombu options may be passed as keyword args to override defaults
        """
        options = {
            'durable': True,
            'auto_delete': False,
            'exclusive': False,
        }
        options.update(kwargs)
        super(TopicPublisher, self).__init__(channel,
                                             'hyperline',  # conf.control_exchange,
                                             topic,
                                             type='topic',
                                             **options)

class ConsumerBase(object):
    """Base class for message consumer"""

    def __init__(self, channel, connection, tag, **kwargs):
        self.connection = connection
        self.tag = str(tag)
        self.kwargs = kwargs
        self.channel = channel
        self.queue = None

        self.connect(self.channel)

    def connect(self, channel):
        """Declare the queque after rabbit connected"""
        self.kwargs['channel'] = channel
        self.queue = kombu.entity.Queue(**self.kwargs)
        self.queue.declare()

    def consume(self, *args, **kwargs):
        options = {'consumer_tag': self.tag}
        options['nowait'] = kwargs.get('nowait', False)
        connection = kwargs.get('connection', self.connection)
        if not connection:
            raise ValueError("No connection found")

        def _callback(raw_message):
            message = self.channel.message_to_python(raw_message)
            try:
                #connection.write(message.payload)
                print('hello')
                print(message.payload)
            except Exception:
                raise
            else:
                message.ack()

        """
        Start a queue consumer. Consumers last as long as the channel they were created on,
        or until the client cancels them.
        """

        return self.queue.consume(*args, callback=_callback, **options)


class TopicConsumer(ConsumerBase):
    """
    A TopicConsumer will receive messages from the queue and write back to it's connection
    """
    def __init__(self, channel, topic, connection, tag, name=None, **kwargs):

        options = {
            'durable': True,
            'auto_delete': False,
            'exclusive': False
        }
        options.update(kwargs)

        exchange = kombu.entity.Exchange(name='hyperline',  # conf.control_exchange,
                                         type='topic',
                                         durable=options['durable'],
                                         auto_delete=options['auto_delete'])

        super(TopicConsumer, self).__init__(channel,
                                            connection,
                                            tag,
                                            name=name,
                                            exchange=exchange,
                                            routing_key=topic,
                                            **options)

class Connection(object):
    """Connection object"""

    def __init__(self,
                 rabbit_host,
                 rabbit_port,
                 rabbit_userid,
                 rabbit_password,
                 rabbit_virtual_host,
                 max_retries=5,
                 retry_interval=5):

        self.max_retries = max_retries
        self.retry_interval = retry_interval
        self.consumer_num = itertools.count(1)
        self.consumers = []

        params = {}
        params.setdefault('hostname', rabbit_host)
        params.setdefault('port', int(rabbit_port))
        params.setdefault('userid', rabbit_userid)
        params.setdefault('password', rabbit_password)
        params.setdefault('virtual_host', rabbit_virtual_host)

        self.params = params
        self.connection = None
        self.channel = None
        self.connect()

    def _connect(self):
        """Connect to rabbit"""
        if self.connection is not None:
            try:
                self.connection.close()
            except:
                pass
            self.connection = None
        print("Connecting to AMQP server on %(hostname)s:%(port)d" % self.params)
        self.connection = kombu.connection.BrokerConnection(**self.params)
        self.connection.connect()
        self.channel = self.connection.channel()

    def connect(self):

        attempt = 0
        while True:
            attempt += 1
            try:
                self._connect()
                return
            except:
                print("Connecting to AMQP failed...retry")

            print(attempt)
            if attempt >= self.max_retries:
                print("Connecting to AMQP server on %(hostname)s:%(port)d falied" % self.params)
                sys.exit(1)
            time.sleep(self.retry_interval)

    # def ensure(self, error_callback, method, *args, **kwargs):
    #     """Make sure the method was invoked succeed"""
    #     while True:
    #         try:
    #             return method(*args, **kwargs)
    #         except Exception as ex:
    #             error_callback(ex)
    #
    #         self.connect()

    def publisher_send(self, publisher_cls, topic, msg):
        """Send message from publisher"""
        # def _error_callback(exc):
        #     print(exc)
        #     print("Send topic messsage failed")
        #
        # def _publish():
        #     publisher = publisher_cls(self.channel, topic)
        #     publisher.send(msg)
        #
        # self.ensure(_error_callback,_publish)
        publisher = publisher_cls(self.channel, topic)
        publisher.send(msg)

    def topic_send(self, topic, msg):
        """Send a 'topic' message"""
        self.publisher_send(TopicPublisher, topic, msg)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.connection.close()
        self.channel = None
        self.connection = None

    def declare_consumer(self, consumer_cls, topic, connection):
        """Create a Consumer using the class that was passed in and
           add it to our list of consumers"""

        consumer = consumer_cls(self.channel, topic, connection, next(self.consumer_num))
        self.consumers.append(consumer)
        return consumer

    def declare_topic_consumer(self, topic, connection):
        """Create a 'topic' consumer"""
        self.declare_consumer(TopicConsumer, topic, connection)

    def create_consumer(self, topic, connection, fanout=False):
        """Create a consumer that calls a method in a proxy object"""
        if fanout:
            self.declare_fanout_consumer(topic, connection)
        else:
            self.declare_topic_consumer(topic, connection)

    def drain_events(self):

        return self.connection.drain_events()

class MessageProxy(object):
    """
    A MessageProxy plays two important roles, one is producing messages, the other
    is consuming messages.

    A MessageProxy will be instanced(?) when a new connection is made. One Connection
    map to one MessageProxy instances.

    When Connection is closed or lost, the MessageProxy will be destroyed.

    A MessageProxy will contains two primary methods, `send` and `consume`, the former
    used for sending messages to queue, and the latter used for getting message from queue.
    """


