GroupsCollection = 'groups'
GroupsPerUserCollection = 'groups_per_user'
INSTALL_ONLY = 'Install Only'
READ_ONLY = 'Read Only'
ADMINISTRATOR = 'Administrator'

class GroupKeys():
    GroupName = 'group_name'
    CustomerName = 'customer_name'
    Permissions = 'permissions'
    GroupId = 'id'


class GroupIndexes():
    CustomerName = 'customer_name'


class GroupsPerUserKeys():
    CustomerName = 'customer_name'
    UserName = 'user_name'
    GroupName = 'group_name'
    GroupId = 'group_id'
    Id = 'id'


class GroupsPerUserIndexes():
    CustomerName = 'customer_name'
    UserName = 'user_name'
    GroupName = 'group_name'
    GroupId = 'group_id'
