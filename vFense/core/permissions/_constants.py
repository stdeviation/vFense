class Permissions():
    READ = 'read'
    ADMINISTRATOR = 'administrator'
    INSTALL = 'install'
    UNINSTALL = 'uninstall'
    REBOOT = 'reboot'
    SHUTDOWN = 'shutdown'
    CREATE_TAG = 'create tag'
    REMOVE_TAG = 'remove tag'
    EDIT_TAG = 'edit tag'
    EDIT_AGENT = 'edit agent'
    ADD_AGENTS_TO_TAG = 'add agents to tag'
    REMOVE_AGENTS_FROM_TAG = 'remove agents from tag'
    CREATE_VIEW = 'create view'
    REMOVE_VIEW = 'remove view'
    NEW_AGENT = 'new agent'
    ASSIGN_NEW_TOKEN = 'assign new token to agents'
    DELETE_AGENT = 'delete agent'
    ADD_AGENTS_TO_VIEW = 'add agents to view'
    REMOVE_AGENTS_FROM_VIEW = 'remove agents from view'
    REMOTE_ASSISTANCE = 'remote assistance'
    EDIT_TIME_ZONE = 'edit time zone'
    HIDE_UNHIDE_APPLICATIONS = 'hide_apps'
    CREATE_NOTIFICATION = 'create notification'
    REMOVE_NOTIFICATION = 'remove notification'
    EDIT_NOTIFICATION = 'edit notification'

    @staticmethod
    def get_valid_permissions():
        valid_permissions = (
            map(lambda x: getattr(Permissions, x), dir(Permissions)[:-3])
        )
        return valid_permissions
