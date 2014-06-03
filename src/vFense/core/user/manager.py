import logging
from vFense import VFENSE_LOGGING_CONFIG
from vFense.errorz._constants import ApiResultKeys
from vFense.core.user import User
from vFense.core.user._db_model import UserKeys
from vFense.core.user._constants import DefaultUsers
from vFense.core.group._db_model import GroupKeys, GroupsPerUserKeys
from vFense.core.group._db import (
    delete_groups_from_user,
    fetch_group_by_name, user_exist_in_group,
    fetch_groupids_for_user, fetch_group
)

from vFense.core.group._constants import DefaultGroups

from vFense.core.view._db import (
    users_exists_in_view, insert_user_per_view,
    delete_user_in_views, fetch_views_for_user,
    fetch_all_view_names, update_usernames_for_views
)

from vFense.core.view._db_model import ViewKeys
from vFense.core.view._constants import Defaultviews

from vFense.core.user._db import (
    insert_user, fetch_user, fetch_users,
    delete_user, update_user, fetch_user_and_all_properties,
    fetch_users_and_all_properties, delete_users, user_status_toggle,
    update_views_for_user
)

from vFense.core.group._db import user_exist_in_group, insert_group_per_user, \
    delete_users_in_group

from vFense.core.group.groups import validate_group_ids, \
    add_user_to_groups, remove_groups_from_user, get_group

