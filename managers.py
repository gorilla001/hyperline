__author__ = 'nmg'

# from meta import MetaSession
from meta import MetaConnection
import asyncio

class ConnectionManagerProxy(metaclass=MetaConnection):
    """
    Connection manager proxy.
    """
    def __init__(self, connection):
        if connection.path == '/':
            self._connection_manager = NormalUserConnectionManager()
        if connection.path == '/service':
            self._connection_manager = CustomServiceConnectionManager()

    def __getattr__(self, method):
        return getattr(self._connection_manager, method)


class Manager(metaclass=MetaConnection):
    """
    Interface class for connection managers
    """
    # def __init__(self):
    #     self.connections = {}
    # _connections = {}

    def add_connection(self, connection):
        """
        Add user-connection pairs in connection manager
        """
        raise NotImplementedError()

    def pop_connection(self, user_id):
        """
        Delete user-connection pair from connection manager
        """
        raise NotImplementedError()

    def get_connection(self, user_id):
        """
        Get connection associated by user_id from conneciton manager
        """
        raise NotImplementedError()

class NormalUserConnectionManager(object):
    """
    Normal user session manager. normal users means external user.
    """
    def __init__(self):
        self.connections = {}

    def add_connection(self, connection):
        """
        Add session in SessionManager
        """
        self.connections[connection.uid] = connection

    def pop_connection(self, user_id):
        """
        Delete session from SessionManager
        """
        try:
            self.connections.pop(user_id)
        except KeyError:
            pass

    def get_connection(self, user_id):
        # Get session associated by client if exists.

        return self.connections.get(user_id)

class CustomServiceConnectionManager(Manager):
    """
    Custom service session manager
    """
    # _connections = {}
    # def __init__(self):
    #     try:
    #         self.connections = self.connections.copy()
    #     except AttributeError:
    #         self.connections = {}
    def __init__(self):
        self._connections = {}
        self._loop = asyncio.get_event_loop()
        self.looping_call()

    def add_connection(self, connection):
        """
        Add session in SessionManager
        """
        self._connections[connection.uid] = connection

    def pop_connection(self, user_id):
        """
        Delete session from SessionManager
        """
        try:
            self._connections.pop(user_id)
        except KeyError:
            pass

    def get_connection(self, user_id):
        # Get session associated by client if exists.

        return self._connections.get(user_id)

    def get_connections(self):
        # Get all connections
        return list(self._connections.values())

    def looping_call(self):
        self._loop.call_later(1.0, self.check_expire)

    def check_expire(self):
        print(self._connections)
        self.looping_call()

if __name__ == '__main__':
    from collections import namedtuple
    Connection = namedtuple('Connection', ['path'])
    _connection = Connection('/service')
    manager_proxy = ConnectionManagerProxy(_connection)
    print(manager_proxy.add_connection)
    manager_proxy.add_connection()

