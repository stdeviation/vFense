class vFensePlugins():
    RV_PLUGIN = 'rv'
    CORE_PLUGIN = 'core'
    RA_PLUGIN = 'ra'
    MONITORING_PLUGIN = 'monitoring'
    VULNERABILITY = 'vulnerability'
    PATCHING = 'patching'
    VALID_PLUGINS = (
        RV_PLUGIN, CORE_PLUGIN, RA_PLUGIN, MONITORING_PLUGIN,
        VULNERABILITY, PATCHING
    )


class OperationErrors():
    EXPIRED = 'Operation expired'
    PICKEDUP = 'Operation was picked up by the agent'
    PENDINGPICKUP = 'Operation has not been picked up by the agent'
    COMPLETED = 'Operation was completed successfully'
    FAILED = 'Operation completed with errors'


class AdminActions():
    CREATE = 'create'
    UPDATE = 'update'
    REMOVE = 'remove'
    VALID_ACTIONS = (CREATE, UPDATE, REMOVE)


class vFenseObjects():
    AGENT = 'agent'
    TAG = 'tag'
    SCHEDULE = 'schedule'
    USER = 'user'
    GROUP = 'group'
    CUSTOMER = 'customer'
    VALID_OBJECTS = (
        AGENT, TAG, SCHEDULE,
        USER, GROUP, CUSTOMER
    )


class BaseURIs():
    LISTENER = 'rvl/v1'
    API = 'api/v1'


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
    INSTALL_AGENT_APPS = 'rv/results/install/apps/agent'
    UNINSTALL = 'rv/results/uninstall'
    UNINSTALL_AGENT = 'rv/results/uninstall'
    REBOOT = 'core/results/reboot'
    SHUTDOWN = 'core/results/shutdown'
    REFRESH_APPS = 'rv/updatesapplications'
    START_UP = 'core/results/startup'
    CHECK_IN = 'core/checkin'
    MONITOR_DATA = 'monitoring/monitordata'
    REFRESH_RESPONSE_URIS = 'core/uris/response'


class AgentOperations():
    NEWAGENT = 'new_agent'
    REFRESH_APPS = 'updatesapplications'
    CHECK_IN = 'check_in'
    MONITOR_DATA = 'monitor_data'
    START_UP = 'startup'
    INSTALL_OS_APPS = 'install_os_apps'
    INSTALL_CUSTOM_APPS = 'install_custom_apps'
    INSTALL_SUPPORTED_APPS = 'install_supported_apps'
    INSTALL_AGENT_APPS = 'install_agent_apps'
    UNINSTALL = 'uninstall'
    UNINSTALL_AGENT = 'uninstall_agent'
    REBOOT = 'reboot'
    SHUTDOWN = 'shutdown'
    RA = 'ra'
    REFRESH_RESPONSE_URIS = 'refresh_response_uris'

    OPERATIONS = (
        NEWAGENT, REFRESH_APPS, CHECK_IN, MONITOR_DATA,
        START_UP, INSTALL_OS_APPS, INSTALL_CUSTOM_APPS,
        INSTALL_SUPPORTED_APPS, INSTALL_AGENT_APPS,
        UNINSTALL, UNINSTALL_AGENT,
        REBOOT, SHUTDOWN, RA, REFRESH_RESPONSE_URIS
    )
    

