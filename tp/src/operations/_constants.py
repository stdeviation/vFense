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
    REBOOT = 'core/results/reboot'
    SHUTDOWN = 'core/results/shutdown'
    APPS_REFRESH = 'core/results/updatesapplications'
    START_UP = 'core/results/startup'
    CHECK_IN = 'core/checkin'
    MONITOR_DATA = 'monitoring/monitordata'
    REFRESH_RESPONSE_URIS = 'core/uris/response'


class ValidOperations():
    NEWAGENT = 'new_agent'
    APPS_REFRESH = 'updatesapplications'
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
        NEWAGENT, APPS_REFRESH, CHECK_IN, MONITOR_DATA,
        START_UP, INSTALL_OS_APPS, INSTALL_CUSTOM_APPS,
        INSTALL_SUPPORTED_APPS, INSTALL_AGENT_APPS,
        UNINSTALL, UNINSTALL_AGENT,
        REBOOT, SHUTDOWN, RA, REFRESH_RESPONSE_URIS
    )
    

