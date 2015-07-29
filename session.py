__author__ = 'nmg'

__all__ = ['Session']

import asyncio
import json
from struct import pack
from meta import MetaSession
import websockets
import log as logging

logger = logging.getLogger(__name__)

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

    def add_session(self, session):
        raise NotImplementedError()

    def pop_session(self, user_id):
        raise NotImplementedError()

    def get_session(self, user_id):
        raise NotImplementedError()


class NormalUserSessionManager(SessionManager):
    """
    Normal user session manager. normal users means external user.
    """
    __type__ = '0'

    def __init__(self):
        self.sessions = {}
        self._loop = asyncio.get_event_loop()
        self.looping_call()

    def add_session(self, session):
        """
        Add session in SessionManager
        """
        self.sessions[session.uid] = session

    def pop_session(self, user_id):
        """
        Delete session from SessionManager
        """
        self.sessions.pop(user_id)

    def get_session(self, user_id):
        # Get session associated by client if exists.

        return self.sessions.get(user_id)

    def looping_call(self):
        self._loop.call_later(5.0, self.check_expire)

    def check_expire(self):
        print(self.sessions)
        self.looping_call()
#
class CustomServiceSessionManager(SessionManager):
    """
    Custom service session manager
    """
    __type__ = '10'

    def __init__(self):
        self.sessions = {}
        self._loop = asyncio.get_event_loop()
        self.looping_call()

    def add_session(self, session):
        """
        Add session in SessionManager
        """
        self.sessions[session.uid] = session

    def pop_session(self, client):
        """
        Delete session from SessionManager
        """
        self.sessions.pop(client)

    def get_session(self, client):
        # Get session associated by client if exists.
        return self.sessions.get(client)

    def get_sessions(self):
        # Get all sessions
        return list(self.sessions.values())

    def looping_call(self):
        self._loop.call_later(5.0, self.check_expire)

    def check_expire(self):
        print(self.sessions)
        self.looping_call()
#
# class SportManSessionManager(SessionManager):
#     """
#     Sport man session manager
#     """
#     def __init__(self):
#         self.sessions = {}
#
#     def add_session(self, client, session):
#         """
#         Add session in SessionManager
#         """
#         self.sessions[client] = session
#
#     def pop_session(self, client):
#         """
#         Delete session from SessionManager
#         """
#         self.sessions.pop(client)
#
#     def get_session(self, client):
#         # Get session associated by client if exists.
#
#         return self.sessions.get(client)

class Session(object):
    """
    Session object is used for managing connection(transport). After `timeout` seconds, and
    has no `touch` called, the connection will be closed.
    """
    __slots__ = ['uid', 'name', 'role', 'path', 'transport', 'associated_sessions',
                 'timeout', '_loop', '_timeout_handler', 'manager']

    def __init__(self, timeout=1800):
        self.uid = None  # client id
        self.name = None  # client name
        self.role = None  # client role
        self.path = None

        self.transport = None  # client connection
        self.associated_sessions = {}

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
        self.manager.pop_session(self)

    def close(self):
        """
        Close Session connection
        """
        asyncio.async(self.transport.close())
        self.transport = None

    @asyncio.coroutine
    def send(self, msg):
        # yield from self.transport.send(json.dumps(msg))
        try:
            yield from self.transport.send(json.dumps(msg.json))
        except websockets.exceptions.InvalidState as exc:
            logger.error("Send message failed! {}".format(exc))

    def write(self, msg):
        self.transport.write(pack("!I", len(msg)) + bytes(msg, encoding='utf-8'))

    @property
    def is_websocket(self):
        return hasattr(self.transport, 'send')


if __name__ == '__main__':
    pass
