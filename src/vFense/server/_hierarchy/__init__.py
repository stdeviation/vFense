from collections import namedtuple

UserCollection = 'users'
GroupCollection = 'groups'
ViewCollection = 'views'
DefaultView = 'default'


class UserKey():

    Name = 'name'  # Primary key!
    Id = 'id'
    FullName = 'full_name'
    Email = 'email'
    Password = 'password'
    Enabled = 'enabled'
    Groups = 'groups'
    Views = 'views'
    CurrentView = 'current_view'
    DefaultView = 'default_view'

UserInfo = namedtuple('UserInfo', [UserKey.Name])


class GroupKey():

    Id = 'id'
    Name = 'name'
    View = 'view'
    Users = 'users'
    Permissions = 'permissions'

GroupInfo = namedtuple('GroupInfo', [GroupKey.Id, GroupKey.Name])


class ViewKey():

    Name = 'name'  # Primary key!!
    Id = 'id'
    Groups = 'groups'
    Users = 'users'

    # Temporary hacks
    NetThrottle = 'net_throttle'
    CpuThrottle = 'cpu_throttle'

ViewInfo = namedtuple('ViewInfo', [ViewKey.Name])
