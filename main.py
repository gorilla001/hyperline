__author__ = 'nmg'

from hyperline import HyperLine, HyperLineServer
import log as logging
import constant as cfg

if __name__ == '__main__':
    logging.setup()
    server = HyperLineServer(protocol_factory=HyperLine,
                             host=cfg.host,
                             port=cfg.port,
                             ws_host=cfg.ws_host,
                             ws_port=cfg.ws_port)
    server.start()
