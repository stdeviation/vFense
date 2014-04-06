

class ValidOperations():
    NEWAGENT = 'newagent'
    APPS_REFRESH = 'updatesapplications'
    CHECKIN = 'checkin'
    STARTUP = 'startup'
    INSTALL_OS_APPS = 'install_os_apps'
    INSTALL_CUSTOM_APPS = 'install_custom_apps'
    INSTALL_SUPPORTED_APPS = 'install_agent_apps'
    INSTALL_AGENT_APPS = 'install_agent_apps'
    UNINSTALL_OS_APPS = 'uninstall_os_apps'
    UNINSTALL_CUSTOM_APPS = 'uninstall_custom_apps'
    UNINSTALL_SUPPORTED_APPS = 'uninstall_agent_apps'
    UNINSTALL_AGENT_APPS = 'uninstall_agent_apps'
    REBOOT = 'reboot'
    SHUTDOWN = 'shutdown'
    RA = 'ra'
    OPERATIONS = (
        NEWAGENT, APPS_REFRESH, CHECKIN,
        STARTUP, INSTALL_OS_APPS, INSTALL_CUSTOM_APPS,
        INSTALL_SUPPORTED_APPS, INSTALL_AGENT_APPS,
        UNINSTALL_OS_APPS, UNINSTALL_CUSTOM_APPS,
        UNINSTALL_SUPPORTED_APPS, UNINSTALL_AGENT_APPS,
        REBOOT, SHUTDOWN, RA
    )
