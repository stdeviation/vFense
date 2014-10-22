class DefaultUsers():
    GLOBAL_ADMIN = 'global_admin'
    GLOBAL_AGENT = 'global_agent'
    ADMIN = 'admin'
    AGENT = 'agent_api'

class UserDefaults():
    @staticmethod
    def full_name():
        return None

    @staticmethod
    def email():
        return None

    @staticmethod
    def enabled():
        return True

    @staticmethod
    def is_global():
        return False

    @staticmethod
    def views():
        return list()
