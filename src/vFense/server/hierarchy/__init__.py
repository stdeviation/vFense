
DefaultView = 'default'
DefaultUser = 'default'
AdminUser = 'admin'
AdminGroup = 'Administrator'


class Collection():

    Users = 'users'
    Views = 'views'
    Groups = 'groups'

    GroupsPerView = 'groups_per_view'
    GroupsPerUser = 'groups_per_user'

    UsersPerView = 'users_per_view'


class UserKey():

    UserName = 'user_name'  # Primary key!
    FullName = 'full_name'
    Email = 'email'
    Password = 'password'
    Enabled = 'enabled'
    CurrentView = 'current_view'
    DefaultView = 'default_view'

    Views = 'views'
    Groups = 'groups'
    Permissions = 'permissions'


class GroupKey():

    Id = 'id'

    GroupName = 'group_name'
    Permissions = 'permissions'
    ViewId = 'view_id'
    GroupNameAndViewId = 'group_name_and_view_id'

    Users = 'users'
    View = 'view'


class ViewKey():

    ViewName = 'view_name'  # Primary key!!
    Properties = 'properties'

    Groups = 'groups'
    Users = 'users'


class GroupsPerUserKey():

    Id = 'id'
    GroupId = 'group_id'
    UserId = 'user_id'
    ViewId = 'view_id'
    GroupIdAndViewId = 'group_id_and_view_id'
    UserIdAndViewId = 'user_id_and_view_id'
    GroupUserAndViewId = 'group_user_and_view_id'


class GroupsPerViewKey():

    Id = 'id'
    GroupId = 'group_id'
    ViewId = 'view_id'
    GroupAndViewId = 'group_and_view_id'


class UsersPerViewKey():

    Id = 'id'
    UserId = 'user_id'
    ViewId = 'view_id'
    UserAndViewId = 'user_and_view_id'


class CoreProperty():
    NetThrottle = 'net_throttle'
    CpuThrottle = 'cpu_throttle'
    PackageUrl = 'package_download_url_base'
    OperationTtl = 'operation_ttl'


class DefaultGroup():
    ReadOnly = 'Read Only'
    InstallOnly = 'Install Only'
    Administrator = AdminGroup

SafeGroups = (
    DefaultGroup.ReadOnly,
    DefaultGroup.InstallOnly,
    DefaultGroup.Administrator
)
