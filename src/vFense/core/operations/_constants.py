
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


class AgentOperations():
    NEW_AGENT = 'new_agent'
    NEW_TOKEN = 'new_token'
    REFRESH_APPS = 'updatesapplications'
    APPS_REFRESH = 'apps_refresh'
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


class AuthenticationOperations():
    LOGIN = 'login'
    LOGOUT = 'logout'


class V1ListenerURIs():
    LOGIN = (AuthenticationOperations.LOGIN, 'rvl/login', 'POST', False)
    LOGOUT = (AuthenticationOperations.LOGOUT,'rvl/logout', 'GET', False)
    NEWAGENT = (AgentOperations.NEW_AGENT, 'core/newagent', 'POST', False)
    INSTALL_OS_APPS = (
        AgentOperations.INSTALL_OS_APPS, 'rv/results/install/apps/', 'PUT',
        True
    )
    INSTALL_CUSTOM_APPS = (
        AgentOperations.INSTALL_CUSTOM_APPS, 'rv/results/install/apps/custom',
        'PUT', True
    )
    INSTALL_SUPPORTED_APPS = (
        AgentOperations.INSTALL_SUPPORTED_APPS,
        'rv/results/install/apps/supported', 'PUT', True
    )
    INSTALL_AGENT_UPDATE = (
        AgentOperations.INSTALL_AGENT_UPDATE, 'rv/results/install/apps/agent',
        'PUT', True
    )
    UNINSTALL = (
        AgentOperations.UNINSTALL, 'rv/results/uninstall', 'PUT', True
    )
    UNINSTALL_AGENT = (
        AgentOperations.UNINSTALL_AGENT, 'rv/results/uninstall', 'PUT', True
    )
    REBOOT = (
        AgentOperations.REBOOT, 'core/results/reboot', 'PUT', True
    )
    SHUTDOWN = (
        AgentOperations.SHUTDOWN, 'core/results/shutdown', 'PUT', True
    )
    REFRESH_APPS = (
        AgentOperations.REFRESH_APPS, 'rv/updatesapplications', 'PUT', True
    )
    AVAILABLE_AGENT_UPDATE = (
        AgentOperations.AVAILABLE_AGENT_UPDATE, 'rv/available_agent_update',
        'PUT', False
    )
    START_UP = (AgentOperations.START_UP, 'core/results/startup', 'PUT', True)
    CHECK_IN = (AgentOperations.CHECK_IN, 'core/checkin', 'GET', True)
    MONITOR_DATA = (
        AgentOperations.MONITOR_DATA, 'monitoring/monitordata', 'POST', True
    )
    REFRESH_RESPONSE_URIS = (
        AgentOperations.REFRESH_RESPONSE_URIS, 'core/uris/response', 'GET',
        False
    )

    @staticmethod
    def get_valid_listener_uris():
        valid_uris = (
            map(
                lambda x:
                getattr(V1ListenerURIs, x), dir(V1ListenerURIs)[:-3]
            )
        )
        return valid_uris

class V2ListenerURIs():
    NEWAGENT = (AgentOperations.NEW_AGENT, 'core/newagent', 'POST', False)
    INSTALL_OS_APPS = (
        AgentOperations.INSTALL_OS_APPS, 'results/apps/os/install', 'PUT',
        True
    )
    INSTALL_CUSTOM_APPS = (
        AgentOperations.INSTALL_CUSTOM_APPS, 'results/apps/install/custom',
        'PUT', True
    )
    INSTALL_SUPPORTED_APPS = (
        AgentOperations.INSTALL_SUPPORTED_APPS,
        'results/apps/install/supported', 'PUT', True
    )
    INSTALL_AGENT_UPDATE = (
        AgentOperations.INSTALL_AGENT_UPDATE, 'apps/results/apps/agent',
        'PUT', True
    )
    UNINSTALL = (
        AgentOperations.UNINSTALL, 'apps/results/uninstall', 'PUT', True
    )
    UNINSTALL_AGENT = (
        AgentOperations.UNINSTALL_AGENT, 'apps/results/uninstall', 'PUT', True
    )
    REBOOT = (AgentOperations.REBOOT, 'core/results/reboot', 'PUT', True)
    SHUTDOWN = (
        AgentOperations.SHUTDOWN, 'core/results/shutdown', 'PUT', True
    )
    NEW_TOKEN = (
        AgentOperations.NEW_TOKEN, 'core/results/newtoken', 'PUT', True
    )
    REFRESH_APPS = (
        AgentOperations.APPS_REFRESH, 'apps/apps_refresh', 'PUT', True
    )
    AVAILABLE_AGENT_UPDATE = (
        AgentOperations.AVAILABLE_AGENT_UPDATE, 'apps/available_agent_update',
        'PUT', False
    )
    START_UP = (AgentOperations.START_UP, 'core/results/startup', 'PUT', True)
    CHECK_IN = (AgentOperations.CHECK_IN, 'core/checkin', 'GET', True)
    MONITOR_DATA = (
        AgentOperations.MONITOR_DATA, 'monitoring/monitordata', 'POST', True
    )
    REFRESH_RESPONSE_URIS = (
        AgentOperations.REFRESH_RESPONSE_URIS, 'core/uris/response',
        'GET', False
    )

    @staticmethod
    def get_valid_listener_uris():
        valid_uris = (
            map(
                lambda x:
                getattr(V2ListenerURIs, x), dir(V2ListenerURIs)[:-3]
            )
        )
        return valid_uris