from vFense.core.view.views import get_view, \
    add_user_to_views, remove_views_from_user, \
    validate_views

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
            user_atrribute (str): The attribute you want to retrieve.
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
            user_key = user_data.get(user_attribute)

        return user_key

    @time_it
    def _all_attributes_for_user(self):
        """Retrieve a user and all of its properties by username.
        Basic Usage:
            >>> from vFense.user.manager import UserManager
            >>> username = 'admin'
            >>> user._all_attributes_for_user()

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
                    "rv_status_code": 13001,
                    "updated_ids": [
                        "tester"
                    ],
                    "unchanged_ids": [],
                    "message": "toggle_user_status - user tester is enabled",
                    "data": [],
                }
        """
        status = self.toggle_status.func_name + ' - '
        status_code, _, _, _ = (
            user_status_toggle(self.username)
        )
        self.properties = self._all_attributes_for_user()
        if status_code == DbCodes.Replaced:
            if self.properties[UserKeys.Enabled]:
                msg = 'user %s is enabled' % (self.username)

            else:
                msg = 'user %s is disabled' % (self.username)

            generic_status_code = GenericCodes.ObjectUpdated
            vfense_status_code = UserCodes.UserUpdated

        elif status_code == DbCodes.Skipped:
            msg = 'user %s is invalid' % (self.username)
            generic_status_code = GenericCodes.InvalidId
            vfense_status_code = UserFailureCodes.InvalidUserName


        results = {
            ApiResultKeys.DB_STATUS_CODE: status_code,
            ApiResultKeys.GENERIC_STATUS_CODE: generic_status_code,
            ApiResultKeys.VFENSE_STATUS_CODE: vfense_status_code,
            ApiResultKeys.MESSAGE: status + msg,
            ApiResultKeys.UPDATED_IDS: [self.username],
            ApiResultKeys.DATA: [],
        }

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
            >>> username = 'shaolin'
            >>> fullname = 'testing 4 life'
            >>> password = 'Testing123#'
            >>> group_ids = ['8757b79c-7321-4446-8882-65457f28c78b']
            >>> view = 'default'
            >>> email = 'test@test.org'
            >>> enabled = True
            >>> is_global = False
            >>> user = (
                    User(
                        username, password, email=email,
                        enabled=enabled, is_global=is_global
                    )
                )
            >>> manager = UserManager(username)
            >>> manager.create(user, view, group_ids)

        Return:
            Dictionary of the status of the operation.
            {
                'rv_status_code': 1010,
                'errors': [],
                'message': 'None - create user testing123 was created',
                'data': {
                    'current_view': 'default',
                    'full_name': 'tester4life',
                    'default_view': 'default',
                    'password': '$2a$12$HFAEabWwq8Hz0TIZ.jV59eHLoy0DdogdtR9TgvZnBCye894oljZOe',
                    'user_name': 'testing123',
                    'enabled': 'yes',
                    'email': 'test@test.org'
                }
            }
        """
        status = self.create.func_name + ' - '
        user_exist = self.properties
        generated_ids = []
        generic_status_code = 0
        vfense_status_code = 0
        errors = []
        user_data = user.to_dict()
        if isinstance(user, User) and not user_exist:
            invalid_fields = user.get_invalid_fields()

            if invalid_fields:
                generic_status_code = GenericFailureCodes.FailedToCreateObject
                vfense_status_code = UserFailureCodes.FailedToCreateUser
                errors = invalid_fields

            else:
                encrypted_password = Crypto().hash_bcrypt(user.password)
                user_data[UserKeys.Password] = encrypted_password
                current_view_is_valid = get_view(user.current_view)
                default_view_is_valid = get_view(user.default_view)
                validated_groups, _, invalid_groups = (
                    validate_group_ids(
                        group_ids, user.current_view, user.is_global
                    )
                )

                if (
                        current_view_is_valid and
                        default_view_is_valid and
                        validated_groups
                    ):
                    object_status, _, _, generated_ids = (
                        insert_user(user_data)
                    )

                    if object_status == DbCodes.Inserted:
                        msg = 'user name %s created' % (self.username)
                        self.properties = self._user_attributes()
                        generated_ids.append(self.username)
                        views = (
                            list(
                                set(
                                    [
                                        user.current_view,
                                        user.default_view
                                    ]
                                )
                            )
                        )
                        if user.is_global:
                            views = fetch_all_view_names()

                        self.add_to_views(views)
                        self.add_to_groups(group_ids)
                        generic_status_code = GenericCodes.ObjectCreated
                        vfense_status_code = UserCodes.UserCreated
                        user_data.pop(UserKeys.Password)

                elif (
                        not current_view_is_valid or
                        not default_view_is_valid and
                        validated_groups
                    ):
                    msg = (
                        'view name %s does not exist' %
                        (user.current_view)
                    )
                    generic_status_code = GenericCodes.InvalidId
                    vfense_status_code = (
                        ViewFailureCodes.ViewDoesNotExist
                    )

                elif (
                        current_view_is_valid or
                        default_view_is_valid and
                        not validated_groups
                    ):
                    msg = 'group ids %s does not exist' % (invalid_groups)
                    generic_status_code = GenericCodes.InvalidId
                    vfense_status_code = GroupFailureCodes.InvalidGroupId

                else:
                    group_error = (
                        'group ids %s does not exist' % (invalid_groups)
                    )
                    view_error = (
                        'view name %s does not exist' %
                        (user.current_view)
                    )
                    msg = group_error + ' and ' + view_error
                    generic_status_code = GenericFailureCodes.FailedToCreateObject
                    vfense_status_code = UserFailureCodes.FailedToCreateUser

        elif user_exist and isinstance(user, User):
            msg = 'username %s already exists' % (self.username)
            generic_status_code = GenericCodes.ObjectExists
            vfense_status_code = UserFailureCodes.UserNameExists

        else:
            msg = 'Please pass a User instance, not a %s' % (str(type(user)))
            generic_status_code = GenericFailureCodes.FailedToCreateObject
            vfense_status_code = UserFailureCodes.FailedToCreateUser

        results = {
            ApiResultKeys.GENERIC_STATUS_CODE: generic_status_code,
            ApiResultKeys.VFENSE_STATUS_CODE: vfense_status_code,
            ApiResultKeys.MESSAGE: status + msg,
            ApiResultKeys.GENERATED_IDS: generated_ids,
            ApiResultKeys.ERRORS: errors,
            ApiResultKeys.DATA: [user_data],
        }

        return results


    @time_it
    def add_to_views(self, views=None):
        """Add a multiple views to a user
        Kwargs:
            views (list): List of views this user will be added too.
                default = None

        Basic Usage:
            >>> from vFense.user.manager import UserManager
            >>> username = 'shaolin'
            >>> views = ['TopPatch', 'vFense']
            >>> manager = UserManager(username)
            >>> manager.add_to_views(views)

        Returns:
            Dictionary of the status of the operation.
            {
                'rv_status_code': 1017,
                'message': "None - add_user_to_views - view names existed 'default', 'TopPatch', 'vFense' unchanged",
                'data': []
            }
        """
        if isinstance(views, str):
            views = views.split(',')

        views_are_valid = validate_views(views)
        if self.properties[UserKeys.Global]:
            views = fetch_all_view_names()

        results = {}
        user_exist = self.properties
        status = self.add_to_views.func_name + ' - '
        if views_are_valid[0] and user_exist:
            status_code, _, _, _ = update_views_for_user(self.username, views)
            if status_code == DbCodes.Replaced:
                update_usernames_for_views(views, [self.username])
                msg = (
                    'user %s added to %s' % (
                        self.username, ' and '.join(views)
                    )
                )
                results[ApiResultKeys.MESSAGE] = status + msg
                results[ApiResultKeys.GENERIC_STATUS_CODE] = (
                    GenericCodes.ObjectCreated
                )
                results[ApiResultKeys.VFENSE_STATUS_CODE] = (
                    ViewCodes.viewsAddedToUser
                )

        elif not user_exist:
            msg = 'User name is invalid: %s' % (self.username)
            results[ApiResultKeys.MESSAGE] = status + msg
            results[ApiResultKeys.GENERIC_STATUS_CODE] = (
                GenericCodes.InvalidId
            )
            results[ApiResultKeys.VFENSE_STATUS_CODE] = (
                UserFailureCodes.UserNameDoesNotExist
            )

        elif not views_are_valid[0]:
            msg = (
                'View names are invalid: %s' % (
                    ' and '.join(views_are_valid[2])
                )
            )
            results[ApiResultKeys.MESSAGE] = status + msg
            results[ApiResultKeys.GENERIC_STATUS_CODE] = (
                GenericCodes.InvalidId
            )
            results[ApiResultKeys.VFENSE_STATUS_CODE] = (
                ViewFailureCodes.InvalidViewName
            )

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
            >>> username = 'shaolin'
            >>> group_ids = ['0834e656-27a5-4b13-ba56-635797d0d1fc']
            >>> manager = UserManager(username)
            >>> manager.add_to_groups(group_ids)

        Returns:
            Returns the results in a dictionary
        {
            'rv_status_code': 1010,
            'message': "None - groups per user [u'ee54820c-cb4e-46a1-9d11-73afe8c4c4e3'] was created",
            'data': {
                'group_name': u'FooLah',
                'user_name': 'alien',
                'group_id': '0834e656-27a5-4b13-ba56-635797d0d1fc',
                'view': 'default'
            }
        }
        """
        status = add_user_to_groups.func_name + ' - '
        groups_are_valid = (
            validate_group_ids(
                group_ids, is_global=self.properties[UserKeys.Global]
            )
        )
        user_exist = self.properties
        results = None
        generated_ids = []
        users_group_exist = []
        generic_status_code = 0
        vfense_status_code = 0
        if groups_are_valid[0] and user_exist:
            data_list = []
            for group_id in group_ids:
                group = fetch_group(group_id)
                user_in_group = (
                    user_exist_in_group(self.username, group_id)
                )
                if not user_in_group:
                    data_to_add = (
                        {
                            GroupsPerUserKeys.ViewName: (
                                group.get(GroupKeys.ViewName)
                            ),
                            GroupsPerUserKeys.UserName: self.username,
                            GroupsPerUserKeys.GroupName: (
                                group[GroupKeys.GroupName]
                            ),
                            GroupsPerUserKeys.Global: group[GroupKeys.Global],
                            GroupsPerUserKeys.GroupId: group_id
                        }
                    )
                    data_list.append(data_to_add)

                else:
                    users_group_exist.append(group_id)

            if len(data_list) == len(group_ids):
                status_code, _, _, generated_ids = (
                    insert_group_per_user(data_list)
                )

                if status_code == DbCodes.Inserted:
                    msg = 'user %s add to groups' % (self.username)
                    generic_status_code = GenericCodes.ObjectCreated
                    vfense_status_code = GroupCodes.GroupCreated

            else:
                msg = (
                    'user %s is already in groups %s' % (
                        self.username, ' and '.join(users_group_exist)
                    )
                )
                status_code = DbCodes.Skipped
                generic_status_code = GenericCodes.ObjectExists
                vfense_status_code = GroupFailureCodes.GroupExistForUser

        elif not groups_are_valid[0]:
            msg = (
                'Group Ids are invalid: %s' % (
                    ' and '.join(groups_are_valid[2])
                )
            )
            status_code = DbCodes.Errors
            generic_status_code = GenericCodes.InvalidId
            vfense_status_code = GroupFailureCodes.InvalidGroupId

        elif not user_exist:
            msg = 'User name is invalid: %s' % (self.username)
            status_code = DbCodes.Errors
            generic_status_code = GenericCodes.InvalidId
            vfense_status_code = UserFailureCodes.InvalidUserName

        results = {
            ApiResultKeys.DB_STATUS_CODE: status_code,
            ApiResultKeys.GENERIC_STATUS_CODE: generic_status_code,
            ApiResultKeys.VFENSE_STATUS_CODE: vfense_status_code,
            ApiResultKeys.GENERATED_IDS: generated_ids,
            ApiResultKeys.MESSAGE: status + msg,
            ApiResultKeys.DATA: [],
        }

        return results

    @time_it
    def remove(self):
        """Remove a user from vFense

        Basic Usage:
            >>> from vFense.user.manager import UserManager
            >>> username = 'shaolin'
            >>> manager = UserManager(username)
            >>> manager.remove()

        Return:
            Dictionary of the status of the operation.
        """
        user_exist = self.properties
        status = self.remove.func_name + ' - '
        username_not_to_delete = []
        username_to_delete = []
        results = {}
        if user_exist and self.username != DefaultUsers.ADMIN:
            self.remove_from_groups()
            self.remove_from_views()
            username_to_delete.append(self.username)

            object_status, _, _, _ = (
                delete_user(self.username)
            )

            if object_status == DbCodes.Deleted:
                results[ApiResultKeys.DELETED_IDS] = (
                    username_to_delete
                )
                results[ApiResultKeys.GENERIC_STATUS_CODE] = (
                    GenericCodes.ObjectDeleted
                )
                results[ApiResultKeys.VFENSE_STATUS_CODE] = (
                    UserCodes.UserDeleted
                )
                msg = 'User removed %s' % (self.username)

        elif self.username == DefaultUsers.ADMIN:
            msg = 'Can not delete the %s user' % (self.username)
            username_not_to_delete.append(self.username)
            results[ApiResultKeys.GENERIC_STATUS_CODE] = (
                GenericCodes.CouldNotBeDeleted
            )
            results[ApiResultKeys.VFENSE_STATUS_CODE] = (
                UserFailureCodes.AdminUserCanNotBeDeleted
            )

        else:
            msg = 'User does not exist %s' % (self.username)
            username_not_to_delete.append(self.username)
            results[ApiResultKeys.GENERIC_STATUS_CODE] = (
                GenericCodes.InvalidId
            )
            results[ApiResultKeys.VFENSE_STATUS_CODE] = (
                UserFailureCodes.UserNameDoesNotExist
            )

        results[ApiResultKeys.DELETED_IDS] = (
            username_to_delete
        )
        results[ApiResultKeys.UNCHANGED_IDS] = (
            username_not_to_delete
        )
        results[ApiResultKeys.DATA] = []
        results[ApiResultKeys.MESSAGE] = status + msg

        return results

    @time_it
    def remove_from_groups(self, group_ids=None):
        """Remove a group from a user
        Kwargs:
            group_ids(list): List of group_ids.

        Basic Usage:
            >>> username = 'shaolin'
            >>> group_ids = ['0834e656-27a5-4b13-ba56-635797d0d1fc', '8757b79c-7321-4446-8882-65457f28c78b']
            >>> manager = UserManager(username)
            >>> manager.remove_from_groups(group_ids)

        Returns:
            Returns the results in a dictionary
            {
                'rv_status_code': 1004,
                'message': 'None - remove_groups_from_user - group ids: 0834e656-27a5-4b13-ba56-635797d0d1fc, 8757b79c-7321-4446-8882-65457f28c78b does not exist',
            }
        """
        status = self.remove_from_groups.func_name + ' - '
        exist_in_groupids = False
        admin_group_id = None
        admin_group_id_exists_in_group_ids = False
        group_ids_in_db = fetch_groupids_for_user(self.username)
        if self.username == DefaultUsers.ADMIN:
            admin_group_id = fetch_group_by_name(
                DefaultGroups.ADMIN, Defaultviews.DEFAULT,
                GroupKeys.GroupId)[GroupKeys.GroupId]

        if group_ids:
            exist_in_groupids = set(group_ids).issubset(group_ids_in_db)
        if not group_ids:
            group_ids = group_ids_in_db
            exist_in_groupids = True

        if exist_in_groupids:
            if not admin_group_id in group_ids:
                msg = 'group ids: ' + 'and '.join(group_ids)

            else:
                admin_group_id_exists_in_group_ids = True
                msg = (
                    'Cannot remove the %s group from the %s user' %
                    (DefaultGroups.ADMIN, DefaultUsers.ADMIN)
                )

        if exist_in_groupids and not admin_group_id_exists_in_group_ids:

            status_code, _, _, _ = (
                delete_groups_from_user(self.username, group_ids)
            )
            if status_code == DbCodes.Deleted:
                generic_status_code = GenericCodes.ObjectDeleted
                vfense_status_code = GroupCodes.GroupsRemovedFromUser

            elif status_code == DbCodes.Unchanged:
                generic_status_code = GenericCodes.ObjectUnchanged
                vfense_status_code = GroupCodes.GroupUnchanged

            elif status_code == DbCodes.Skipped:
                generic_status_code = GenericCodes.InvalidId
                vfense_status_code = GroupFailureCodes.InvalidGroupId

        elif admin_group_id_exists_in_group_ids:
            status_code = DbCodes.Skipped
            generic_status_code = GenericCodes.InvalidId
            vfense_status_code = GroupFailureCodes.CantRemoveAdminFromGroup

        else:
            msg = (
                'groups %s do not exist for user %s' %
                (' and '.join(group_ids), self.username)
            )
            status_code = DbCodes.Skipped
            generic_status_code = GenericCodes.InvalidId
            vfense_status_code = GroupFailureCodes.GroupDoesNotExistForUser

        results = {
            ApiResultKeys.DB_STATUS_CODE: status_code,
            ApiResultKeys.GENERIC_STATUS_CODE: generic_status_code,
            ApiResultKeys.VFENSE_STATUS_CODE: vfense_status_code,
            ApiResultKeys.MESSAGE: status + msg,
            ApiResultKeys.DATA: [],
        }

        return results

    @time_it
    def remove_from_views(self, views=None):
        """Remove a view from a user
        Kwargs:
            views (list): List of views,
                you want to remove from this user

        Basic Usage:
            >>> username = 'shaolin'
            >>> views = ['test']
            >>> manager = UserManager(username)
            >>> manager.remove_from_views(views)

        Returns:
            Dictionary of the status of the operation.
            >>>
            {
                'rv_status_code': 1004,
                'message': 'None - remove_views_from_user - removed views from user alien: TopPatch and vFense does not exist',
            }
        """
        status = self.remove_from_views.func_name + ' - '
        views_in_db = fetch_views_for_user(self.username)
        exist = False
        if not views:
            views = views_in_db
            exist = True
        else:
            exist = set(views).issubset(views_in_db)

        if exist:
            status_code, count, errors, generated_ids = (
                delete_user_in_views(self.username, views)
            )
            if status_code == DbCodes.Deleted:
                msg = 'removed views from user %s' % (self.username)
                generic_status_code = GenericCodes.ObjectDeleted
                vfense_status_code = ViewCodes.viewsRemovedFromUser

            elif status_code == DbCodes.Skipped:
                msg = 'invalid view name or invalid username'
                generic_status_code = GenericCodes.InvalidId
                vfense_status_code = ViewFailureCodes.InvalidViewName

            elif status_code == DbCodes.DoesNotExist:
                msg = 'view name or username does not exist'
                generic_status_code = GenericCodes.DoesNotExist
                vfense_status_code = (
                    ViewFailureCodes.UsersDoNotExistForView
                )

        else:
            msg = (
                'view names do not exist: %s' %
                (', '.join(views))
            )
            generic_status_code = GenericCodes.DoesNotExist
            vfense_status_code = ViewFailureCodes.UsersDoNotExistForView

        results = {
            ApiResultKeys.DB_STATUS_CODE: status_code,
            ApiResultKeys.GENERIC_STATUS_CODE: generic_status_code,
            ApiResultKeys.VFENSE_STATUS_CODE: vfense_status_code,
            ApiResultKeys.MESSAGE: status + msg,
            ApiResultKeys.DATA: [],
        }

        return(results)

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
            {
                'uri': None,
                'rv_status_code': 1008,
                'http_method': None,
                'http_status': 200,
                'message': 'None - change_password - Password changed for user admin - admin was updated',
                'data': []
            }
        """
        user_exist = self.properties
        status = self.change_password.func_name + ' - '
        generic_status_code = 0
        vfense_status_code = 0
        results = {}
        if user_exist:
            valid_passwd, strength = check_password(new_password)
            original_encrypted_password = (
                password.encode('utf-8')
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
                    generic_status_code = GenericCodes.ObjectUpdated
                    vfense_status_code = UserCodes.PasswordChanged

            elif new_password_verified_against_orignal_password:
                msg = (
                    'New password is the same as the original - user %s - ' %
                    (self.username)
                )
                generic_status_code = GenericFailureCodes.FailedToUpdateObject
                vfense_status_code = UserFailureCodes.NewPasswordSameAsOld

            elif original_password_verified and not valid_passwd:
                msg = (
                    'New password is to weak for user %s - ' %
                    (self.username)
                )
                generic_status_code = GenericFailureCodes.FailedToUpdateObject
                vfense_status_code = UserFailureCodes.WeakPassword

            elif not original_password_verified:
                msg = (
                    'Password not verified for user %s - ' %
                    (self.username)
                )
                generic_status_code = GenericFailureCodes.FailedToUpdateObject
                vfense_status_code = UserFailureCodes.InvalidPassword

            results[ApiResultKeys.UPDATED_IDS] = [self.username]

        else:
            msg = 'User %s does not exist - ' % (self.username)
            generic_status_code = GenericCodes.InvalidId
            vfense_status_code = UserFailureCodes.UserNameDoesNotExist

        results[ApiResultKeys.GENERIC_STATUS_CODE] = generic_status_code
        results[ApiResultKeys.VFENSE_STATUS_CODE] = vfense_status_code
        results[ApiResultKeys.MESSAGE] = status + msg
        results[ApiResultKeys.DATA] = []
        results[ApiResultKeys.UNCHANGED_IDS] = [self.username]

        return results

    @time_it
    def reset_password(self, password):
        """Change password for a user.
        Args:
            password (str): Original password.

        Basic Usage:
            >>> username = 'shaolin'
            >>> password = 'my new password'
            >>> manager = UserManager(username)
            >>> manager.reset_password(password)

        Return:
            Dictionary of the status of the operation.
            {
                'uri': None,
                'rv_status_code': 1008,
                'http_method': None,
                'http_status': 200,
                'message': 'None - change_password - Password changed for user admin - admin was updated',
                'data': []
            }
        """
        user_exist = self.properties
        status = self.reset_password.func_name + ' - '
        generic_status_code = 0
        vfense_status_code = 0
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
        results[ApiResultKeys.MESSAGE] = status + msg
        results[ApiResultKeys.DATA] = []

        return results


    @time_it
    def change_view(self, user):
        """Change current or default view.
        Args:
            password (str): Original password.
        Basic Usage:
            >>> from vFense.user import User
            >>> from vFense.user.manager import UserManager
            >>> username = 'shaolin'
            >>> current_view = 'default'
            >>> user = (
                    User(
                        username, current_view=current_view,
                    )
                )
            >>> manager = UserManager(username)
            >>> manager.change_view(user)
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
        data.pop(UserKeys.UserName)
        data.pop(UserKeys.Password)
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
    def __edit_user_properties(self, user):
        """ Edit the properties of a view.
        Args:
            user (User): The User instance with all of its properties.

        Return:
            Dictionary of the status of the operation.
            {
                'rv_status_code': 1008,
                'message': 'None - edit_user_properties - admin was updated',
                'data': {
                    'full_name': 'vFense Admin'
                }
            }
        """

        user_exist = self.properties
        status = self.__edit_user_properties.func_name + ' - '
        generic_status_code = 0
        vfense_status_code = 0
        results = {}
        data = []
        results[ApiResultKeys.DATA] = data
        if user_exist:
            invalid_fields = user.get_invalid_fields()
            data = user.to_dict_non_null()
            data.pop(UserKeys.UserName)
            data.pop(UserKeys.Password)
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
        results[ApiResultKeys.MESSAGE] = status + msg

        return results
