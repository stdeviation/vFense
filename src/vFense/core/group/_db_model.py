class GroupCollections():
    Groups = 'groups'
    GroupsPerUser = 'groups_per_user'


class GroupKeys():
    GroupName = 'group_name'
    Views = 'views'
    Permissions = 'permissions'
    GroupId = 'id'
    Global = 'global'
    Users = 'users'


class GroupIndexes():
    Views = 'views'
    Users = 'users'


class GroupsPerUserKeys():
    Views = 'views'
    UserName = 'user_name'
    GroupName = 'group_name'
    GroupId = 'group_id'
    Global = 'global'
    Id = 'id'


class GroupsPerUserIndexes():
    Views = 'view_name'
    UserName = 'user_name'
    GroupId = 'group_id'
