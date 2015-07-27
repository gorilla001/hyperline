__author__ = 'nmg'

from hyperline import HyperLine, HyperLineServer
import log as logging

if __name__ == '__main__':
    logging.setup()
    server = HyperLineServer(protocol_factory=HyperLine,
                             host='localhost',
                             port=2222,
                             ws_host='0.0.0.0',
                             ws_port=9000)
    server.start()
