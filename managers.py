__author__ = 'nmg'

# from meta import MetaSession
from meta import MetaConnection

class ConnectionManager(metaclass=MetaConnection):
    """
    Connection manager for managing all other managers
    """
    @staticmethod
    def add_connection(connection):
        """
        Add connection in connection manager according connection.path attribute
        """
        if connection.path == '/service':
            CustomServiceConnectionManager().add_connection(connection)
        if connection.path == '/':
            NormalUserConnectionManager().add_connection(connection)

class Manager(metaclass=MetaConnection):
    """
    Interface class for connection managers
    """
    # def __init__(self):
    #     self.connections = {}

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

class NormalUserConnectionManager(Manager):
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
        self.connections.pop(user_id)

    def get_connection(self, user_id):
        # Get session associated by client if exists.

        return self.connection.get(user_id)

class CustomServiceConnectionManager(Manager):
    """
    Custom service session manager
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
        self.connections.pop(user_id)

    def get_connection(self, user_id):
        # Get session associated by client if exists.

        return self.connection.get(user_id)

    def get_connections(self):
        # Get all connections
        return list(self.connections.values())

if __name__ == '__main__':
    pass

