__author__ = 'nmg'


class Manager(object):
    """
    Base class for managers
    """
    def __init__(self, session):
        self.sessions = session

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

class CustomServiceSessionManager(Manager):
    """
    Custom service session manager
    """
    def __init__(self):
        self.sessions = {}

        super().__init__(self.sessions)

class SportManSessionManager(Manager):
    """
    Sport man session manager
    """
    def __init__(self):
        self.sessions = {}

        super().__init__(self.sessions)


class SessionManagerFactory(object):
    @classmethod
    def create_manager(cls, user_type):
        pass

if __name__ == '__main__':

    cs = CustomServiceSessionManager()
    print(id(cs.sessions))

    sm = SportManSessionManager()
    print(id(sm.sessions))

