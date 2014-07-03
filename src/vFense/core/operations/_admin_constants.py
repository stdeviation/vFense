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
    ADD_USERS_TO_VIEW = 'add users to view'
    ADD_USER_TO_VIEW = 'add user to views'
    ADD_VIEW_TO_GROUP = 'add view to group'
    ADD_AGENT_TO_VIEWS = 'add agent to views'
    ADD_AGENTS_TO_VIEWS = 'add agents to views'
    ###CREATE
    NEW_AGENT = 'new agent'
    CREATE_USER = 'create user'
    CREATE_GROUP = 'create group'
    CREATE_VIEW = 'create view'
    CREATE_TAG = 'create tag'
    CREATE_NOTIFICATION = 'create notification'
    ###ADD TO
    ADD_USER_TO_GROUP = 'add user to group'
    ADD_USERS_TO_GROUP = 'add user to group'
    ADD_GROUP_TO_USER = 'add group to user'
    ADD_GROUP_TO_VIEW = 'add group to view'
    ADD_GROUPS_TO_USER = 'add groups to user'
    ADD_GROUPS_TO_VIEW = 'add groups to view'
    ADD_VIEW_TO_GROUP = 'add view to group'
    ADD_VIEWS_TO_GROUP = 'add views to group'
    ADD_VIEWS_TO_AGENT = 'add views to agent'
    ADD_VIEWS_TO_AGENTS = 'add views to agents'
    ADD_AGENT_TO_TAG = 'add agent to tag'
    ###REMOVE
    REMOVE_GROUP = 'remove group'
    REMOVE_GROUPS = 'remove groups'
    REMOVE_VIEW = 'remove view'
    REMOVE_VIEWS = 'remove views'
    REMOVE_USER = 'remove user'
    REMOVE_USERS = 'remove users'
    REMOVE_NOTIFICATION = 'remove notification'
    REMOVE_TAG = 'remove tag'
    REMOVE_TAGS = 'remove tags'
    REMOVE_AGENT = 'remove agent'
    REMOVE_AGENTS = 'remove agents'
    ###REMOVE FROM
    REMOVE_VIEW_FROM_GROUP = 'remove view from group'
    REMOVE_VIEWS_FROM_GROUP = 'remove views from group'
    REMOVE_VIEWS_FROM_AGENT = 'remove views from agent'
    REMOVE_VIEWS_FROM_AGENTS = 'remove views from agents'
    REMOVE_VIEW_FROM_USER = 'remove view from group'
    REMOVE_USER_FROM_VIEW = 'remove user from view'
    REMOVE_USER_FROM_GROUP = 'remove user from group'
    REMOVE_USERS_FROM_GROUP = 'remove users from group'
    REMOVE_USERS_FROM_VIEW = 'remove users from view'
    REMOVE_GROUPS_FROM_VIEW = 'remove groups from view'
    REMOVE_AGENT_FROM_TAG = 'remove agent from tag'
    ###EDIT
    EDIT_GROUP_EMAIL = 'edit group email'
    EDIT_GROUP_PERMISSIONS = 'edit group permissions'
    EDIT_CPU_THROTTLE = 'edit cpu throttle'
    EDIT_NET_THROTTLE = 'edit net throttle'
    EDIT_SERVER_QUEUE_TTL = 'edit server queue ttl'
    EDIT_AGENT_QUEUE_TTL = 'edit agent queue ttl'
    EDIT_DOWNLOAD_URL = 'edit download url'
    EDIT_USER_PASSWORD = 'edit user password'
    RESET_USER_PASSWORD = 'reset user password'
    EDIT_USER_EMAIL = 'edit user email'
    EDIT_USER_FULL_NAME = 'edit user full name'
    TOGGLE_USER_STATUS = 'toggle user status'
    EDIT_CURRENT_VIEW = 'edit current user view'
    EDIT_DEFAULT_VIEW = 'edit default user view'
    EDIT_LOG_SETTINGS = 'edit log settings'
    EDIT_NOTIFICATION = 'edit notification'
    EDIT_AGENT_DISPLAY_NAME = 'edit agent display name'
    EDIT_AGENT_PRODUCTION_LEVEL = 'edit agent production level'
    EDIT_TIME_ZONE = 'edit time zone'

    @staticmethod
    def get_admin_actions():
        valid_actions = (
            map(lambda x: getattr(AdminActions, x), dir(AdminActions)[:-3])
        )
        return valid_actions
