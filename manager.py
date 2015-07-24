__author__ = 'nmg'

from meta import MetaSession

class Manager(metaclass=MetaSession):
    """
    Base class for managers
    """
    def add_session(self, session):
        try:
            _session_manager = self._session_managers[session.role]
            _session_manager.add_session(session)
        except KeyError:
            pass

    def pop_session(self, client):
        try:
            _session_manager = self._session_managers[session.role]
            _session_manager.pop_session(client)
        except KeyError:
            pass

    def get_session(self, client):
        try:
            _session_manager = self._session_managers[session.role]
            _session_manager.get_session(client)
        except KeyError:
            pass

class NormalUserSessionManager(Manager):
    """
    Normal user session manager. normal users means external user.
    """
    __type__ = '0'

    def __init__(self):
        self.sessions = {}

    def add_session(self, session):
        """
        Add session in SessionManager
        """
        self.sessions[session.client] = session

    def pop_session(self, client):
        """
        Delete session from SessionManager
        """
        self.sessions.pop(client)

    def get_session(self, client):
        # Get session associated by client if exists.

        return self.sessions.get(client)

class CustomServiceSessionManager(Manager):
    """
    Custom service session manager
    """
    __type__ = '1'

    def __init__(self):
        self.sessions = {}

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

class SportManSessionManager(Manager):
    """
    Sport man session manager
    """
    def __init__(self):
        self.sessions = {}

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

class SessionManagerFactory(object):
    @classmethod
    def create_manager(cls, user_type):
        pass

if __name__ == '__main__':

    cs = CustomServiceSessionManager()
    print(id(cs.sessions))

    sm = SportManSessionManager()
    print(id(sm.sessions))

