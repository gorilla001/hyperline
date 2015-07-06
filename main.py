__author__ = 'nmg'

from hyperline import HyperLineSocketServer
from protocol import HyperLineConsumer


class HyperLineProtocolFactory(HyperLineConsumer):

    def connection_made(self, connection):
        self.logger.info("connected from {}".format(connection))

    def message_received(self, msg):
        self.logger.info(msg)

    def connection_lost(self, connection):
        self.logger.info("disconnected from {}".format(connection))

def server(name=None, description=None, **kwargs):
    """Create the :class:`.SocketServer` with :class:`HyperLineProtocolFactory`
    as protocol factory.
    """
    name = name or 'hyperline'
    description = description or 'hyperline'
    return HyperLineSocketServer(HyperLineProtocolFactory,
                                 name=name,
                                 description=description,
                                 **kwargs)

if __name__ == '__main__':
    server().start()
