__author__ = 'nmg'

from server import HyperLineServer
from protocol import HyperLineConsumer
from handlers import handler
from pulsar.async.futures import task
import json

class HyperLineConsumerFactory(HyperLineConsumer):

    def connection_made(self, connection):
        """
        When connection made, try to connected to AMQP, created queue, and listened for consume.

        Every consumer listened message that belong to it, if messaged received, it will be
        write back to consumer's connection.That means every consumer must associated a connection.

        A consumer also a producer, it means a consumer producing messages send to others, and consuming
        messages for itself.If a message is sending for others, a consumer will be a producer, and
        put the message in queue, otherwise when a message is sending for itself, a consumer is consumer,
        and get the message from queue and write back to it's connection.

        So we called such a consumer as a proxy, a MessageProxy.

        :param connection:
        :return:
        """
        self.logger.info("connected from {}".format(connection))

    @task
    def message_received(self, msg):
        """
        The real message handler
        :param msg: a full message without prefix length
        :return: None
        """
        # Convert bytes msg to python dictionary
        msg = json.loads(msg.decode("utf-8"))

        # Handler msg
        #msg['connection'] = self.connection
        #msg['logger'] = self.logger

        #return handler(msg)
        print(msg)

    def connection_lost(self, connection):
        self.logger.info("disconnected from {}".format(connection))


def server(name=None, description=None, **kwargs):
    """Create the :class:`.SocketServer` with :class:`HyperLineProtocolFactory`
    as protocol factory.
    """
    name = name or 'hyperline'
    description = description or 'hyperline'
    return HyperLineServer(callable=HyperLineConsumerFactory,
                           name=name,
                           description=description,
                           **kwargs)


if __name__ == '__main__':

    server().start()

