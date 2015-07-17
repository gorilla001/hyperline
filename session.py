__author__ = 'nmg'

__all__ = ['Session']

import asyncio
from decorator import singleton


@singleton
class SessionManager(object):
    """
    Manage session objects.

    The session object will be deleted automatic after session is timed-out.
    """
    def __init__(self):
        self.sessions = {}
        self.interval = 2.0
        self._loop = asyncio.get_event_loop()
        self.looping_call()

    def looping_call(self):
        self._loop.call_later(self.interval, self.check_expire)

    def register(self, client, session):
        self.sessions[client] = session

    def unregister(self, client):
        del self.sessions[client]

    def get(self, client):
        # Get transport associated by client if exists.
        if client not in self.sessions:
            return None

        return self.sessions[client].transport

    def check_expire(self):
        print(self.sessions)
        self.looping_call()

    def __repr__(self):
        return "{}".format(self.sessions)

    __str__ = __repr__

class Session(object):
    """
    Session object is used for managing connection(transport). After `timeout` seconds, and
    has no `touch` called, the connection will be closed.
    """

    def __init__(self, client, transport, timeout=5):
        self.client = client
        self.transport = transport
        self.timeout = timeout
        self._loop = asyncio.get_event_loop()
        self._timeout_handler = None
        self.manager = SessionManager()
        self.add_timeout()

    def add_timeout(self):
        self._timeout_handler = self._loop.call_later(self.timeout, self.close_connection)

    def close_connection(self):
        # Close connection
        asyncio.async(self.transport.close())

        # Delete self from SessionManager
        self.explode()

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

    def explode(self):
        """
        When session explode, it will delete itself from SessionManager.
        """
        self.manager.unregister(self.client)


if __name__ == '__main__':
    Session()
