__author__ = 'nmg'

from pulsar.apps.socket import SocketServer
from protocol import HyperLineConnection
from functools import partial



class HyperLineServer(SocketServer):

    # Override the `SocketServer`'s `protocol_factory` method to use our own `HyperLineConnection`.
    # If this method does not exist, the default `pulsar.Connection` will be used.

    def protocol_factory(self):
        return partial(HyperLineConnection, self.cfg.callable)

# import eventlet
# from eventlet.green import socket
#
# class EventletServer(object):
#     def __init__(self, handler, host, port):
#         self.handler = handler
#         self.host = host
#         self.port = port
#
#     def start(self):
#         try:
#             server = eventlet.listen((self.host, self.port))
#             while True:
#                 connection, address = server.accept()
#                 writer = connection.makefile('w')
#                 reader = connection.makefile('r')
#
#                 eventlet.spawn_n(self.handler,
#                                  writer,
#                                  reader)
#
#         except (KeyboardInterrupt, SystemExit):
#             print("ChatServer exiting.")
#
# def handler(writer, reader):
#     while True:
#         print(reader.read())
#
#
# # if __name__ == '__main__':
# #     server = EventletServer(handler=handler,
# #                             host='localhost',
# #                             port=8090)
# #     print('start server...')
# #     server.start()
#
# def myhandler(sock, addr):
#     print(sock.recv(4096))
#     #print(sock.__dict__)
#
# eventlet.serve(eventlet.listen(('127.0.0.1', 9999)), myhandler)