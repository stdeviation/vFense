class vFensePlugins():
    RV_PLUGIN = 'rv'
    CORE_PLUGIN = 'core'
    RA_PLUGIN = 'ra'
    MONITORING_PLUGIN = 'monitoring'
    VULNERABILITY = 'vulnerability'
    PATCHING = 'patching'

    @staticmethod
    def get_valid_plugins():
        valid_plugins = (
            map(
                lambda x:
                getattr(vFensePlugins, x), dir(vFensePlugins)[:-3]
            )
        )
        return valid_plugins


class OperationErrors():
    EXPIRED = 'Operation expired'
    PICKEDUP = 'Operation was picked up by the agent'
    PENDINGPICKUP = 'Operation has not been picked up by the agent'
    COMPLETED = 'Operation was completed successfully'
    FAILED = 'Operation completed with errors'


class vFenseObjects():
    AGENT = 'agent'
    TAG = 'tag'
    SCHEDULE = 'schedule'
    USER = 'user'
    GROUP = 'group'
    VIEW = 'view'

    @staticmethod
    def get_valid_objects():
        valid_objects = (
            map(
                lambda x:
                getattr(vFenseObjects, x), dir(vFenseObjects)[:-3]
            )
        )
        return valid_objects


class BaseURIs():
    LISTENER = 'rvl'
    API = 'api'

class URIVersions():
    V1 = 'v1'
    V2 = 'v2'

    @staticmethod
    def get_valid_versions():
        valid_versions = (
            map(
                lambda x:
                getattr(URIVersions, x), dir(URIVersions)[:-3]
            )
        )
        return valid_versions


class AuthenticationURIs():
    LOGIN = 'rvl/login'
    LOGOUT = 'rvl/logout'


class AuthenticationOperations():
    LOGIN = 'login'
    LOGOUT = 'logout'


class ListenerURIs():
    NEWAGENT = 'core/newagent'
    RA = 'ra/rd/results'

    INSTALL_OS_APPS = 'rv/results/install/apps/os'
    INSTALL_CUSTOM_APPS = 'rv/results/install/apps/custom'
    INSTALL_SUPPORTED_APPS = 'rv/results/install/apps/supported'
    INSTALL_AGENT_UPDATE = 'rv/results/install/apps/agent'
    UNINSTALL = 'rv/results/uninstall'
    UNINSTALL_AGENT = 'rv/results/uninstall'
    REBOOT = 'core/results/reboot'
    SHUTDOWN = 'core/results/shutdown'
    REFRESH_APPS = 'rv/updatesapplications'
    AVAILABLE_AGENT_UPDATE = 'rv/available_agent_update'
    START_UP = 'core/results/startup'
    CHECK_IN = 'core/checkin'
    MONITOR_DATA = 'monitoring/monitordata'
    REFRESH_RESPONSE_URIS = 'core/uris/response'

    @staticmethod
    def get_valid_listener_uris():
        valid_uris = (
            map(
                lambda x:
                getattr(ListenerURIs, x), dir(ListenerURIs)[:-3]
            )
        )
        return valid_uris


class AgentOperations():
    NEW_AGENT = 'new_agent'
    NEW_TOKEN = 'new_token'
    REFRESH_APPS = 'updatesapplications'
    CHECK_IN = 'check_in'
    MONITOR_DATA = 'monitor_data'
    START_UP = 'startup'
    INSTALL_OS_APPS = 'install_os_apps'
    INSTALL_CUSTOM_APPS = 'install_custom_apps'
    INSTALL_SUPPORTED_APPS = 'install_supported_apps'
    INSTALL_AGENT_UPDATE = 'install_agent_update'
    UNINSTALL = 'uninstall'
    UNINSTALL_AGENT = 'uninstall_agent'
    REBOOT = 'reboot'
    SHUTDOWN = 'shutdown'
    RA = 'ra'
    REFRESH_RESPONSE_URIS = 'refresh_response_uris'
    AVAILABLE_AGENT_UPDATE = 'available_agent_update'

    @staticmethod
    def get_valid_operations():
        valid_operations = (
            map(
                lambda x:
                getattr(AgentOperations, x), dir(AgentOperations)[:-3]
            )
        )
        return valid_operations
