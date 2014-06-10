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
    CREATE_VIEW = 'create view'
    REMOVE_VIEW = 'remove view'
    ADD_USERS_TO_VIEW = 'add users to view'
    REMOVE_USERS_FROM_VIEW = 'remove users from view'
    EDIT_CPU_THROTTLE = 'edit cpu throttle'
    EDIT_NET_THROTTLE = 'edit net throttle'
    EDIT_SERVER_QUEUE_TTL = 'edit server queue ttl'
    EDIT_AGENT_QUEUE_TTL = 'edit agent queue ttl'
    EDIT_DOWNLOAD_URL = 'edit download url'
    CREATE_GROUP = 'create group'
    REMOVE_GROUP = 'remove group'
    ADD_VIEW_TO_GROUP = 'add view to group'
    REMOVE_VIEW_FROM_GROUP = 'remove view from group'
    EDIT_GROUP_EMAIL = 'edit group email'
    EDIT_GROUP_PERMISSIONS = 'edit group permissions'
    CREATE_USER = 'create user'
    REMOVE_USER = 'remove user'
    ADD_USER_TO_VIEW = 'add user to views'
    REMOVE_USER_FROM_VIEW = 'remove user from view'
    ADD_USER_TO_GROUP = 'add user to group'
    REMOVE_USER_FROM_GROUP = 'remove user from group'
    EDIT_USER_PASSWORD = 'edit user password'
    EDIT_USER_EMAIL = 'edit user email'
    EDIT_DEFAULT_VIEW = 'edit default user view'
    CREATE_TAG = 'create tag'
    REMOVE_TAG = 'remove tag'
    ADD_AGENT_TO_TAG = 'add agent to tag'
    REMOVE_AGENT_FROM_TAG = 'remove agent from tag'
    EDIT_LOG_SETTINGS = 'edit log settings'
    CREATE_NOTIFICATION = 'create notification'
    EDIT_NOTIFICATION = 'edit notification'
    REMOVE_NOTIFICATION = 'remove notification'
    EDIT_AGENT_DISPLAY_NAME = 'edit agent display name'
    VALID_ACTIONS = (CREATE, UPDATE, REMOVE)


class vFenseObjects():
    AGENT = 'agent'
    TAG = 'tag'
    SCHEDULE = 'schedule'
    USER = 'user'
    GROUP = 'group'
    VIEW = 'view'
    VALID_OBJECTS = (
        AGENT, TAG, SCHEDULE,
        USER, GROUP, VIEW
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


class AgentOperations():
    NEW_AGENT = 'new_agent'
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

    OPERATIONS = (
        NEW_AGENT, REFRESH_APPS, CHECK_IN, MONITOR_DATA,
        START_UP, INSTALL_OS_APPS, INSTALL_CUSTOM_APPS,
        INSTALL_SUPPORTED_APPS, INSTALL_AGENT_UPDATE,
        UNINSTALL, UNINSTALL_AGENT,
        REBOOT, SHUTDOWN, RA, REFRESH_RESPONSE_URIS
    )
