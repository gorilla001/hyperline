__author__ = 'nmg'

__all__ = ['Session']

import asyncio
import json
# import functools
from struct import pack
from meta import MetaSession

# class Timer(object):
#     """
#     Session Timer
#     """
#     def __init__(self, timeout):
#         self.timeout = timeout
#         self._loop = asyncio.get_event_loop()
#         self._timeout_handler = None
#
#     def add_handler(self, handler):
#         pass
#
#     def start(self):
#         self._timeout_handler = self._loop.call_later(self.timeout, self.close_connection)
#
#     def cancel(self):
#         self._timeout_handler.cancel()
#         self._timeout_handler = None
class SessionManager(metaclass=MetaSession):
    """
    Manage session objects.

    The session object will be deleted automatic after session is timed-out.

    SessionManager used for two purpose, one is storing sessions, and the other is
    manage sessions.

    Sessions will be stored in a dictionary as 'client' for key, and 'connection' for value.

    SessionManager do the following things:
    . add(update) or delete session
    . manage session life cycle
    . handler session expired
    . send notify

    """
    def __init__(self, timeout=1800):
        # sessions contains client-connection pairs.
        self.sessions = {}  # for normal user

        self.custom_services = {}  # for custom services

        self._loop = asyncio.get_event_loop()
        self.interval = 2.0
        self.timeout = timeout
        self.looping_call()

    def looping_call(self):
        self._loop.call_later(self.interval, self.check_expire)

    def add_session(self, client, session):
        """
        Add session in SessionManager
        """
        self.sessions[client] = session

    def pop_session(self, client):
        """
        Delete session from SessionManager
        """
        self.sessions.pop(client)

    def get_session(self, client):
        # Get session associated by client if exists.

        return self.sessions.get(client)

    def add_custom_service(self, client):
        pass

    # def add_timeout(self, client):
    #     """
    #     Add timeout for session associated by client.
    #     """
    #     session = self.get_session(client)
    #     session._timeout_handler = self._loop.call_later(
    #         self.timeout, functools.partial(self.timeout_handler, client))

    # def cancel_timeout(self, client):
    #     """
    #     Cancel timeout for session associated by client.
    #     """
    #     session = self.get_session(client)
    #     session._timeout_handler.cancel()
    #     session._timeout_handler = None
    #
    # def touch(self, client):
    #     """
    #     Cancel timeout handler and re-add handler. The client will call `touch` for
    #     next timeout.
    #
    #     Every `heartbeat` message received or every `chat` message received, the session
    #     will be touched.
    #     """
    #     self.cancel_timeout(client)
    #     self.add_timeout(client)
    #
    # def timeout_handler(self, client):
    #     # Close connection
    #     self.get_session(client).close()
    #
    #     # Delete self from SessionManager
    #     self.explode(client)

    # def explode(self, client):
    #     """
    #     Delete session from SessionManager
    #     """
    #     self.pop_session(client)
    def send_notify(self, client, online=True):
        """
        Send online or offline messages to all clients include me.

        Message body should like this:

            {'type': 'notify', 'content': notify-types}

        The notify types have the following values:

           0 - online
           1 - offline
           (continue...)
        """
        for client in self.sessions.keys():
            pass

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

    def __init__(self, timeout=1800):
        self.client = None
        self.transport = None
        self.timeout = timeout
        self._loop = asyncio.get_event_loop()
        self._timeout_handler = None
        self.manager = SessionManager()

    def add_timeout(self, timeout=None):
        if timeout is None:
            timeout = self.timeout

        self._timeout_handler = self._loop.call_later(timeout, self.timeout_handler)

    def timeout_handler(self):
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
        self.manager.pop_session(self.client)

    def close(self):
        """
        Close Session connection
        """
        asyncio.async(self.transport.close())
        self.transport = None

    @asyncio.coroutine
    def send(self, msg):
        yield from self.transport.send(json.dumps(msg))

    def write(self, msg):
        self.transport.write(pack("!I", len(msg)) + bytes(msg, encoding='utf-8'))


if __name__ == '__main__':
    pass
