__author__ = 'nmg'

__all__ = ['Session']

import asyncio

class SessionManager(object):
    """
    Manage session objects
    """
    def __init__(self):
        self.sessions = {}

    def register(self, client, session):
        self.sessions[client] = session

    def unregister(self, client):
        del self.sessions[client]

    def get(self, client):
        # Get transport associated by client if exists.
        if client not in self.sessions:
            return None

        return self.sessions[client].transport

    def expire(self):
        pass

    def __repr__(self):
        return "{}".format(self.sessions)

    __str__ = __repr__

class Session(object):
    """
    Session object is used for managing connection(transport). After `timeout` seconds, and
    has no `touch` called, the connection will be closed.
    """

    def __init__(self, transport, timeout=5):
        self.transport = transport
        self.timeout = timeout
        self._loop = asyncio.get_event_loop()
        self._timeout_handler = None
        self.add_timeout()

    def add_timeout(self):
        self._timeout_handler = self._loop.call_later(self.timeout, self.close_connection)

    def close_connection(self):
        print('timeout closed')
        asyncio.async(self.transport.close())

    def cancel_timeout(self):
        """
        Cancel timeout handler. So the close_connection action will not be acted.
        """
        self._timeout_handler.cancel()
        self._timeout_handler = None

    def touch(self):
        """
        Cancel timeout handler and re-add handler. The client will call `touch` for
        next timeout.

        Every `heartbeat` message received or every `chat` message received, the session
        will be touched.
        """
        self.cancel_timeout()
        self.add_timeout()


if __name__ == '__main__':
    Session()
