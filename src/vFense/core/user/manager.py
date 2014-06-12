import logging
from vFense import VFENSE_LOGGING_CONFIG
from vFense.errorz._constants import ApiResultKeys
from vFense.core.user import User
from vFense.core.user._db_model import UserKeys
from vFense.core.user._constants import DefaultUsers
from vFense.core.view._constants import DefaultViews
from vFense.core.group._db_model import GroupKeys
from vFense.core.group._db import (
    delete_user_in_groups, add_user_to_groups,
    fetch_group_by_name, fetch_groupids_for_user
)

from vFense.core.group._constants import DefaultGroups

from vFense.core.view._db import (
    delete_user_in_views, fetch_views_for_user, fetch_view,
    fetch_all_view_names, update_usernames_for_views
)


from vFense.core.user._db import (
    insert_user, fetch_user, delete_user, update_user,
    fetch_user_and_all_properties, user_status_toggle,
    update_views_for_user, delete_views_in_user
)

from vFense.core.group.groups import (
    validate_group_ids, validate_groups_in_views
)

from vFense.core.view.views import validate_view_names

from vFense.utils.security import Crypto, check_password
from vFense.core.decorators import time_it
from vFense.errorz.status_codes import (
    UserFailureCodes, UserCodes, GenericFailureCodes, GenericCodes,
    DbCodes, ViewFailureCodes, GroupFailureCodes, GroupCodes,
    ViewCodes
)

logging.config.fileConfig(VFENSE_LOGGING_CONFIG)
logger = logging.getLogger('rvapi')


