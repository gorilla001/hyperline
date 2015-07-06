__author__ = 'nmg'

from pulsar.apps.socket import SocketServer
from protocol import HyperLineConnection
from functools import partial

class HyperLineSocketServer(SocketServer):

    # Override the `SocketServer`'s `protocol_factory` method to use our own `HyperLineConnection`.
    # If this method does not exist, the default `pulsar.Connection` will be used
    def protocol_factory(self):
        return partial(HyperLineConnection, self.cfg.callable)
