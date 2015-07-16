__author__ = 'nmg'

from hyperline import HyperLine, HyperLineServer

if __name__ == '__main__':
    server = HyperLineServer(protocol_factory=HyperLine,
                             host='localhost',
                             port=2222,
                             ws_host='localhost',
                             ws_port=9000)
    server.start()
