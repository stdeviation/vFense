class AdminOperationDefaults():
    ERRORS = []
    IDS_REMOVED = []
    IDS_UPDATED = []
    IDS_CREATED = []
    OBJECT_DATA = {}
    STATUS_MESSAGE = ''
    GENERIC_STATUS_CODE = None
    VFENSE_STATUS_CODE = None

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
    VALID_ACTIONS = (
        ADD_AGENT_TO_TAG, ADD_USERS_TO_VIEW, ADD_USER_TO_GROUP,
        ADD_USER_TO_VIEW, ADD_VIEW_TO_GROUP, CREATE_GROUP,
        CREATE_NOTIFICATION, CREATE_TAG, CREATE_USER, CREATE_VIEW,
        EDIT_AGENT_DISPLAY_NAME, EDIT_AGENT_QUEUE_TTL, EDIT_CPU_THROTTLE,
        EDIT_DEFAULT_VIEW, EDIT_DOWNLOAD_URL, EDIT_GROUP_EMAIL,
        EDIT_GROUP_PERMISSIONS, EDIT_LOG_SETTINGS, EDIT_NET_THROTTLE,
        EDIT_NOTIFICATION, EDIT_SERVER_QUEUE_TTL, EDIT_USER_EMAIL,
        EDIT_USER_PASSWORD, REMOVE_AGENT_FROM_TAG, REMOVE_GROUP,
        REMOVE_NOTIFICATION, REMOVE_TAG, REMOVE_USER, REMOVE_USERS_FROM_VIEW,
        REMOVE_USER_FROM_GROUP, REMOVE_USER_FROM_VIEW, REMOVE_VIEW,
        REMOVE_VIEW_FROM_GROUP
    )


