import logging
from vFense import VFENSE_LOGGING_CONFIG
from vFense.core.decorators import time_it
from vFense.errorz._constants import ApiResultKeys
from vFense.errorz.status_codes import (
    GroupCodes, GenericCodes, GenericFailureCodes,
    GroupFailureCodes, DbCodes
)
from vFense.core.group import Group
from vFense.core.group._db import (
    fetch_group, insert_group, delete_users_in_group,
    delete_group, delete_views_in_group, add_views_to_group,
    add_users_to_group, delete_permissions_in_group,
    add_permissions_to_group, update_group
)
from vFense.core.group._db_model import (
    GroupKeys
)
from vFense.core.user.users import validate_users_in_views

logging.config.fileConfig(VFENSE_LOGGING_CONFIG)
logger = logging.getLogger('rvapi')

class GroupManager(object):
    """All actions that need to be performed on a group,
        is performed with this class
    """
    def __init__(self, group_id=None):
        self.group_id = group_id
        if group_id:
            self.properties = self._group_attributes()
            self.users = self._users()
            self.views = self._views()
        else:
            self.properties = {}
            self.users = []
            self.views = []

    @time_it
    def _group_attributes(self):
        """Retrieve a group from the database
        Basic Usage:
            >>> from vFense.group.manager import GroupManager
            >>> group_id = '8757b79c-7321-4446-8882-65457f28c78b'
            >>> group = GroupManager(group_id)
            >>> group._group_attributes()

        Returns:
             Returns a Dict of the properties of a group
             >>>
             {
                 "users": [
                     "global_admin"
                 ],
                 "views": [
                     "global"
                 ],
                 "global": true,
                 "group_name": "Global Administrator",
                 "id": "9b09c68e-a06a-4615-8547-ca3bd3ae8633",
                 "permissions": [
                     "administrator"
                 ]
             }
        """
        if self.group_id:
            data = fetch_group(self.group_id)
            if not data:
                data = {}
        else:
            data = {}
        return data

    @time_it
    def _users(self):
        """Retrieve a group from the database
        Basic Usage:
            >>> from vFense.group.manager import GroupManager
            >>> group_id = '8757b79c-7321-4446-8882-65457f28c78b'
            >>> group = GroupManager(group_id)
            >>> group._users()

        Returns:
             Returns a list of users.
             >>>
             [
                 "global_admin"
             ]
        """
        data = self._group_attributes()
        if data:
            data = data[GroupKeys.Users]

        return data

    @time_it
    def _views(self):
        """Retrieve a group from the database
        Basic Usage:
            >>> from vFense.group.manager import GroupManager
            >>> group_id = '8757b79c-7321-4446-8882-65457f28c78b'
            >>> group = GroupManager(group_id)
            >>> group._views()

        Returns:
             Returns a list of views.
             >>>
             [
                 "global"
             ]
        """
        data = self._group_attributes()
        if data:
            data = data[GroupKeys.Views]

        return data

    @time_it
    def get_attribute(self, group_attribute):
        """Retrieve group property.
        Args:
            group_attribute (str): The attribute you want to retrieve.
                example attributes.. users, views, email, permissions

        Basic Usage:
            >>> from vFense.group.manager import GroupManager
            >>> group_id = '96f02bcf-2ada-465c-b175-0e5163b36e1c'
            >>> group = GroupManager(group_id)
            >>> property = 'permissions'
            >>> group.get_property(property)

        Return:
            String
        """
        group_data = fetch_group(self.username)
        group_key = None
        if group_data:
            group_key = group_data.get(group_attribute, None)

        return group_key

    @time_it
    def create(self, group):
        """Create a group in vFense
        Args:
            group_name (Group): Instance of a group.

        Basic Usage:
            >>> from vFense.group import Group
            >>> from vFense.group.manager import GroupManager
            >>> name = 'Global Administrator'
            >>> view = 'global'
            >>> permissions = ['administrator']
            >>> is_global = True
            >>> group = Group(name, permissions, view, is_global)
            >>> manager = GroupManager()
            >>> manager.create(group)

        Returns:
            Returns the results in a dictionary
            >>>
            {
                "errors": [],
                "generic_status_code": 1010,
                "generated_ids": [
                    "b48d3d95-37b2-45cf-8cd0-e61c853141df"
                ],
                "message": "create - group Global Administrator created",
                "vfense_status_code": 12000,
                "data": {
                    "users": [],
                    "permissions": [
                        "administrator"
                    ],
                    "global": true,
                    "views": [
                        "global"
                    ],
                    "group_name": "Global Administrator"
                }
            }
        """
        generated_ids = []
        results = {}
        if isinstance(group, Group):
            group_exist = self.properties
            group.fill_in_defaults()
            invalid_fields = group.get_invalid_fields()
            group_data = group.to_dict()
            results[ApiResultKeys.ERRORS] = invalid_fields
            if not invalid_fields and not group_exist:
                status_code, status_count, error, generated_ids = (
                    insert_group(group_data)
                )

                if status_code == DbCodes.Inserted:
                    msg = 'group %s created' % (group.name)
                    results[ApiResultKeys.GENERIC_STATUS_CODE] = (
                        GenericCodes.ObjectCreated
                    )
                    results[ApiResultKeys.VFENSE_STATUS_CODE] = (
                        GroupCodes.GroupCreated
                    )
                    results[ApiResultKeys.MESSAGE] = msg
                    results[ApiResultKeys.GENERATED_IDS] = generated_ids
                    results[ApiResultKeys.DATA] = group_data

            elif group_exist:
                msg = 'group %s exists' % (group.name)
                status_code = DbCodes.Unchanged
                results[ApiResultKeys.GENERIC_STATUS_CODE] = (
                    GenericCodes.ObjectExists
                )
                results[ApiResultKeys.VFENSE_STATUS_CODE] = (
                    GroupFailureCodes.GroupIdExists
                )
                results[ApiResultKeys.MESSAGE] = msg

            elif invalid_fields:
                msg = 'Invalid fields for group %s' % (group.name)
                results[ApiResultKeys.GENERIC_STATUS_CODE] = (
                    GenericFailureCodes.InvalidFields
                )
                results[ApiResultKeys.VFENSE_STATUS_CODE] = (
                    GroupFailureCodes.InvalidFields
                )
                results[ApiResultKeys.MESSAGE] = msg

        else:
            msg = (
                'The 1st argument must be of type Group and not %s' %
                (type(group))
            )
            results[ApiResultKeys.GENERIC_STATUS_CODE] = (
                GenericFailureCodes.FailedToCreateObject
            )
            results[ApiResultKeys.VFENSE_STATUS_CODE] = (
                GenericFailureCodes.InvalidInstanceType
            )
            results[ApiResultKeys.MESSAGE] = msg

        return results

    @time_it
    def remove(self, force=True):
        """Remove  a group in vFense
        Kwargs:
            force (boolean): Remove this group even if users are
                in this group. (If a user is not part of any group, than
                that user has readonly access to vFense)
                default = False
        Basic Usage:
            >>> from vFense.group.manager import GroupManager
            >>> group_id = '8757b79c-7321-4446-8882-65457f28c78b'
            >>> group = GroupManager(group_id)
            >>> group.remove()

        Returns:
            Returns the results in a dictionary
        """
        results = {}
        if (
                self.properties and self.users and force or
                self.properties and not self.users
            ):
            status_code, status_count, error, generated_id = (
                delete_group(self.group_id)
            )
            if status_code == DbCodes.Deleted:
                msg = 'group_id %s deleted' % (self.group_id)
                results[ApiResultKeys.GENERIC_STATUS_CODE] = (
                    GenericCodes.ObjectDeleted
                )
                results[ApiResultKeys.VFENSE_STATUS_CODE] = (
                    GroupCodes.GroupDeleted
                )
                results[ApiResultKeys.DELETED_IDS] = [self.group_id]
                results[ApiResultKeys.MESSAGE] = msg

        elif self.users and not force:
            msg = (
                'users exist for group %s' % (self.group_id)
            )
            results[ApiResultKeys.GENERIC_STATUS_CODE] = (
                GenericCodes.ObjectUnchanged
            )
            results[ApiResultKeys.VFENSE_STATUS_CODE] = (
                GroupCodes.GroupUnchanged
            )
            results[ApiResultKeys.UNCHANGED_IDS] = [self.group_id]
            results[ApiResultKeys.MESSAGE] = msg

        elif not self.properties:
            msg = 'group_id %s does not exist' % (self.group_id)
            results[ApiResultKeys.GENERIC_STATUS_CODE] = (
                GenericCodes.ObjectUnchanged
            )
            results[ApiResultKeys.VFENSE_STATUS_CODE] = (
                GroupCodes.GroupUnchanged
            )
            results[ApiResultKeys.UNCHANGED_IDS] = [self.group_id]
            results[ApiResultKeys.MESSAGE] = msg

        return results

    @time_it
    def remove_users(self, users=None, force=False):
        """Remove uers from group.
        Kwargs:
            users (list): Remove a list of users from this group.
                default=None (Remove all users from this group)
            force (boolean): Remove global users from this group.
                default=False (Do not remove global users from this group)

        Basic Usage:
            >>> from vFense.group.manager import GroupManager
            >>> group_id = '8757b79c-7321-4446-8882-65457f28c78b'
            >>> users = ['global_admin']
            >>> group = GroupManager(group_id)
            >>> group.remove_users(users, force=True)

        Returns:
            Returns the results in a dictionary
        """
        results = {}
        users_exist_in_group = False
        if not users:
            users = self.users
            users_exist_in_group = True
        else:
            if users in self.users:
                users_exist_in_group = True

        is_global = self.properties[GroupKeys.GLOBAL]

        if self.properties and users and users_exist_in_group:
            if (
                    is_global and force or
                    not is_global and not force
                ):

                status_code, _, _, _ = (
                    delete_users_in_group(self.group_id, users)
                )
                if status_code == DbCodes.Replaced:
                    msg = (
                        'Users %s removed from group %s' %
                        (', '.join(users), self.group_id)
                    )
                    results[ApiResultKeys.GENERIC_STATUS_CODE] = (
                        GenericCodes.ObjectUpdated
                    )
                    results[ApiResultKeys.VFENSE_STATUS_CODE] = (
                        GroupCodes.RemovedUsersFromGroup
                    )
                    results[ApiResultKeys.MESSAGE] = msg
                    results[ApiResultKeys.UPDATED_IDS] = [self.group]

            elif is_global and not force:
                msg = (
                    'Can not remove users %s from a global group %s' %
                    (', '.join(users), self.group_id)
                )
                results[ApiResultKeys.GENERIC_STATUS_CODE] = (
                    GenericCodes.InvalidId
                )
                results[ApiResultKeys.VFENSE_STATUS_CODE] = (
                    GroupFailureCodes.CantRemoveGlobalUsersFromGroup
                )
                results[ApiResultKeys.MESSAGE] = msg
                results[ApiResultKeys.UNCHANGED_IDS] = [self.group]

        elif not users and self.properties:
            msg = (
                'users do not exist in group %s' % (self.group_id)
            )
            results[ApiResultKeys.GENERIC_STATUS_CODE] = (
                GenericCodes.ObjectUnchanged
            )
            results[ApiResultKeys.VFENSE_STATUS_CODE] = (
                GroupCodes.GroupUnchanged
            )
            results[ApiResultKeys.UNCHANGED_IDS] = [self.group]
            results[ApiResultKeys.MESSAGE] = msg

        elif not self.properties:
            msg = 'group_id %s does not exist' % (self.group_id)
            status_code = DbCodes.Skipped
            results[ApiResultKeys.GENERIC_STATUS_CODE] = (
                GenericCodes.ObjectUnchanged
            )
            results[ApiResultKeys.VFENSE_STATUS_CODE] = (
                GroupCodes.GroupUnchanged
            )
            results[ApiResultKeys.UNCHANGED_IDS] = [self.group]
            results[ApiResultKeys.MESSAGE] = msg

        return results

    @time_it
    def remove_views(self, views=None, force=False):
        """Remove views from group.
        Kwargs:
            views (list): Remove a list of views from this group.
                default = None
            force (bool): Remove a view from this group, even if
                this is a global group.
                default = False
        Basic Usage:
            >>> from vFense.group.manager import GroupManager
            >>> group_id = '8757b79c-7321-4446-8882-65457f28c78b'
            >>> views = ['global']
            >>> group = GroupManager(group_id)
            >>> group.remove_views(views, force=True)

        Returns:
            Returns the results in a dictionary
        """
        results = {}
        views_exist_in_group = False
        if not views:
            views = self.views
            views_exist_in_group = True
        else:
            if views in self.views:
                views_exist_in_group = True

        is_global = self.properties[GroupKeys.GLOBAL]

        if self.properties and views and views_exist_in_group:
            if (
                    is_global and force or
                    not is_global and not force
                ):

                status_code, _, _, _ = (
                    delete_views_in_group(self.group_id, views)
                )
                if status_code == DbCodes.Replaced:
                    msg = (
                        'Views %s removed from group %s' %
                        (', '.join(views), self.group_id)
                    )
                    results[ApiResultKeys.GENERIC_STATUS_CODE] = (
                        GenericCodes.ObjectUpdated
                    )
                    results[ApiResultKeys.VFENSE_STATUS_CODE] = (
                        GroupCodes.RemovedViewsFromGroup
                    )
                    results[ApiResultKeys.VFENSE_STATUS_CODE] = msg
                    results[ApiResultKeys.UPDATED_IDS] = [self.group_id]

            elif is_global and not force:
                msg = (
                    'Can not remove views %s from a global group %s' %
                    (', '.join(views), self.group_id)
                )
                results[ApiResultKeys.GENERIC_STATUS_CODE] = (
                    GenericCodes.InvalidId
                )
                results[ApiResultKeys.VFENSE_STATUS_CODE] = (
                    GroupFailureCodes.CantRemoveViewsFromGlobalGroup
                )
                results[ApiResultKeys.VFENSE_STATUS_CODE] = msg
                results[ApiResultKeys.UNCHANGED_IDS] = [self.group_id]

        elif not views and self.properties:
            msg = (
                'Views do not exist in group %s' % (self.group_id)
            )
            results[ApiResultKeys.GENERIC_STATUS_CODE] = (
                GenericCodes.ObjectUnchanged
            )
            results[ApiResultKeys.VFENSE_STATUS_CODE] = (
                GroupCodes.GroupUnchanged
            )
            results[ApiResultKeys.VFENSE_STATUS_CODE] = msg
            results[ApiResultKeys.UNCHANGED_IDS] = [self.group_id]

        elif not self.properties:
            msg = 'group_id %s does not exist' % (self.group_id)
            status_code = DbCodes.Skipped
            results[ApiResultKeys.GENERIC_STATUS_CODE] = (
                GenericCodes.ObjectUnchanged
            )
            results[ApiResultKeys.VFENSE_STATUS_CODE] = (
                GroupCodes.GroupUnchanged
            )
            results[ApiResultKeys.VFENSE_STATUS_CODE] = msg
            results[ApiResultKeys.UNCHANGED_IDS] = [self.group_id]

        return results

    @time_it
    def add_users(self, users):
        """Add users to group.
        Args:
            users (list): Add a list of users to this group.

        Basic Usage:
            >>> from vFense.group.manager import GroupManager
            >>> group_id = '8757b79c-7321-4446-8882-65457f28c78b'
            >>> users = ['global_admin']
            >>> group = GroupManager(group_id)
            >>> group.add_users(users)

        Returns:
            Returns the results in a dictionary
        """
        users_exist_in_group = bool(set(users).intersection(self.users))
        results = {}

        is_global = self.properties[GroupKeys.Global]
        invalid_users, global_valid_users, local_valid_users = (
            validate_users_in_views(users, self.properties[GroupKeys.Views])
        )

        if self.properties and not users_exist_in_group and not invalid_users:
            if (is_global and len(global_valid_users) == len(users) or
                    not is_global and len(local_valid_users) == len(users)):

                status_code, _, _, _ = (
                    add_users_to_group(self.group_id, users)
                )
                if status_code == DbCodes.Replaced:
                    msg = (
                        'Users %s added to group %s' %
                        (', '.join(users), self.group_id)
                    )
                    results[ApiResultKeys.GENERIC_STATUS_CODE] = (
                        GenericCodes.ObjectUpdated
                    )
                    results[ApiResultKeys.VFENSE_STATUS_CODE] = (
                        GroupCodes.AddedUsersToGroup
                    )
                    results[ApiResultKeys.MESSAGE] = msg
                    results[ApiResultKeys.UPDATED_IDS] = [self.group_id]

            elif is_global and len(global_valid_users) != len(users):
                msg = (
                    'Can not add non global users: %s, to a global group: %s'
                    % (', '.join(users), self.group_id)
                )
                results[ApiResultKeys.GENERIC_STATUS_CODE] = (
                    GenericCodes.InvalidId
                )
                results[ApiResultKeys.VFENSE_STATUS_CODE] = (
                    GroupFailureCodes.CantAddUsersToGlobalGroup
                )
                results[ApiResultKeys.MESSAGE] = msg
                results[ApiResultKeys.UNCHANGED_IDS] = [self.group_id]

            elif not is_global and len(global_valid_users) > 0:
                msg = (
                    'Can not add global users: %s, to a local group: %s' %
                    (', '.join(users), self.group_id)
                )
                results[ApiResultKeys.GENERIC_STATUS_CODE] = (
                    GenericCodes.InvalidId
                )
                results[ApiResultKeys.VFENSE_STATUS_CODE] = (
                    GroupFailureCodes.CantAddLocalUsersToGlobalGroup
                )
                results[ApiResultKeys.MESSAGE] = msg
                results[ApiResultKeys.UNCHANGED_IDS] = [self.group_id]

        elif users_exist_in_group:
            msg = (
                'users: %s, already exist in group %s' %
                (', '.join(users), self.group_id)
            )
            results[ApiResultKeys.GENERIC_STATUS_CODE] = (
                GenericCodes.ObjectUnchanged
            )
            results[ApiResultKeys.VFENSE_STATUS_CODE] = (
                GroupCodes.GroupUnchanged
            )
            results[ApiResultKeys.MESSAGE] = msg
            results[ApiResultKeys.UNCHANGED_IDS] = [self.group_id]

        elif invalid_users:
            msg = (
                'users: %s, invalid for group %s' %
                (', '.join(invalid_users), self.group_id)
            )
            results[ApiResultKeys.GENERIC_STATUS_CODE] = (
                GenericCodes.ObjectUnchanged
            )
            results[ApiResultKeys.VFENSE_STATUS_CODE] = (
                GroupCodes.GroupUnchanged
            )
            results[ApiResultKeys.MESSAGE] = msg
            results[ApiResultKeys.UNCHANGED_IDS] = [self.group_id]
            results[ApiResultKeys.INVALID_IDS] = invalid_users

        elif not self.properties:
            msg = 'group_id %s does not exist' % (self.group_id)
            results[ApiResultKeys.GENERIC_STATUS_CODE] = (
                GenericCodes.ObjectUnchanged
            )
            results[ApiResultKeys.VFENSE_STATUS_CODE] = (
                GroupCodes.GroupUnchanged
            )
            results[ApiResultKeys.MESSAGE] = msg
            results[ApiResultKeys.UNCHANGED_IDS] = [self.group_id]
            results[ApiResultKeys.INVALID_IDS] = [self.group_id]

        return results

    @time_it
    def add_views(self, views):
        """Add views to group.
        Args:
            views (list): Add a list of views to this group.

        Basic Usage:
            >>> from vFense.group.manager import GroupManager
            >>> group_id = '8757b79c-7321-4446-8882-65457f28c78b'
            >>> views = ['global']
            >>> group = GroupManager(group_id)
            >>> group.add_views(views)

        Returns:
            Returns the results in a dictionary
        """
        results = {}
        views_exist_in_group = False
        if views in self.views:
            views_exist_in_group = True
        else:
            views_exist_in_group = False


        if self.properties and not views_exist_in_group:
            status_code, _, _, _ = (
                add_views_to_group(self.group_id, views)
            )
            if status_code == DbCodes.Replaced:
                msg = (
                    'Views %s added to group %s' %
                    (', '.join(views), self.group_id)
                )
                results[ApiResultKeys.GENERIC_STATUS_CODE] = (
                    GenericCodes.ObjectUpdated
                )
                results[ApiResultKeys.VFENSE_STATUS_CODE] = (
                    GroupCodes.AddedViewsToGroup
                )
                results[ApiResultKeys.UPDATED_IDS] = [self.group_id]
                results[ApiResultKeys.MESSAGE] = msg


        elif self.properties and views_exist_in_group:
            msg = (
                'Views %s already exist in group %s' %
                (', '.join(views), self.group_id)
            )
            results[ApiResultKeys.GENERIC_STATUS_CODE] = (
                GenericCodes.ObjectExists
            )
            results[ApiResultKeys.VFENSE_STATUS_CODE] = (
                GroupCodes.GroupUnchanged
            )
            results[ApiResultKeys.UNCHANGED_IDS] = [self.group_id]
            results[ApiResultKeys.MESSAGE] = msg


        elif not self.properties:
            msg = 'group_id %s does not exist' % (self.group_id)
            results[ApiResultKeys.GENERIC_STATUS_CODE] = (
                GenericCodes.ObjectUnchanged
            )
            results[ApiResultKeys.VFENSE_STATUS_CODE] = (
                GroupCodes.GroupUnchanged
            )
            results[ApiResultKeys.UNCHANGED_IDS] = [self.group_id]
            results[ApiResultKeys.MESSAGE] = msg

        return results

    def remove_permissions(self, permissions):
        """Remove permissions for this group.
        Args:
            permissions (list): List of permissions.

        Basic Usage:
            >>> from vFense.group.manager import GroupManager
            >>> group_id = '8757b79c-7321-4446-8882-65457f28c78b'
            >>> permissions = ['install', 'uninstall']
            >>> group = GroupManager(group_id)
            >>> group.remove_permissions(permissions)

        Returns:
            Returns the results in a dictionary
        """
        group_exist = self.properties
        results = {}
        if group_exist:
            group = Group(
                group_exist[GroupKeys.GroupName], permissions=permissions
            )
            invalid_permissions = group.get_invalid_fields()
            if not invalid_permissions:
                status_code, _, _, _ = (
                    delete_permissions_in_group(self.group_id, permissions)
                )
                if status_code == DbCodes.Replaced:
                    msg = (
                        'Removed the following permissions: %s from group %s'
                        % (permissions, self.group_id)
                    )
                    results[ApiResultKeys.MESSAGE] = msg
                    results[ApiResultKeys.GENERIC_STATUS_CODE] = (
                        GenericCodes.ObjectUpdated
                    )
                    results[ApiResultKeys.VFENSE_STATUS_CODE] = (
                        GroupCodes.PermissionsUpdated
                    )
                    results[ApiResultKeys.UPDATED_IDS] = [self.group_id]

                if status_code == DbCodes.Unchanged:
                    msg = (
                        'These permissions do not exist: %s in group %s'
                        % (permissions, self.group_id)
                    )
                    results[ApiResultKeys.MESSAGE] = msg
                    results[ApiResultKeys.GENERIC_STATUS_CODE] = (
                        GenericCodes.ObjectUnchanged
                    )
                    results[ApiResultKeys.VFENSE_STATUS_CODE] = (
                        GroupCodes.PermissionsUnchanged
                    )
                    results[ApiResultKeys.UNCHANGED_IDS] = [self.group_id]

            else:
                msg = 'Invalid permissions: %s' % (permissions)
                results[ApiResultKeys.MESSAGE] = msg
                results[ApiResultKeys.GENERIC_STATUS_CODE] = (
                    GenericCodes.InvalidValue
                )
                results[ApiResultKeys.VFENSE_STATUS_CODE] = (
                    GroupFailureCodes.InvalidPermissions
                )
                results[ApiResultKeys.UNCHANGED_IDS] = [self.group_id]
                results[ApiResultKeys.INVALID_IDS] = permissions


        else:
            msg = 'group_id %s does not exist' % (self.group_id)
            results[ApiResultKeys.GENERIC_STATUS_CODE] = (
                GenericCodes.ObjectUnchanged
            )
            results[ApiResultKeys.VFENSE_STATUS_CODE] = (
                GroupCodes.GroupUnchanged
            )
            results[ApiResultKeys.MESSAGE] = msg
            results[ApiResultKeys.UNCHANGED_IDS] = [self.group_id]
            results[ApiResultKeys.INVALID_IDS] = [self.group_id]

        return results


    def add_permissions(self, permissions):
        """Add permissions for this group.
        Args:
            permissions (list): List of permissions.

        Basic Usage:
            >>> from vFense.group.manager import GroupManager
            >>> group_id = '8757b79c-7321-4446-8882-65457f28c78b'
            >>> permissions = ['install', 'uninstall']
            >>> group = GroupManager(group_id)
            >>> group.add_permissions(permissions)

        Returns:
            Returns the results in a dictionary
        """
        group_exist = self.properties
        results = {}
        if group_exist:
            group = (
                Group(
                    group_exist[GroupKeys.GroupName],
                    permissions=permissions
                )
            )
            invalid_permissions = group.get_invalid_fields()
            if not invalid_permissions:
                status_code, _, _, _ = (
                    add_permissions_to_group(self.group_id, permissions)
                )
                if status_code == DbCodes.Replaced:
                    msg = (
                        'Added the following permissions: %s to group %s'
                        % (permissions, self.group_id)
                    )
                    results[ApiResultKeys.MESSAGE] = msg
                    results[ApiResultKeys.GENERIC_STATUS_CODE] = (
                        GenericCodes.ObjectUpdated
                    )
                    results[ApiResultKeys.VFENSE_STATUS_CODE] = (
                        GroupCodes.PermissionsUpdated
                    )
                    results[ApiResultKeys.UPDATED_IDS] = [self.group_id]

                if status_code == DbCodes.Unchanged:
                    msg = (
                        'These permissions do not exist: %s in group %s'
                        % (permissions, self.group_id)
                    )
                    results[ApiResultKeys.MESSAGE] = msg
                    results[ApiResultKeys.GENERIC_STATUS_CODE] = (
                        GenericCodes.ObjectUnchanged
                    )
                    results[ApiResultKeys.VFENSE_STATUS_CODE] = (
                        GroupCodes.PermissionsUnchanged
                    )
                    results[ApiResultKeys.UNCHANGED_IDS] = [self.group_id]

            else:
                msg = 'Invalid permissions: %s' % (permissions)
                results[ApiResultKeys.MESSAGE] = msg
                results[ApiResultKeys.GENERIC_STATUS_CODE] = (
                    GenericCodes.InvalidValue
                )
                results[ApiResultKeys.VFENSE_STATUS_CODE] = (
                    GroupFailureCodes.InvalidPermissions
                )
                results[ApiResultKeys.UNCHANGED_IDS] = [self.group_id]
                results[ApiResultKeys.INVALID_IDS] = permissions

        else:
            msg = 'group_id %s does not exist' % (self.group_id)
            results[ApiResultKeys.GENERIC_STATUS_CODE] = (
                GenericCodes.ObjectUnchanged
            )
            results[ApiResultKeys.VFENSE_STATUS_CODE] = (
                GroupCodes.GroupUnchanged
            )
            results[ApiResultKeys.MESSAGE] = msg
            results[ApiResultKeys.UNCHANGED_IDS] = [self.group_id]
            results[ApiResultKeys.INVALID_IDS] = [self.group_id]

        return results

    def edit_name(self, group_name):
        """Edit the name of this group.
        Args:
            group_name (str): The new name of this group.

        Basic Usage:
            >>> from vFense.group.manager import GroupManager
            >>> group_id = '8757b79c-7321-4446-8882-65457f28c78b'
            >>> group_name = 'Foo'
            >>> group = GroupManager(group_id)
            >>> group.change_name(group_name)

        Returns:
            Returns the results in a dictionary
        """
        group = Group(name=group_name)
        results = self.__edit_properties(group)

        return results


    def edit_email(self, email):
        """Edit the email address of this group.
        Args:
            email (str): The new email address of this group.

        Basic Usage:
            >>> from vFense.group.manager import GroupManager
            >>> group_id = '8757b79c-7321-4446-8882-65457f28c78b'
            >>> email = 'foo@foo.com'
            >>> group = GroupManager(group_id)
            >>> group.change_email(email)

        Returns:
            Returns the results in a dictionary
        """
        group = Group(email=email)
        results = self.__edit_properties(group)

        return results


    def __edit_properties(self, group):
        """Edit the properties of this group.
        Args:
            group (Group): Group instance.

        Basic Usage:
            >>> from vFense.group import Group
            >>> from vFense.group.manager import GroupManager
            >>> group_id = '8757b79c-7321-4446-8882-65457f28c78b'
            >>> group = Group(group_name, email="foo@foo.com")
            >>> manager = GroupManager(group_id)
            >>> manager.__edit_properties(group)

        Returns:
            Returns the results in a dictionary
        """
        group_exist = self.properties
        results = {}
        invalid_fields = group.get_invalid_fields()
        if group_exist and not invalid_fields and isinstance(group, Group):
            status_code, _, _, _ = (
                update_group(self.group_id, group.to_dict_non_null())
            )
            if status_code == DbCodes.Replaced:
                msg = (
                    'group id %s updated with data: %s'
                    % (self.group_id, group.to_dict_non_null())
                )
                results[ApiResultKeys.MESSAGE] = msg
                results[ApiResultKeys.GENERIC_STATUS_CODE] = (
                    GenericCodes.ObjectUpdated
                )
                results[ApiResultKeys.VFENSE_STATUS_CODE] = (
                    GroupCodes.GroupUpdated
                )
                results[ApiResultKeys.UPDATED_IDS] = [self.group_id]

            if status_code == DbCodes.Unchanged:
                msg = (
                    'Group data: %s is the same as the previous values'
                    % (group.to_dict_non_null())
                )
                results[ApiResultKeys.MESSAGE] = msg
                results[ApiResultKeys.GENERIC_STATUS_CODE] = (
                    GenericCodes.ObjectUnchanged
                )
                results[ApiResultKeys.VFENSE_STATUS_CODE] = (
                    GroupCodes.GroupUnchanged
                )
                results[ApiResultKeys.UNCHANGED_IDS] = [self.group_id]

        elif invalid_fields:
            msg = 'Invalid fields: %s' % (invalid_fields)
            results[ApiResultKeys.GENERIC_STATUS_CODE] = (
                GenericCodes.InvalidFields
            )
            results[ApiResultKeys.VFENSE_STATUS_CODE] = (
                GroupFailureCodes.InvalidFields
            )
            results[ApiResultKeys.MESSAGE] = msg
            results[ApiResultKeys.UNCHANGED_IDS] = [self.group_id]
            results[ApiResultKeys.INVALID_DATA] = [invalid_fields]

        elif not isinstance(group, Group):
            msg = 'Group not of instance type Group: %s' % (type(group))
            results[ApiResultKeys.GENERIC_STATUS_CODE] = (
                GenericCodes.InvalidValue
            )
            results[ApiResultKeys.VFENSE_STATUS_CODE] = (
                GroupFailureCodes.InvalidValue
            )
            results[ApiResultKeys.MESSAGE] = msg
            results[ApiResultKeys.UNCHANGED_IDS] = [self.group_id]

        else:
            msg = 'group_id %s does not exist' % (self.group_id)
            results[ApiResultKeys.GENERIC_STATUS_CODE] = (
                GenericCodes.ObjectUnchanged
            )
            results[ApiResultKeys.VFENSE_STATUS_CODE] = (
                GroupCodes.GroupUnchanged
            )
            results[ApiResultKeys.MESSAGE] = msg
            results[ApiResultKeys.UNCHANGED_IDS] = [self.group_id]
            results[ApiResultKeys.INVALID_IDS] = [self.group_id]

        return results
