__author__ = 'nmg'

from session import Session
from struct import pack
from impl_kombu import Connection

#from twisted.internet.defer import Deferred
from twisted.internet.threads import deferToThread
# session = Session()
# Message handler for handling message according to message type
# 0 - register
# 1 - text-chat
# 2 - voice
# 3 - picture
# -1 - unregister
# msg_handler = {
#     '0': 'register',
#     '1': 'chat',
#     '-1': 'unregister',
#     '255': 'heartbeat',
# }

import time
import asyncio

class MetaHandler(type):
    """Metaclass for messagehandler"""
    def __init__(cls, name, bases, _dict):
        try:
            cls._msg_handlers[cls.__msgtype__] = cls
        except AttributeError:
            cls._msg_handlers = {}

class MessageHandler(metaclass=MetaHandler):
    # def __init__(self):
    #     self._session = Session()  # Singleton
    #_session = Session()
    def __init__(self):
        self.rabbit_host = '192.168.99.100'
        self.rabbit_port = 32768
        self.rabbit_virtual_host = '/'
        self.rabbit_userid = 'guest'
        self.rabbit_password = 'guest'

    def __call__(self, msg):
        try:
            _handler = self._msg_handlers[msg['type']]
            return _handler().handler(msg)
        except KeyError:
            raise
            #return ErrorHandler().handler(msg)

        # for _handler in self._msg_handlers:
        #     if hasattr(_handler, '__msgtype__'):
        #         if _handler.__msgtype__ == msg['type']:
        #             return _handler().handler(msg)

        # return ErrorHandler().handler(msg)

class Register(MessageHandler):
    """
    Registry handler for handling clients registry.
    """
    __msgtype__ = 'register'

    def handler(self, msg):
    # def handler(self, msg):
    #     """Register user in global session"""
    #     self._session.register(msg['sender'], msg['transport'])
    #
    #     # Get offline msgs from db
    #     offline_msgs = self.get_offline_msg(msg)
    #
    #     # Send offline msgs
    #     self.send_offline_msg(offline_msgs)
    #     #self.get_offline_msg(msg)
    #
    # @asyncio.coroutine
    # def get_offline_msg(self, msg):
    #
    #     # Get offline msg from mongodb. This will be block
    #     #result = yield from self.get_offline_msg_from_db(msg['sender'])
    #     result = self.get_offline_msg_from_db(msg['sender'])
    #
    #     return result
    #
    # def send_offline_msg(self, msg):
    #
    #     print(msg)
    #
    # @staticmethod
    # def get_offline_msg_from_db(user):
    #     time.sleep(5.0)
    #     return "message"
        with Connection(rabbit_host=self.rabbit_host,
                        rabbit_port=self.rabbit_port,
                        rabbit_virtual_host=self.rabbit_virtual_host,
                        rabbit_userid=self.rabbit_userid,
                        rabbit_password=self.rabbit_password) as connection:
            connection.create_consumer(msg['sender'], msg['connection'])

            for consumer in connection.consumers:
                consumer.consume()
            while True:
                connection.drain_events()

class SendTextMsg(MessageHandler):
    """
    Send message to others.
    """
    __msgtype__ = 'text'  # Text message

    def handler(self, msg):
        """
        Send message to receiver if receiver is online, and
        save message to mongodb. Otherwise save
        message to mongodb as offline message.
        :param msg:
        :return: None
        """
    #     transport = self._session.get(msg['receiver'], None)
    #     if transport:
    #         # Pack message as length-prifixed and send to receiver.
    #         transport.write(pack("!I", len(msg)) + msg)
    #         return self.save_message(msg)
    #
    #     return self.save_message(msg, online=False)
    #
    # def save_message(self, online=True):
    #     pass
        log = msg.pop('logger')
        log.info("Delivering msg to queue...[topic] {}".format(msg['receiver']))

        with Connection(rabbit_host=self.rabbit_host,
                        rabbit_port=self.rabbit_port,
                        rabbit_virtual_host=self.rabbit_virtual_host,
                        rabbit_userid=self.rabbit_userid,
                        rabbit_password=self.rabbit_password) as connection:

            del msg['connection']
            connection.topic_send(msg['receiver'], msg)

class Unregister(MessageHandler):
    """Unregister user from global session"""
    __msgtype__ = 'unregister'

    def handler(self, msg):
        """Unregister user record from global session"""
        del self.session[msg['sender']]

class ErrorHandler(MessageHandler):
    """
    Unknown message type
    """
    __msgtype__ = 'unknown'

    def handler(self, msg):
        print("Unknown message type: {}".format(msg))


handler = MessageHandler()