class UserManager(object):
    """All actions that need to be performed on a user,
        is performed with this class
    """
    def __init__(self, username):
        self.username = username
        self.properties = self._user_attributes()

    @time_it
    def _user_attributes(self, without_fields=[UserKeys.Password]):
        """Retrieve properties from the users collection.
        Args:
            without_fields (list): The attributes you do not
                want to retrieve. example attributes.. password
                default = 'password'

        Basic Usage:
            >>> from vFense.user.manager import UserManager
            >>> name = 'admin'
            >>> user = UserManager(name)
            >>> user._user_attributes()

        Returns:
            Dictionary
            >>>
            {
                "current_view": "default",
                "enabled": "yes",
                "full_name": "vFense Admin Account",
                "default_view": "default",
                "user_name": "admin",
                "email": ""
            }
        """
        data = fetch_user(self.username, without_fields)
        return data

    @time_it
    def get_attribute(self, user_attribute):
        """Retrieve user property.
        Args:
            user_attribute (str): The attribute you want to retrieve.
                example attributes.. password, current_view, email

        Basic Usage:
            >>> from vFense.user.manager import UserManager
            >>> name = 'admin'
            >>> user = UserManager(name)
            >>> property = 'current_view'
            >>> user.get_property(property)

        Return:
            String
        """
        user_data = fetch_user(self.username)
        user_key = None
        if user_data:
            user_key = user_data.get(user_attribute, None)

        return user_key

    @time_it
    def get_all_attributes(self):
        """Retrieve a user and all of its properties by username.
        Basic Usage:
            >>> from vFense.user.manager import UserManager
            >>> username = 'admin'
            >>> user.get_all_attributes()

        Returns:
            Dictionary of user properties.
            {
                "current_view": "default",
                "views": [
                    {
                        "admin": true,
                        "name": "default"
                    }
                ],
                "groups": [
                    {
                        "group_id": "1b74a706-34e5-482a-bedc-ffbcd688f066",
                        "group_name": "Administrator"
                    }
                ],
                "default_view": "default",
                "user_name": "admin",
                "permissions": [
                    "administrator"
                ]
            }
        """
        user_data = fetch_user_and_all_properties(self.username)
        return user_data

    @time_it
    def toggle_status(self):
        """Enable or disable a user
        Basic Usage:
            >>> from vFense.user.manager import UserManager
            >>> username = 'admin'
            >>> user.toggle_status()

        Returns:
            Dictionary of the status of the operation.
            >>>
                {
                    "vfense_status_code": 13001,
                    "updated_ids": [
                        "tester"
                    ],
                    "message": "toggle_user_status - user tester is enabled",
                }
        """
        results = {}
        status_code, _, _, _ = (
            user_status_toggle(self.username)
        )
        self.properties = self._user_attributes()
        if status_code == DbCodes.Replaced:
            if self.properties[UserKeys.Enabled]:
                msg = 'user %s is enabled' % (self.username)

            else:
                msg = 'user %s is disabled' % (self.username)

            results[ApiResultKeys.GENERIC_STATUS_CODE] = (
                GenericCodes.ObjectUpdated
            )
            results[ApiResultKeys.VFENSE_STATUS_CODE] = (
                UserCodes.UserUpdated
            )
            results[ApiResultKeys.UPDATED_IDS] = [self.username]

        elif status_code == DbCodes.Skipped:
            msg = 'user %s is invalid' % (self.username)
            results[ApiResultKeys.GENERIC_STATUS_CODE] = (
                GenericCodes.InvalidId
            )
            results[ApiResultKeys.VFENSE_STATUS_CODE] = (
                UserFailureCodes.InvalidUserName
            )

        results[ApiResultKeys.MESSAGE] = msg

        return results

    @time_it
    def create(self, user, group_ids):
        """Add a new user into vFense
        Args:
            user (User): A user instance filled out with the
                appropriate fields.
            group_ids (list): List of vFense group ids to add the user too.

        Basic Usage:
            >>> from vFense.user import User
            >>> from vFense.user.manager import UserManager
            >>> username = 'global_admin'
            >>> fullname = 'Global Administrator'
            >>> password = 'Testing123#'
            >>> group_ids = ['8757b79c-7321-4446-8882-65457f28c78b']
            >>> user = (
                    User(
                        username, password=password,
                        full_name=fullname,
                        enabled=True, is_global=True
                    )
                )
            >>> manager = UserManager(username)
            >>> manager.create(user, group_ids)

        Return:
            Dictionary of the status of the operation.
            >>>
            {
                "errors": [],
                "data": [
                    {
                        "default_view": "global",
                        "global": true,
                        "full_name": "Global Administrator",
                        "views": [
                            "global"
                        ],
                        "current_view": "global",
                        "user_name": "global_admin",
                        "email": null,
                        "enabled": true
                    }
                ],
                "generic_status_code": 1010,
                "generated_ids": [
                    "global_admin"
                ],
                "message": "create - user name global_admin created",
                "vfense_status_code": 13000
            }
        """
        user_exist = self.properties
        user.fill_in_defaults()
        user_data = user.to_dict()
        results = {}
        if isinstance(user, User) and not user_exist:
            invalid_fields = user.get_invalid_fields()
            results[ApiResultKeys.ERRORS] = invalid_fields

            if invalid_fields:
                results[ApiResultKeys.GENERIC_STATUS_CODE] = (
                    GenericFailureCodes.FailedToCreateObject
                )
                results[ApiResultKeys.VFENSE_STATUS_CODE] = (
                    UserFailureCodes.FailedToCreateUser
                )

            else:
                encrypted_password = Crypto().hash_bcrypt(user.password)
                user_data[UserKeys.Password] = encrypted_password
                current_view_is_valid = fetch_view(user.current_view)
                default_view_is_valid = fetch_view(user.default_view)
                validated_groups, _, invalid_groups = (
                    validate_group_ids(
                        group_ids, user.current_view, user.is_global
                    )
                )
                views = (list(set([user.current_view, user.default_view])))
                if user.is_global:
                    views = fetch_all_view_names()
                user_data[UserKeys.Views] = views


                if (current_view_is_valid and default_view_is_valid and
                        validated_groups):
                    object_status, _, _, generated_ids = (
                        insert_user(user_data)
                    )
                    user_data.pop(UserKeys.Password)

                    if object_status == DbCodes.Inserted:
                        msg = 'user name %s created' % (self.username)
                        self.properties = self._user_attributes()
                        self.add_to_views(views)
                        self.add_to_groups(group_ids)
                        results[ApiResultKeys.GENERIC_STATUS_CODE] = (
                            GenericCodes.ObjectCreated
                        )
                        results[ApiResultKeys.VFENSE_STATUS_CODE] = (
                            UserCodes.UserCreated
                        )
                        results[ApiResultKeys.GENERATED_IDS] = [self.username]
                        results[ApiResultKeys.MESSAGE] = msg
                        results[ApiResultKeys.DATA] = [user_data]

                elif (not current_view_is_valid or not default_view_is_valid
                      and validated_groups):

                    msg = (
                        'view name %s does not exist' %
                        (user.current_view)
                    )
                    results[ApiResultKeys.GENERIC_STATUS_CODE] = (
                        GenericCodes.InvalidId
                    )
                    results[ApiResultKeys.VFENSE_STATUS_CODE] = (
                        ViewFailureCodes.ViewDoesNotExist
                    )
                    results[ApiResultKeys.MESSAGE] = msg
                    results[ApiResultKeys.UNCHANGED_IDS] = [self.username]
                    results[ApiResultKeys.DATA] = []

                elif (current_view_is_valid or default_view_is_valid and
                      not validated_groups):

                    msg = 'group ids %s does not exist' % (invalid_groups)
                    results[ApiResultKeys.GENERIC_STATUS_CODE] = (
                        GenericCodes.InvalidId
                    )
                    results[ApiResultKeys.VFENSE_STATUS_CODE] = (
                        GroupFailureCodes.InvalidGroupId
                    )
                    results[ApiResultKeys.MESSAGE] = msg
                    results[ApiResultKeys.UNCHANGED_IDS] = [self.username]

                else:
                    group_error = (
                        'group ids %s does not exist' % (invalid_groups)
                    )
                    view_error = (
                        'view name %s does not exist' %
                        (user.current_view)
                    )
                    msg = group_error + ' and ' + view_error
                    results[ApiResultKeys.GENERIC_STATUS_CODE] = (
                        GenericFailureCodes.FailedToCreateObject
                    )
                    results[ApiResultKeys.VFENSE_STATUS_CODE] = (
                        UserFailureCodes.FailedToCreateUser
                    )
                    results[ApiResultKeys.MESSAGE] = msg
                    results[ApiResultKeys.UNCHANGED_IDS] = [self.username]

        elif user_exist and isinstance(user, User):
            msg = 'username %s already exists' % (self.username)
            results[ApiResultKeys.GENERIC_STATUS_CODE] = (
                GenericCodes.ObjectExists
            )
            results[ApiResultKeys.VFENSE_STATUS_CODE] = (
                UserFailureCodes.UserNameExists
            )
            results[ApiResultKeys.MESSAGE] = msg
            results[ApiResultKeys.UNCHANGED_IDS] = [self.username]

        else:
            msg = 'Please pass a User instance, not a %s' % (str(type(user)))
            results[ApiResultKeys.GENERIC_STATUS_CODE] = (
                GenericFailureCodes.FailedToCreateObject
            )
            results[ApiResultKeys.VFENSE_STATUS_CODE] = (
                GenericFailureCodes.InvalidInstanceType
            )
            results[ApiResultKeys.MESSAGE] = msg
            results[ApiResultKeys.UNCHANGED_IDS] = [self.username]

        return results


    @time_it
    def add_to_views(self, views=None):
        """Add a multiple views to a user
        Kwargs:
            views (list): List of views this user will be added too.
                default = None

        Basic Usage:
            >>> from vFense.user.manager import UserManager
            >>> username = 'tester1'
            >>> views = ['Test View 2']
            >>> manager = UserManager(username)
            >>> manager.add_to_views(views)

        Returns:
            Dictionary of the status of the operation.
            >>>
            {
                "message": "user tester1 added to Test View 2",
                "vfense_status_code": 14004,
                "generic_status_code": 1008
            }
        """
        if isinstance(views, str):
            views = views.split(',')

        views_are_valid, _, _ = validate_view_names(views)
        if self.properties[UserKeys.Global]:
            views = fetch_all_view_names()

        results = {}
        user_exist = self.properties
        if views_are_valid and user_exist:
            status_code, _, _, _ = update_views_for_user(self.username, views)
            update_usernames_for_views(views, [self.username])
            if status_code == DbCodes.Replaced:
                msg = (
                    'user %s was added to %s successfully' % (
                        self.username, ', '.join(views)
                    )
                )
                results[ApiResultKeys.MESSAGE] = msg
                results[ApiResultKeys.GENERIC_STATUS_CODE] = (
                    GenericCodes.ObjectUpdated
                )
                results[ApiResultKeys.VFENSE_STATUS_CODE] = (
                    ViewCodes.ViewsAddedToUser
                )
                results[ApiResultKeys.UPDATED_IDS] = [self.username]

            elif status_code == DbCodes.Unchanged:
                msg = (
                    'user %s is already in views: %s' % (
                        self.username, ', '.join(views)
                    )
                )
                results[ApiResultKeys.MESSAGE] = msg
                results[ApiResultKeys.GENERIC_STATUS_CODE] = (
                    GenericCodes.ObjectUnchanged
                )
                results[ApiResultKeys.VFENSE_STATUS_CODE] = (
                    ViewCodes.ViewUnchanged
                )
                results[ApiResultKeys.UNCHANGED_IDS] = [self.username]


        elif not user_exist:
            msg = 'User name is invalid: %s' % (self.username)
            results[ApiResultKeys.MESSAGE] = msg
            results[ApiResultKeys.GENERIC_STATUS_CODE] = (
                GenericCodes.InvalidId
            )
            results[ApiResultKeys.VFENSE_STATUS_CODE] = (
                UserFailureCodes.UserNameDoesNotExist
            )
            results[ApiResultKeys.INVALID_IDS] = [self.username]

        elif not views_are_valid[0]:
            msg = (
                'View names are invalid: %s' % (
                    ' and '.join(views_are_valid[2])
                )
            )
            results[ApiResultKeys.MESSAGE] = msg
            results[ApiResultKeys.GENERIC_STATUS_CODE] = (
                GenericCodes.InvalidId
            )
            results[ApiResultKeys.VFENSE_STATUS_CODE] = (
                ViewFailureCodes.InvalidViewName
            )
            results[ApiResultKeys.INVALID_IDS] = [views]

        return results

    @time_it
    def add_to_groups(self, group_ids):
        """Add a user into a vFense group
        Args:
            username (str):  Name of the user already in vFense.
            view (str): The view this user is part of.
            group_ids (list): List of group ids.

        Basic Usage:
            >>> from vFense.user.manager import UserManager
            >>> username = 'tester1'
            >>> group_ids = ['0834e656-27a5-4b13-ba56-635797d0d1fc']
            >>> manager = UserManager(username)
            >>> manager.add_to_groups(group_ids)

        Returns:
            Returns the results in a dictionary
            >>>
            {
                "data": [],
                "generic_status_code": 1008,
                "message": "add_user_to_groups - user tester1 add to groups",
                "vfense_status_code": 12004
            }
        """
        user_exist = self.properties
        results = {}
        generated_ids = []
        users_group_exist = []
        if user_exist:
            is_global = user_exist[UserKeys.Global]
            invalid_groups, valid_global_groups, valid_local_groups = (
                validate_groups_in_views(
                    group_ids, user_exist[UserKeys.Views]
                )
            )
            if (
                    is_global and
                    len(valid_global_groups) == len(group_ids)
                    or not is_global and
                    len(valid_local_groups) == len(group_ids)
                ):

                status_code, _, _, generated_ids = (
                    add_user_to_groups(group_ids, self.username)
                )

                if status_code == DbCodes.Replaced:
                    msg = (
                        'user %s add to groups: %s' %
                        (self.username, ', '.join(group_ids))
                    )
                    results[ApiResultKeys.GENERIC_STATUS_CODE] = (
                        GenericCodes.ObjectUpdated
                    )
                    results[ApiResultKeys.VFENSE_STATUS_CODE] = (
                        UserCodes.UsersAddedToGroup
                    )
                    results[ApiResultKeys.UPDATED_IDS] = [self.username]
                    results[ApiResultKeys.MESSAGE] = msg

                elif status_code == DbCodes.Unchanged:
                    msg = (
                        'user %s is already in groups: %s' % (
                            self.username, ', '.join(users_group_exist)
                        )
                    )
                    results[ApiResultKeys.GENERIC_STATUS_CODE] = (
                        GenericCodes.ObjectExists
                    )
                    results[ApiResultKeys.VFENSE_STATUS_CODE] = (
                        GroupFailureCodes.GroupExistForUser
                    )
                    results[ApiResultKeys.UNCHANGED_IDS] = [self.username]
                    results[ApiResultKeys.MESSAGE] = msg


            elif is_global and len(valid_global_groups) != len(group_ids):
                msg = (
                    'Can not add local groups to a global user %s: %s' %
                    (self.username, ', '.join(group_ids))
                )
                results[ApiResultKeys.GENERIC_STATUS_CODE] = (
                    GenericCodes.InvalidId
                )
                results[ApiResultKeys.VFENSE_STATUS_CODE] = (
                    UserFailureCodes.CantAddLocalGroupToGlobalUser
                )
                results[ApiResultKeys.UNCHANGED_IDS] = [self.username]
                results[ApiResultKeys.MESSAGE] = msg

            elif not is_global and len(valid_local_groups) != len(group_ids):
                msg = (
                    'Can not add global groups to a local user %s: %s' %
                    (self.username, ', '.join(group_ids))
                )
                results[ApiResultKeys.GENERIC_STATUS_CODE] = (
                    GenericCodes.InvalidId
                )
                results[ApiResultKeys.VFENSE_STATUS_CODE] = (
                    UserFailureCodes.CantAddGlobalGroupToLocalUser
                )
                results[ApiResultKeys.UNCHANGED_IDS] = [self.username]
                results[ApiResultKeys.MESSAGE] = msg

            elif invalid_groups:
                msg = (
                    'Invalid group ids: %s' %
                    (', '.join(invalid_groups))
                )
                results[ApiResultKeys.GENERIC_STATUS_CODE] = (
                    GenericCodes.InvalidId
                )
                results[ApiResultKeys.VFENSE_STATUS_CODE] = (
                    GroupFailureCodes.InvalidGroupId
                )
                results[ApiResultKeys.INVALID_IDS] = [group_ids]
                results[ApiResultKeys.UNCHANGED_IDS] = [self.username]
                results[ApiResultKeys.MESSAGE] = msg

        elif not user_exist:
            msg = 'User name is invalid: %s' % (self.username)
            results[ApiResultKeys.GENERIC_STATUS_CODE] = (
                GenericCodes.InvalidId
            )
            results[ApiResultKeys.VFENSE_STATUS_CODE] = (
                UserFailureCodes.InvalidUserName
            )
            results[ApiResultKeys.INVALID_IDS] = [self.username]
            results[ApiResultKeys.UNCHANGED_IDS] = [self.username]
            results[ApiResultKeys.MESSAGE] = msg

        return results

    @time_it
    def remove(self, force=False):
        """Remove a user from vFense

        Kwargs:
            force (boolean): Remove the global_admin users
                default=False

        Basic Usage:
            >>> from vFense.user.manager import UserManager
            >>> username = 'shaolin'
            >>> manager = UserManager(username)
            >>> manager.remove()

        Returns:
            Dictionary of the status of the operation.
            >>>
            {
                "generic_status_code": 1012,
                "deleted_ids": [
                    "tester1"
                ],
                "message": "remove - User removed tester1",
                "vfense_status_code": 13002
            }
        """
        user_exist = self.properties
        username_not_to_delete = []
        username_to_delete = []
        results = {}
        if (user_exist and self.username != DefaultUsers.GLOBAL_ADMIN
                and not force
                or user_exist and force):

            self.remove_from_groups()
            self.remove_from_views()
            username_to_delete.append(self.username)

            object_status, _, _, _ = (
                delete_user(self.username)
            )

            if object_status == DbCodes.Deleted:
                msg = 'User removed %s' % (self.username)
                results[ApiResultKeys.DELETED_IDS] = (
                    username_to_delete
                )
                results[ApiResultKeys.GENERIC_STATUS_CODE] = (
                    GenericCodes.ObjectDeleted
                )
                results[ApiResultKeys.VFENSE_STATUS_CODE] = (
                    UserCodes.UserDeleted
                )
                results[ApiResultKeys.MESSAGE] = msg

        elif self.username == DefaultUsers.GLOBAL_ADMIN:
            msg = 'Can not delete the %s user' % (self.username)
            username_not_to_delete.append(self.username)
            results[ApiResultKeys.GENERIC_STATUS_CODE] = (
                GenericCodes.CouldNotBeDeleted
            )
            results[ApiResultKeys.VFENSE_STATUS_CODE] = (
                UserFailureCodes.AdminUserCanNotBeDeleted
            )
            results[ApiResultKeys.UNCHANGED_IDS] = (
                username_not_to_delete
            )
            results[ApiResultKeys.MESSAGE] = msg

        else:
            msg = 'User does not exist %s' % (self.username)
            username_not_to_delete.append(self.username)
            results[ApiResultKeys.GENERIC_STATUS_CODE] = (
                GenericCodes.InvalidId
            )
            results[ApiResultKeys.VFENSE_STATUS_CODE] = (
                UserFailureCodes.UserNameDoesNotExist
            )
            results[ApiResultKeys.MESSAGE] = msg
            results[ApiResultKeys.INVALID_IDS] =  [self.username]
            results[ApiResultKeys.UNCHANGED_IDS] =  [self.username]

        return results

    @time_it
    def remove_from_groups(self, group_ids=None, remove_admin=False):
        """Remove a group from a user
        Kwargs:
            group_ids (list): List of group_ids.
            remove_admin (bool): Wheather to remove the global admin user
                from this group.
                default = False

        Basic Usage:
            >>> username = 'shaolin'
            >>> group_ids = ['0834e656-27a5-4b13-ba56-635797d0d1fc', '8757b79c-7321-4446-8882-65457f28c78b']
            >>> manager = UserManager(username)
            >>> manager.remove_from_groups(group_ids)

        Returns:
            Returns the results in a dictionary
            >>>
            {
                "message": "group ids: f8fc202f-2691-4d17-8cb8-eec6a1197bae",
                "vfense_status_code": 12005,
                "generic_status_code": 1012
            }
        """
        user_exist = self.properties
        exist_in_groupids = False
        admin_group_id = None
        admin_group_id_exists_in_group_ids = False
        results = {}
        if user_exist:
            group_ids_in_db = fetch_groupids_for_user(self.username)
            if self.username == DefaultUsers.GLOBAL_ADMIN:
                admin_group_id = (
                    fetch_group_by_name(
                        DefaultGroups.GLOBAL_ADMIN, DefaultViews.GLOBAL,
                        GroupKeys.GroupId
                    )[GroupKeys.GroupId]
                )

            if group_ids:
                exist_in_groupids = set(group_ids).issubset(group_ids_in_db)
            if not group_ids:
                group_ids = group_ids_in_db
                exist_in_groupids = True

            if exist_in_groupids:
                if admin_group_id in group_ids and not remove_admin:
                    admin_group_id_exists_in_group_ids = True

            if (
                    exist_in_groupids and
                    not admin_group_id_exists_in_group_ids
                    or exist_in_groupids
                    and admin_group_id_exists_in_group_ids and remove_admin
            ):

                status_code, _, _, _ = (
                    delete_user_in_groups(self.username, group_ids)
                )
                if status_code == DbCodes.Replaced:
                    msg = (
                        'Removed group ids: %s from user %s' %
                        (', '.join(group_ids), self.username)
                    )
                    results[ApiResultKeys.GENERIC_STATUS_CODE] = (
                        GenericCodes.ObjectDeleted
                    )
                    results[ApiResultKeys.VFENSE_STATUS_CODE] = (
                        GroupCodes.RemovedUsersFromGroup
                    )
                    results[ApiResultKeys.MESSAGE] = msg
                    results[ApiResultKeys.UPDATED_IDS] = [self.username]

                elif status_code == DbCodes.Unchanged:
                    msg = (
                        'Group ids: %s do not exist for user %s' %
                        (', '.join(group_ids), self.username)
                    )
                    results[ApiResultKeys.GENERIC_STATUS_CODE] = (
                        GenericCodes.ObjectUnchanged
                    )
                    results[ApiResultKeys.VFENSE_STATUS_CODE] = (
                        GroupCodes.GroupsUnchanged
                    )
                    results[ApiResultKeys.MESSAGE] = msg
                    results[ApiResultKeys.UNCHANGED_IDS] = [self.username]

            elif admin_group_id_exists_in_group_ids and not remove_admin:
                msg = (
                    'Can not remove the special group %s from user %s' %
                        (', '.join(group_ids), self.username)
                )
                results[ApiResultKeys.GENERIC_STATUS_CODE] = (
                    GenericCodes.InvalidId
                )
                results[ApiResultKeys.VFENSE_STATUS_CODE] = (
                    GroupFailureCodes.CantRemoveAdminFromGroup
                )
                results[ApiResultKeys.MESSAGE] =  msg
                results[ApiResultKeys.UNCHANGED_IDS] = [self.username]

            else:
                msg = (
                    'groups %s do not exist for user %s' %
                    (' and '.join(group_ids), self.username)
                )
                results[ApiResultKeys.GENERIC_STATUS_CODE] = (
                    GenericCodes.InvalidId
                )
                results[ApiResultKeys.VFENSE_STATUS_CODE] = (
                    GroupFailureCodes.GroupDoesNotExistForUser
                )
                results[ApiResultKeys.MESSAGE] =  msg
                results[ApiResultKeys.INVALID_IDS] = group_ids
                results[ApiResultKeys.UNCHANGED_IDS] =  [self.username]

        else:
            msg = 'User does not exist %s' % (self.username)
            results[ApiResultKeys.GENERIC_STATUS_CODE] = (
                GenericCodes.InvalidId
            )
            results[ApiResultKeys.VFENSE_STATUS_CODE] = (
                GroupFailureCodes.InvalidGroupId
            )
            results[ApiResultKeys.MESSAGE] =  msg
            results[ApiResultKeys.INVALID_IDS] =  [self.username]
            results[ApiResultKeys.UNCHANGED_IDS] =  [self.username]

        return results

    @time_it
    def remove_from_views(self, views=None):
        """Remove a view from a user
        Kwargs:
            views (list): List of views,
                you want to remove from this user

        Basic Usage:
            >>> username = 'tester1'
            >>> views = ['Test View 1']
            >>> manager = UserManager(username)
            >>> manager.remove_from_views(views)

        Returns:
            Dictionary of the status of the operation.
            >>>
            {
                "message": "remove_from_views - removed views from user tester1",
                "vfense_status_code": 14005,
                "updated_ids": [
                    "tester1"
                ],
                "generic_status_code": 1012
            }
        """
        user_exist = self.properties
        results = {}

        if user_exist:
            views_in_db = user_exist[UserKeys.Views]
            views_exist = False
            if not views:
                views = views_in_db
                views_exist = True
            else:
                views_exist = set(views).issubset(views_in_db)

            if views_exist:
                status_code, _, _, _ = (
                    delete_user_in_views(self.username, views)
                )
                if status_code == DbCodes.Replaced:
                    delete_views_in_user(self.username, views)
                    msg = (
                        'removed views from user %s: views = %s' %
                        (self.username, ', '.join(views))
                    )
                    results[ApiResultKeys.MESSAGE] = msg
                    results[ApiResultKeys.GENERIC_STATUS_CODE] = (
                        GenericCodes.ObjectDeleted
                    )
                    results[ApiResultKeys.VFENSE_STATUS_CODE] = (
                        ViewCodes.ViewsRemovedFromUser
                    )
                    results[ApiResultKeys.UPDATED_IDS] = [self.username]

            else:
                msg = (
                    'view names do not exist: %s for user %s' %
                    (', '.join(views), self.username)
                )
                results[ApiResultKeys.GENERIC_STATUS_CODE] = (
                    GenericCodes.DoesNotExist
                )
                results[ApiResultKeys.VFENSE_STATUS_CODE] = (
                    ViewFailureCodes.UsersDoNotExistForView
                )
                results[ApiResultKeys.INVALID_IDS] = [views]
                results[ApiResultKeys.UNCHANGED_IDS] = [self.username]

        else:
            msg = 'Invalid username %s' % (self.username)
            results[ApiResultKeys.MESSAGE] = msg
            results[ApiResultKeys.GENERIC_STATUS_CODE] = (
                GenericCodes.InvalidId
            )
            results[ApiResultKeys.VFENSE_STATUS_CODE] = (
                ViewFailureCodes.InvalidViewName
            )
            results[ApiResultKeys.INVALID_IDS] = [self.username]
            results[ApiResultKeys.UNCHANGED_IDS] = [self.username]

        return results

    @time_it
    def change_password(self, password, new_password):
        """Change password for a user.
        Args:
            password (str): Original password.
            new_password (str): New password.

        Basic Usage:
            >>> username = 'shaolin'
            >>> password = 'my original password'
            >>> new_password = 'my new password'
            >>> manager = UserManager(username)
            >>> manager.change_password(password, new_password)

        Return:
            Dictionary of the status of the operation.
            >>>
            {
                "vfense_status_code": 13004,
                "generic_status_code": 1008,
                "updated_ids": [
                    "global_admin"
                ],
                "message": "Password changed for user global_admin - ",
            }
        """
        user_exist = self.properties
        results = {}
        if user_exist:
            valid_passwd, strength = check_password(new_password)
            original_encrypted_password = (
                self.get_attribute(UserKeys.Password).encode('utf-8')
            )
            original_password_verified = (
                Crypto().verify_bcrypt_hash(
                    password, original_encrypted_password
                )
            )
            encrypted_new_password = Crypto().hash_bcrypt(new_password)
            new_password_verified_against_orignal_password = (
                Crypto().verify_bcrypt_hash(
                    new_password, original_encrypted_password
                )
            )
            if (original_password_verified and valid_passwd and
                    not new_password_verified_against_orignal_password):

                user_data = {UserKeys.Password: encrypted_new_password}

                object_status, _, _, _ = (
                    update_user(self.username, user_data)
                )

                if object_status == DbCodes.Replaced:
                    msg = 'Password changed for user %s - ' % (self.username)
                    results[ApiResultKeys.GENERIC_STATUS_CODE] = (
                        GenericCodes.ObjectUpdated
                    )
                    results[ApiResultKeys.VFENSE_STATUS_CODE] = (
                        UserCodes.PasswordChanged
                    )
                    results[ApiResultKeys.UPDATED_IDS] = [self.username]

            elif new_password_verified_against_orignal_password:
                msg = (
                    'New password is the same as the original - user %s - ' %
                    (self.username)
                )
                results[ApiResultKeys.GENERIC_STATUS_CODE] = (
                    GenericFailureCodes.FailedToUpdateObject
                )
                results[ApiResultKeys.VFENSE_STATUS_CODE] = (
                    UserFailureCodes.NewPasswordSameAsOld
                )
                results[ApiResultKeys.UNCHANGED_IDS] = [self.username]

            elif original_password_verified and not valid_passwd:
                msg = (
                    'New password is to weak for user %s - ' %
                    (self.username)
                )
                results[ApiResultKeys.GENERIC_STATUS_CODE] = (
                    GenericFailureCodes.FailedToUpdateObject
                )
                results[ApiResultKeys.VFENSE_STATUS_CODE] = (
                    UserFailureCodes.WeakPassword
                )
                results[ApiResultKeys.UNCHANGED_IDS] = [self.username]

            elif not original_password_verified:
                msg = (
                    'Password not verified for user %s - ' %
                    (self.username)
                )
                results[ApiResultKeys.GENERIC_STATUS_CODE] = (
                    GenericFailureCodes.FailedToUpdateObject
                )
                results[ApiResultKeys.VFENSE_STATUS_CODE] = (
                    UserFailureCodes.InvalidPassword
                )
                results[ApiResultKeys.UNCHANGED_IDS] = [self.username]


        else:
            msg = 'User %s does not exist - ' % (self.username)
            results[ApiResultKeys.GENERIC_STATUS_CODE] = (
                GenericCodes.InvalidId
            )
            results[ApiResultKeys.VFENSE_STATUS_CODE] = (
                UserFailureCodes.UserNameDoesNotExist
            )
            results[ApiResultKeys.UNCHANGED_IDS] = [self.username]

        results[ApiResultKeys.MESSAGE] = msg

        return results

    @time_it
    def reset_password(self, password):
        """Change password for a user.
        Args:
            password (str): Original password.

        Basic Usage:
            >>> username = 'global_admin'
            >>> password = 'My n3w p@ssword'
            >>> manager = UserManager(username)
            >>> manager.reset_password(password)

        Return:
            Dictionary of the status of the operation.
            >>>
            {
                "message": "Password changed for user global_admin - ",
                "vfense_status_code": 13004,
                "updated_ids": [
                    "global_admin"
                ],
                "generic_status_code": 1008
            }
        """
        user_exist = self.properties
        results = {}
        if user_exist:
            valid_passwd, strength = check_password(password)
            encrypted_password = Crypto().hash_bcrypt(password)
            if valid_passwd:
                user_data = {UserKeys.Password: encrypted_password}

                object_status, _, _, _ = (
                    update_user(self.username, user_data)
                )

                if object_status == DbCodes.Replaced:
                    msg = 'Password changed for user %s - ' % (self.username)
                    generic_status_code = GenericCodes.ObjectUpdated
                    vfense_status_code = UserCodes.PasswordChanged
                    results[ApiResultKeys.UPDATED_IDS] = [self.username]

            else:
                msg = (
                    'New password is to weak for user %s - ' %
                    (self.username)
                )
                generic_status_code = GenericFailureCodes.FailedToUpdateObject
                vfense_status_code = UserFailureCodes.WeakPassword
                results[ApiResultKeys.UNCHANGED_IDS] = [self.username]

        else:
            msg = 'User %s does not exist - ' % (self.username)
            generic_status_code = GenericCodes.InvalidId
            vfense_status_code = UserFailureCodes.UserNameDoesNotExist
            results[ApiResultKeys.UNCHANGED_IDS] = [self.username]

        results[ApiResultKeys.GENERIC_STATUS_CODE] = generic_status_code
        results[ApiResultKeys.VFENSE_STATUS_CODE] = vfense_status_code
        results[ApiResultKeys.MESSAGE] = msg
        results[ApiResultKeys.DATA] = []

        return results


    @time_it
    def change_view(self, user):
        """Change current or default view.
        Args:
            user (User): Original password.
        Basic Usage:
            >>> from vFense.user import User
            >>> from vFense.user.manager import UserManager
            >>> username = 'global_admin'
            >>> current_view = 'global'
            >>> user = (
                    User(
                        username, current_view=current_view,
                    )
                )
            >>> manager = UserManager(username)
            >>> manager.change_view(user)

        Return:
            Dictionary of the status of the operation.
            >>>
            {
                "vfense_status_code": 13001,
                "message": "User global_admin was updated - ",
                "data": [
                    {
                        "current_view": "global"
                    }
                ],
                "updated_ids": [
                    "global_admin"
                ],
                "generic_status_code": 1008
            }
        """
        user_exist = self.properties
        status = self.change_view.func_name + ' - '
        results = {}
        results[ApiResultKeys.DATA] = []
        view = None
        views_in_db = (
            fetch_views_for_user(self.username)
        )
        data = user.to_dict_non_null()
        data.pop(UserKeys.UserName, None)
        data.pop(UserKeys.Password, None)
        if data.get(UserKeys.CurrentView):
            view = data.get(UserKeys.CurrentView)

        elif data.get(UserKeys.DefaultView):
            view = data.get(UserKeys.DefaultView)

        if user_exist and view:

            if user_exist[UserKeys.Global] and view:
                results = self.__edit_user_properties(user)
            elif view in views_in_db:
                results = self.__edit_user_properties(user)
            else:
                msg = (
                    'View %s is not valid for user %s' %
                    (view, self.username)
                )
                results[ApiResultKeys.MESSAGE] = status + msg
                results[ApiResultKeys.GENERIC_STATUS_CODE] = (
                    GenericCodes.InvalidId
                )
                results[ApiResultKeys.VFENSE_STATUS_CODE] = (
                    UserFailureCodes.FailedToUpdateUser
                )
        elif not user_exist and view:
            msg = (
                'User %s is not valid' % (self.username)
            )
            results[ApiResultKeys.MESSAGE] = status + msg
            results[ApiResultKeys.GENERIC_STATUS_CODE] = (
                GenericCodes.InvalidId
            )
            results[ApiResultKeys.VFENSE_STATUS_CODE] = (
                UserFailureCodes.FailedToUpdateUser
            )
        else:
            msg = (
                'current_view or default_view ' +
                'was not set in the User instance'
            )
            results[ApiResultKeys.MESSAGE] = status + msg
            results[ApiResultKeys.GENERIC_STATUS_CODE] = (
                GenericCodes.InvalidId
            )
            results[ApiResultKeys.VFENSE_STATUS_CODE] = (
                UserFailureCodes.FailedToUpdateUser
            )

        return results


    @time_it
    def change_full_name(self, user):
        """Change current or default view.
        Args:
            user (User): A user instance filled out with the
                appropriate fields.
        Basic Usage:
            >>> from vFense.user import User
            >>> from vFense.user.manager import UserManager
            >>> username = 'global_admin'
            >>> user = (
                    User(
                        username, full_name="Shaolin Administrator",
                    )
                )
            >>> manager = UserManager(username)
            >>> manager.change_full_name(user)

        Return:
            Dictionary of the status of the operation.
            >>>
            {
                "vfense_status_code": 13001,
                "message": "__edit_user_properties - User global_admin was updated - ",
                "data": [
                    {
                        "full_name": "Shaolin Administrator"
                    }
                ],
                "updated_ids": [
                    "global_admin"
                ],
                "generic_status_code": 1008
            }
        """
        status = self.change_full_name.func_name + ' - '
        results = {}

        if isinstance(user, User):
            if user.full_name:
                results = self.__edit_user_properties(user)

            else:
                msg = (
                    'Full name was not set in User instance for user %s - '
                    % (self.username)
                )
                results[ApiResultKeys.MESSAGE] = status + msg
                results[ApiResultKeys.DATA] = []
                results[ApiResultKeys.GENERIC_STATUS_CODE] = (
                    GenericCodes.UpdateFailed
                )
                results[ApiResultKeys.VFENSE_STATUS_CODE] = (
                    GenericCodes.InvalidValue
                )
                results[ApiResultKeys.UNCHANGED_IDS] = [self.username]


        else:
            msg = 'An instance of User was not passed - ' % (type(user))
            results[ApiResultKeys.MESSAGE] = status + msg
            results[ApiResultKeys.DATA] = []
            results[ApiResultKeys.GENERIC_STATUS_CODE] = (
                GenericCodes.UpdateFailed
            )
            results[ApiResultKeys.VFENSE_STATUS_CODE] = (
                GenericCodes.InvalidValue
            )
            results[ApiResultKeys.UNCHANGED_IDS] = [self.username]

        return results


    @time_it
    def change_email(self, user):
        """Change current or default view.
        Args:
            user (User): A user instance filled out with the
                appropriate fields.

        Basic Usage:
            >>> from vFense.user import User
            >>> from vFense.user.manager import UserManager
            >>> username = 'global_admin'
            >>> user = (
                    User(
                        username, email="shaolin_admin@shaolin.com",
                    )
                )
            >>> manager = UserManager(username)
            >>> manager.change_email(user)

        Returns:
            >>>
            {
                "vfense_status_code": 13001,
                "message": " User global_admin was updated - ",
                "data": [
                    {
                        "email": "shaolin_admin@shaolin.com"
                    }
                ],
                "updated_ids": [
                    "global_admin"
                ],
                "generic_status_code": 1008
            }
        """
        results = {}

        if isinstance(user, User):
            if user.email:
                results = self.__edit_user_properties(user)

            else:
                msg = (
                    'email was not set in User instance for user %s - '
                    % (self.username)
                )
                results[ApiResultKeys.MESSAGE] = msg
                results[ApiResultKeys.DATA] = []
                results[ApiResultKeys.GENERIC_STATUS_CODE] = (
                    GenericCodes.UpdateFailed
                )
                results[ApiResultKeys.VFENSE_STATUS_CODE] = (
                    GenericCodes.InvalidValue
                )
                results[ApiResultKeys.UNCHANGED_IDS] = [self.username]


        else:
            msg = 'An instance of User was not passed - ' % (type(user))
            results[ApiResultKeys.MESSAGE] = msg
            results[ApiResultKeys.DATA] = []
            results[ApiResultKeys.GENERIC_STATUS_CODE] = (
                GenericCodes.UpdateFailed
            )
            results[ApiResultKeys.VFENSE_STATUS_CODE] = (
                GenericCodes.InvalidValue
            )
            results[ApiResultKeys.UNCHANGED_IDS] = [self.username]

        return results


    @time_it
    def __edit_user_properties(self, user):
        """ Edit the properties of a view.
        Args:
            user (User): The User instance with all of its properties.

        Basic Usage:
            >>> from vFense.user import User
            >>> from vFense.user.manager import UserManager
            >>> username = 'global_admin'
            >>> user = (
                    User(username, full_name='Shaolin Administrator')
                )
            >>> manager = UserManager(username)
            >>> manager.__edit_user_properties(user)

        Return:
            Dictionary of the status of the operation.
            >>>
            {
                "vfense_status_code": 13001,
                "message": "__edit_user_properties - User global_admin was updated - ",
                "data": [
                    {
                        "full_name": "Shaolin Administrator"
                    }
                ],
                "updated_ids": [
                    "global_admin"
                ],
                "generic_status_code": 1008
            }
        """

        user_exist = self.properties
        results = {}
        data = {}
        results[ApiResultKeys.DATA] = []
        if user_exist:
            invalid_fields = user.get_invalid_fields()
            data = user.to_dict_non_null()
            data.pop(UserKeys.UserName, None)
            data.pop(UserKeys.Password, None)
            if not invalid_fields:
                object_status, _, _, _ = (
                    update_user(self.username, data)
                )

                if object_status == DbCodes.Replaced:
                    msg = 'User %s was updated - ' % (self.username)
                    generic_status_code = GenericCodes.ObjectUpdated
                    vfense_status_code = UserCodes.UserUpdated
                    results[ApiResultKeys.UPDATED_IDS] = [self.username]
                    results[ApiResultKeys.DATA] = [data]

                elif object_status == DbCodes.Unchanged:
                    msg = 'User %s was not updated - ' % (self.username)
                    generic_status_code = GenericCodes.ObjectUnchanged
                    vfense_status_code = UserCodes.UserUnchanged
                    results[ApiResultKeys.UNCHANGED_IDS] = [self.username]

            else:
                generic_status_code = GenericCodes.InvalidId
                vfense_status_code = UserFailureCodes.FailedToUpdateUser
                msg = 'User %s properties were invalid - ' % (self.username)
                results[ApiResultKeys.UNCHANGED_IDS] = [self.username]

        else:
            generic_status_code = GenericCodes.InvalidId
            vfense_status_code = UserFailureCodes.UserNameDoesNotExist
            msg = 'User %s does not exist - ' % (self.username)
            results[ApiResultKeys.UNCHANGED_IDS] = [self.username]

        results[ApiResultKeys.GENERIC_STATUS_CODE] = generic_status_code
        results[ApiResultKeys.VFENSE_STATUS_CODE] = vfense_status_code
        results[ApiResultKeys.MESSAGE] = msg

        return results
