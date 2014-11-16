import logging
from vFense._constants import VFENSE_LOGGING_CONFIG
from vFense.core.results import ApiResults
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
    delete_user_in_views, fetch_view,
    fetch_all_view_names, update_usernames_for_views
)


from vFense.core.user._db import (
    insert_user, fetch_user, delete_user, update_user,
    user_status_toggle, update_views_for_user, delete_views_in_user
)

from vFense.core.group.groups import (
    validate_group_ids, validate_groups_in_views
)

from vFense.core.view.views import validate_view_names

from vFense.utils.security import Crypto, check_password
from vFense.core.decorators import time_it
from vFense.core.status_codes import (
    GenericFailureCodes, GenericCodes, DbCodes
)
from vFense.core.user.status_codes import (
    UserFailureCodes, UserCodes,
)
from vFense.core.group.status_codes import (
    GroupFailureCodes, GroupCodes,
)
from vFense.core.view.status_codes import (
    ViewFailureCodes, ViewCodes
)


logging.config.fileConfig(VFENSE_LOGGING_CONFIG)
logger = logging.getLogger('vfense_api')


class UserManager(object):
    """All actions that need to be performed on a user,
        is performed with this class
    """
    def __init__(self, user_name):
        self.user_name = user_name
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
            >>> attributes = user._user_attributes()
            >>> attributes.user_name
            u'global_admin'

        Returns:
            Instance of User
            User(u"default_view=global,is_global=True,views=[u'global'],
            current_view=global,date_modified=2014-10-24 11:37:05.583000+00:00,
            enabled=True,full_name=None,
            date_added=2014-10-24 11:37:05.583000+00:00,
            password=None,user_name=global_admin,email=None")
            }
        """
        data = fetch_user(self.user_name, without_fields)
        if data:
            user = User(**data)
        else:
            user = User()
        return user

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
            u'global'

        Return:
            String
        """
        user_data = fetch_user(self.user_name)
        user_key = None
        if user_data:
            user = User(**user_data)
            user_key = user.to_dict().get(user_attribute, None)

        return user_key

    @time_it
    def toggle_status(self):
        """Enable or disable a user
        Basic Usage:
            >>> from vFense.user.manager import UserManager
            >>> user_name = 'admin'
            >>> results = user.toggle_status()
            >>> results.message
            u'user admin is enabled'

        Returns:
            ApiResults instance
            Check vFense.core.results for all the attributes and methods
            for the instance.
        """
        results = ApiResults()
        results.fill_in_defaults()
        status_code, _, _, _ = (
            user_status_toggle(self.user_name)
        )
        self.properties = self._user_attributes()
        if status_code == DbCodes.Replaced:
            if self.properties.enabled:
                msg = 'user {0} is enabled'.format(self.user_name)

            else:
                msg = 'user {0} is disabled'.format(self.user_name)

            results.generic_status_code = GenericCodes.ObjectUpdated
            results.vfense_status_code = UserCodes.UserUpdated
            results.updated_ids.append(self.user_name)

        elif status_code == DbCodes.Skipped:
            msg = 'user {0} is invalid'.format(self.user_name)
            results.generic_status_code = GenericCodes.InvalidId
            results.vfense_status_code = UserFailureCodes.Invaliduser_name

        results.message = msg

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
            >>> user_name = 'global_admin'
            >>> fullname = 'Global Administrator'
            >>> password = 'Testing123#'
            >>> group_ids = ['8757b79c-7321-4446-8882-65457f28c78b']
            >>> user = (
                    User(
                        user_name, password=password,
                        full_name=fullname,
                        enabled=True, is_global=True
                    )
                )
            >>> manager = UserManager(user_name)
            >>> results = manager.create(user, group_ids)
            >>> results.message
            u'user name global_admin created'

        Returns:
            ApiResults instance
            Check vFense.core.results for all the attributes and methods
            for the instance.
        """
        user_exist = self.properties
        user.fill_in_defaults()
        results = ApiResults()
        results.fill_in_defaults()
        if isinstance(user, User) and not user_exist.user_name:
            invalid_fields = user.get_invalid_fields()
            results.errors = invalid_fields

            if invalid_fields:
                results.generic_status_code = (
                    GenericFailureCodes.FailedToCreateObject
                )
                results.vfense_status_code = (
                    UserFailureCodes.FailedToCreateUser
                )

            else:
                user.unencrypted_password = user.password
                user.password = Crypto().hash_bcrypt(user.password)
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
                user.views = views


                if (current_view_is_valid and default_view_is_valid and
                        validated_groups):
                    object_status, _, _, generated_ids = (
                        insert_user(user.to_dict_db())
                    )

                    if object_status == DbCodes.Inserted:
                        msg = 'user name %s created' % (self.user_name)
                        self.properties = self._user_attributes()
                        self.add_to_views(views)
                        self.add_to_groups(group_ids)
                        results.generic_status_code = (
                            GenericCodes.ObjectCreated
                        )
                        results.vfense_status_code = UserCodes.UserCreated
                        results.generated_ids.append(self.user_name)
                        results.message = msg
                        user.password = None
                        results.data.append(user.to_dict())

                elif (not current_view_is_valid or not default_view_is_valid
                      and validated_groups):

                    msg = (
                        'view name {0} does not exist'
                        .format(user.current_view)
                    )
                    results.generic_status_code = GenericCodes.InvalidId
                    results.vfense_status_code = (
                        ViewFailureCodes.ViewDoesNotExist
                    )
                    results.message = msg
                    results.unchanged_ids.append(self.user_name)

                elif (current_view_is_valid or default_view_is_valid and
                      not validated_groups):

                    msg = (
                        'group ids {0} does not exist'.format(invalid_groups)
                    )
                    results.generic_status_code = GenericCodes.InvalidId
                    results.vfense_status_code = (
                        GroupFailureCodes.InvalidGroupId
                    )
                    results.message = msg
                    results.unchanged_ids.append(self.user_name)

                else:
                    group_error = (
                        'group ids {0} does not exist'.format(invalid_groups)
                    )
                    view_error = (
                        'view name {0} does not exist'
                        .format(user.current_view)
                    )
                    msg = group_error + ' and ' + view_error
                    results.generic_status_code = (
                        GenericFailureCodes.FailedToCreateObject
                    )
                    results.vfense_status_code = (
                        UserFailureCodes.FailedToCreateUser
                    )
                    results.message = msg
                    results.unchanged_ids.append(self.user_name)

        elif user_exist.user_name and isinstance(user, User):
            msg = 'user_name {0} already exists'.format(self.user_name)
            results.generic_status_code = GenericCodes.ObjectExists
            results.vfense_status_code = UserFailureCodes.UserNameExists
            results.message = msg
            results.unchanged_ids.append(self.user_name)

        else:
            msg = 'Please pass a User instance, not a %s' % (str(type(user)))
            results.generic_status_code = (
                GenericFailureCodes.FailedToCreateObject
            )
            results.vfense_status_code = (
                GenericFailureCodes.InvalidInstanceType
            )
            results.message = msg
            results.unchanged_ids.append(self.user_name)

        return results


    @time_it
    def add_to_views(self, views=None):
        """Add a multiple views to a user
        Kwargs:
            views (list): List of views this user will be added too.
                default = None

        Basic Usage:
            >>> from vFense.user.manager import UserManager
            >>> user_name = 'tester1'
            >>> views = ['Test View 2']
            >>> manager = UserManager(user_name)
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
        if self.properties.is_global:
            views = fetch_all_view_names()

        results = ApiResults()
        results.fill_in_defaults()
        user_exist = self.properties
        if views_are_valid and user_exist.user_name:
            status_code, _, _, _ = update_views_for_user(self.user_name, views)
            update_usernames_for_views(views, [self.user_name])
            if status_code == DbCodes.Replaced:
                msg = (
                    'user %s was added to %s successfully' % (
                        self.user_name, ', '.join(views)
                    )
                )
                results.message = msg
                results.generic_status_code = GenericCodes.ObjectUpdated
                results.vfense_status_code = ViewCodes.ViewsAddedToUser
                results.updated_ids.append(self.user_name)

            elif status_code == DbCodes.Unchanged:
                msg = (
                    'user %s is already in views: %s' % (
                        self.user_name, ', '.join(views)
                    )
                )
                results.message = msg
                results.generic_status_code = GenericCodes.ObjectUnchanged
                results.vfense_status_code = ViewCodes.ViewUnchanged
                results.unchanged_ids.append(self.user_name)


        elif not user_exist:
            msg = 'User name is invalid: %s' % (self.user_name)
            results.message = msg
            results.generic_status_code = GenericCodes.InvalidId
            results.vfense_status_code = (
                UserFailureCodes.UserNameDoesNotExist
            )
            results.invalid_ids.append(self.user_name)

        elif not views_are_valid[0]:
            msg = (
                'View names are invalid: %s' % (
                    ' and '.join(views_are_valid[2])
                )
            )
            results.message = msg
            results.generic_status_code = GenericCodes.InvalidId
            results.vfense_status_code = ViewFailureCodes.InvalidViewName
            results.invalid_ids.append(views)

        return results

    @time_it
    def add_to_groups(self, group_ids):
        """Add a user into a vFense group
        Args:
            user_name (str):  Name of the user already in vFense.
            view (str): The view this user is part of.
            group_ids (list): List of group ids.

        Basic Usage:
            >>> from vFense.user.manager import UserManager
            >>> user_name = 'tester1'
            >>> group_ids = ['0834e656-27a5-4b13-ba56-635797d0d1fc']
            >>> manager = UserManager(user_name)
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
        results = ApiResults()
        results.fill_in_defaults()
        generated_ids = []
        users_group_exist = []
        if user_exist.user_name:
            is_global = user_exist.is_global
            invalid_groups, valid_global_groups, valid_local_groups = (
                validate_groups_in_views(
                    group_ids, user_exist.views
                )
            )
            if (
                    is_global and
                    len(valid_global_groups) == len(group_ids)
                    or not is_global and
                    len(valid_local_groups) == len(group_ids)
                ):

                status_code, _, _, generated_ids = (
                    add_user_to_groups(group_ids, self.user_name)
                )

                if status_code == DbCodes.Replaced:
                    msg = (
                        'user %s add to groups: %s' %
                        (self.user_name, ', '.join(group_ids))
                    )
                    results.generic_status_code = GenericCodes.ObjectUpdated
                    results.vfense_status_code = UserCodes.UsersAddedToGroup
                    results.updated_ids.append(self.user_name)
                    results.message = msg

                elif status_code == DbCodes.Unchanged:
                    msg = (
                        'user %s is already in groups: %s' % (
                            self.user_name, ', '.join(users_group_exist)
                        )
                    )
                    results.generic_status_code = GenericCodes.ObjectExists
                    results.vfense_status_code = (
                        GroupFailureCodes.GroupExistForUser
                    )
                    results.unchanged_ids.append(self.user_name)
                    results.message = msg


            elif is_global and len(valid_global_groups) != len(group_ids):
                msg = (
                    'Can not add local groups to a global user %s: %s' %
                    (self.user_name, ', '.join(group_ids))
                )
                results.generic_status_code = GenericCodes.InvalidId
                results.vfense_status_code = (
                    UserFailureCodes.CantAddLocalGroupToGlobalUser
                )
                results.unchanged_ids.append(self.user_name)
                results.message = msg

            elif not is_global and len(valid_local_groups) != len(group_ids):
                msg = (
                    'Can not add global groups to a local user %s: %s' %
                    (self.user_name, ', '.join(group_ids))
                )
                results.generic_status_code = GenericCodes.InvalidId
                results.vfense_status_code = (
                    UserFailureCodes.CantAddGlobalGroupToLocalUser
                )
                results.unchanged_ids.append(self.user_name)
                results.message = msg

            elif invalid_groups:
                msg = (
                    'Invalid group ids: {0}'.format(', '.join(invalid_groups))
                )
                results.generic_status_code = GenericCodes.InvalidId
                results.vfense_status_code = GroupFailureCodes.InvalidGroupId
                results.invalid_ids.append(group_ids)
                results.unchanged_ids.append(self.user_name)
                results.message = msg

        elif not user_exist:
            msg = 'User name is invalid: {0}'.format(self.user_name)
            results.generic_status_code = GenericCodes.InvalidId
            results.vfense_status_code = UserFailureCodes.Invaliduser_name
            results.invalid_ids.append(self.user_name)
            results.unchanged_ids.append(self.user_name)
            results.message = msg

        return results

    @time_it
    def remove(self, force=False):
        """Remove a user from vFense

        Kwargs:
            force (boolean): Remove the global_admin users
                default=False

        Basic Usage:
            >>> from vFense.user.manager import UserManager
            >>> user_name = 'shaolin'
            >>> manager = UserManager(user_name)
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
        user_name_not_to_delete = []
        user_name_to_delete = []
        results = ApiResults()
        results.fill_in_defaults()
        if (user_exist.user_name and self.user_name !=
                DefaultUsers.GLOBAL_ADMIN and not force
                or user_exist and force):

            self.remove_from_groups()
            self.remove_from_views()
            user_name_to_delete.append(self.user_name)

            object_status, _, _, _ = (
                delete_user(self.user_name)
            )

            if object_status == DbCodes.Deleted:
                msg = 'User removed %s' % (self.user_name)
                results.deleted_ids.append(user_name_to_delete)
                results.generic_status_code = GenericCodes.ObjectDeleted
                results.vfense_status_code = UserCodes.UserDeleted
                results.message = msg

        elif self.user_name == DefaultUsers.GLOBAL_ADMIN:
            msg = 'Can not delete the %s user' % (self.user_name)
            user_name_not_to_delete.append(self.user_name)
            results.generic_status_code = (
                GenericCodes.CouldNotBeDeleted
            )
            results.vfense_status_code = (
                UserFailureCodes.AdminUserCanNotBeDeleted
            )
            results.unchanged_idsi.append(user_name_not_to_delete)
            results.message = msg

        else:
            msg = 'User does not exist %s' % (self.user_name)
            user_name_not_to_delete.append(self.user_name)
            results.generic_status_code = GenericCodes.InvalidId
            results.vfense_status_code = (
                UserFailureCodes.UserNameDoesNotExist
            )
            results.message = msg
            results.invalid_ids.append(self.user_name)
            results.unchanged_ids.append(self.user_name)

        return results

    @time_it
    def remove_from_groups(self, group_ids=None, remove_admin=False):
        """Remove a group from a user
        Kwargs:
            group_ids (list): List of group_ids.
            remove_admin (bool): Whether to remove the global admin group
                from this user.
                default = False

        Basic Usage:
            >>> user_name = 'shaolin'
            >>> group_ids = ['0834e656-27a5-4b13-ba56-635797d0d1fc', '8757b79c-7321-4446-8882-65457f28c78b']
            >>> manager = UserManager(user_name)
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
        results = ApiResults()
        results.fill_in_defaults()
        if user_exist.user_name:
            group_ids_in_db = fetch_groupids_for_user(self.user_name)
            if self.user_name == DefaultUsers.GLOBAL_ADMIN:
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
                    delete_user_in_groups(self.user_name, group_ids)
                )
                if status_code == DbCodes.Replaced:
                    msg = (
                        'Removed group ids: %s from user %s' %
                        (', '.join(group_ids), self.user_name)
                    )
                    results.generic_status_code = GenericCodes.ObjectDeleted
                    results.vfense_status_code = (
                        GroupCodes.RemovedUsersFromGroup
                    )
                    results.message = msg
                    results.updated_ids.append(self.user_name)

                elif status_code == DbCodes.Unchanged:
                    msg = (
                        'Group ids: %s do not exist for user %s' %
                        (', '.join(group_ids), self.user_name)
                    )
                    results.generic_status_code = GenericCodes.ObjectUnchanged
                    results.vfense_status_code = GroupCodes.GroupsUnchanged
                    results.message = msg
                    results.unchanged_ids.append(self.user_name)

            elif admin_group_id_exists_in_group_ids and not remove_admin:
                msg = (
                    'Can not remove the special group %s from user %s' %
                        (', '.join(group_ids), self.user_name)
                )
                results.generic_status_code = GenericCodes.InvalidId
                results.vfense_status_code = (
                    GroupFailureCodes.CantRemoveAdminFromGroup
                )
                results.message =  msg
                results.unchanged_ids.append(self.user_name)

            else:
                msg = (
                    'groups %s do not exist for user %s' %
                    (' and '.join(group_ids), self.user_name)
                )
                results.generic_status_code = GenericCodes.InvalidId
                results.vfense_status_code = (
                    GroupFailureCodes.GroupDoesNotExistForUser
                )
                results.message =  msg
                results.invalid_ids.append(group_ids)
                results.unchanged_ids.append(self.user_name)

        else:
            msg = 'User does not exist %s' % (self.user_name)
            results.generic_status_code = GenericCodes.InvalidId
            results.vfense_status_code = GroupFailureCodes.InvalidGroupId
            results.message =  msg
            results.invalid_ids.append(self.user_name)
            results.unchanged_ids.append(self.user_name)

        return results

    @time_it
    def remove_from_views(self, views=None):
        """Remove a view from a user
        Kwargs:
            views (list): List of views,
                you want to remove from this user

        Basic Usage:
            >>> user_name = 'tester1'
            >>> views = ['Test View 1']
            >>> manager = UserManager(user_name)
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
        results = ApiResults()
        results.fill_in_defaults()

        if user_exist.user_name:
            views_in_db = user_exist.views
            views_exist = False
            if not views:
                views = views_in_db
                views_exist = True
            else:
                views_exist = set(views).issubset(views_in_db)

            if views_exist:
                status_code, _, _, _ = (
                    delete_user_in_views(self.user_name, views)
                )
                delete_views_in_user(self.user_name, views)
                if status_code == DbCodes.Replaced:
                    msg = (
                        'removed views from user %s: views = %s' %
                        (self.user_name, ', '.join(views))
                    )
                    results.message = msg
                    results.generic_status_code = GenericCodes.ObjectDeleted
                    results.vfense_status_code = (
                        ViewCodes.ViewsRemovedFromUser
                    )
                    results.updated_ids.append(self.user_name)
                else:
                    msg = (
                        'view names do not exist: %s for user %s' %
                        (', '.join(views), self.user_name)
                    )
                    results.generic_status_code = GenericCodes.DoesNotExist
                    results.vfense_status_code = (
                        ViewFailureCodes.UsersDoNotExistForView
                    )
                    results.invalid_ids.append(views)
                    results.unchanged_ids.append(self.user_name)
                    results.message = msg

            else:
                msg = (
                    'view names do not exist: %s for user %s' %
                    (', '.join(views), self.user_name)
                )
                results.generic_status_code = GenericCodes.DoesNotExist
                results.vfense_status_code = (
                    ViewFailureCodes.UsersDoNotExistForView
                )
                results.invalid_ids.append(views)
                results.unchanged_ids.append(self.user_name)
                results.message = msg

        else:
            msg = 'Invalid user_name %s' % (self.user_name)
            results.message = msg
            results.generic_status_code = GenericCodes.InvalidId
            results.vfense_status_code = (
                ViewFailureCodes.InvalidViewName
            )
            results.invalid_ids.append(self.user_name)
            results.unchanged_ids.append(self.user_name)

        return results

    @time_it
    def change_password(self, password, new_password):
        """Change password for a user.
        Args:
            password (str): Original password.
            new_password (str): New password.

        Basic Usage:
            >>> user_name = 'shaolin'
            >>> password = 'my original password'
            >>> new_password = 'my new password'
            >>> manager = UserManager(user_name)
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
        results = ApiResults()
        results.fill_in_defaults()
        if user_exist.user_name:
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

                user = User(password=encrypted_new_password)

                object_status, _, _, _ = (
                    update_user(self.user_name, user.to_dict_db_update())
                )

                if object_status == DbCodes.Replaced:
                    results.message = (
                        'Password changed for user %s - ' % (self.user_name)
                    )
                    results.generic_status_code = GenericCodes.ObjectUpdated
                    results.vfense_status_code = UserCodes.PasswordChanged
                    results.updated_ids.append(self.user_name)
                    results.data.append(user.to_dict_non_null())

            elif new_password_verified_against_orignal_password:
                results.message = (
                    'New password is the same as the original - user %s - ' %
                    (self.user_name)
                )
                results.generic_status_code = (
                    GenericFailureCodes.FailedToUpdateObject
                )
                results.vfense_status_code = (
                    UserFailureCodes.NewPasswordSameAsOld
                )
                results.unchanged_ids.append(self.user_name)
                results.data.append(user.to_dict_non_null())

            elif original_password_verified and not valid_passwd:
                results.message = (
                    'New password is to weak for user %s - ' %
                    (self.user_name)
                )
                results.generic_status_code = (
                    GenericFailureCodes.FailedToUpdateObject
                )
                results.vfense_status_code = (
                    UserFailureCodes.WeakPassword
                )
                results.unchanged_ids.append(self.user_name)
                results.data.append(user.to_dict_non_null())

            elif not original_password_verified:
                results.message = (
                    'Password not verified for user %s - ' %
                    (self.user_name)
                )
                results.generic_status_code = (
                    GenericFailureCodes.FailedToUpdateObject
                )
                results.vfense_status_code = (
                    UserFailureCodes.InvalidPassword
                )
                results.unchanged_ids.append(self.user_name)
                results.data.append(user.to_dict_non_null())

        else:
            results.message = 'User %s does not exist - ' % (self.user_name)
            results.generic_status_code = GenericCodes.InvalidId
            results.vfense_status_code = (
                UserFailureCodes.UserNameDoesNotExist
            )
            results.unchanged_ids.append(self.user_name)

        return results

    @time_it
    def reset_password(self, password):
        """Change password for a user.
        Args:
            password (str): Original password.

        Basic Usage:
            >>> user_name = 'global_admin'
            >>> password = 'My n3w p@ssword'
            >>> manager = UserManager(user_name)
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
        results = ApiResults()
        results.fill_in_defaults()
        if user_exist.user_name:
            valid_passwd, strength = check_password(password)
            encrypted_password = Crypto().hash_bcrypt(password)
            if valid_passwd:
                user = User(password=encrypted_password)

                object_status, _, _, _ = (
                    update_user(self.user_name, user.to_dict_db_update())
                )

                if object_status == DbCodes.Replaced:
                    results.message = (
                        'Password changed for user %s - ' % (self.user_name)
                    )
                    results.generic_status_code = GenericCodes.ObjectUpdated
                    results.vfense_status_code = UserCodes.PasswordChanged
                    results.data.append(user.to_dict_non_null())
                    results.updated_ids.append(self.user_name)

            else:
                results.message = (
                    'New password is to weak for user %s - ' %
                    (self.user_name)
                )
                results.generic_status_code = (
                    GenericFailureCodes.FailedToUpdateObject
                )
                results.vfense_status_code = UserFailureCodes.WeakPassword
                results.unchanged_ids.append(self.user_name)
                results.data.append(user.to_dict_non_null())

        else:
            results.message = 'User %s does not exist - ' % (self.user_name)
            results.generic_status_code = GenericCodes.InvalidId
            results.vfense_status_code = UserFailureCodes.UserNameDoesNotExist
            results.unchanged_ids.append(self.user_name)

        return results


    @time_it
    def change_view(self, user):
        """Change current or default view.
        Args:
            user (User): Original password.
        Basic Usage:
            >>> from vFense.user import User
            >>> from vFense.user.manager import UserManager
            >>> user_name = 'global_admin'
            >>> current_view = 'global'
            >>> user = (
                    User(
                        user_name, current_view=current_view,
                    )
                )
            >>> manager = UserManager(user_name)
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
        results = ApiResults()
        results.fill_in_defaults()
        view = None
        views_in_db = user_exist[UserKeys.Views]
        if user.current_view:
            view = user.current_view

        elif user.default_view:
            view = user.default_view

        if user_exist.user_name and view:

            if user_exist.is_global and view:
                results = self.__edit_user_properties(user)
            elif view in views_in_db:
                results = self.__edit_user_properties(user)
            else:
                msg = (
                    'View %s is not valid for user %s' %
                    (view, self.user_name)
                )
                results.message = status + msg
                results.generic_status_code = GenericCodes.InvalidId
                results.vfense_status_code = (
                    UserFailureCodes.FailedToUpdateUser
                )
        elif not user_exist and view:
            msg = (
                'User %s is not valid' % (self.user_name)
            )
            results.message = status + msg
            results.generic_status_code = GenericCodes.InvalidId
            results.vfense_status_code = UserFailureCodes.FailedToUpdateUser
        else:
            msg = (
                'current_view or default_view ' +
                'was not set in the User instance'
            )
            results.message = status + msg
            results.generic_status_code = GenericCodes.InvalidId
            results.vfense_status_code = UserFailureCodes.FailedToUpdateUser

        return results


    @time_it
    def edit_full_name(self, full_name):
        """Change current or default view.
        Args:
            full_name (str): The full name of the user.
        Basic Usage:
            >>> from vFense.user.manager import UserManager
            >>> full_name="Shaolin Administrator"
            >>> manager = UserManager('global_admin')
            >>> manager.edit_full_name(full_name)

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
        user = User(self.user_name, full_name=full_name)
        results = self.__edit_user_properties(user)

        return results


    @time_it
    def edit_email(self, email):
        """Edit the email address.
        Args:
            email (str): Edit the email address.

        Basic Usage:
            >>> from vFense.user.manager import UserManager
            >>> email="shaolin_admin@shaolin.com"
            >>> manager = UserManager('global_admin')
            >>> manager.edit_email(email)

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
        user = User(self.user_name, email=email)
        results = self.__edit_user_properties(user)

        return results

    @time_it
    def __edit_user_properties(self, user):
        """ Edit the properties of a view.
        Args:
            user (User): The User instance with all of its properties.

        Basic Usage:
            >>> from vFense.user import User
            >>> from vFense.user.manager import UserManager
            >>> user_name = 'global_admin'
            >>> user = (
                    User(user_name, full_name='Shaolin Administrator')
                )
            >>> manager = UserManager(user_name)
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
        results = ApiResults()
        results.fill_in_defaults()
        if user_exist.user_name:
            invalid_fields = user.get_invalid_fields()
            if not invalid_fields:
                object_status, count, error, _ = (
                    update_user(self.user_name, user.to_dict_db_update())
                )
                if object_status == DbCodes.Replaced:
                    results.message = (
                        'User %s was updated - ' % (self.user_name)
                    )
                    results.generic_status_code = GenericCodes.ObjectUpdated
                    results.vfense_status_code = UserCodes.UserUpdated
                    results.updated_ids.append(self.user_name)
                    results.data.append(user.to_dict_non_null())

                elif object_status == DbCodes.Unchanged:
                    results.message = (
                        'User %s was not updated - ' % (self.user_name)
                    )
                    results.generic_status_code = GenericCodes.ObjectUnchanged
                    results.vfense_status_code = UserCodes.UserUnchanged
                    results.unchanged_ids.append(self.user_name)
                    results.data.append(user.to_dict_non_null())

            else:
                results.generic_status_code = GenericCodes.InvalidId
                results.vfense_status_code = (
                    UserFailureCodes.FailedToUpdateUser
                )
                results.message = (
                    'User %s properties were invalid - ' % (self.user_name)
                )
                results.unchanged_ids.append(self.user_name)
                results.data.append(user.to_dict_non_null())
                results.errors.append(invalid_fields)

        else:
            results.generic_status_code = GenericCodes.InvalidId
            results.vfense_status_code = UserFailureCodes.UserNameDoesNotExist
            results.message = 'User %s does not exist - ' % (self.user_name)
            results.unchanged_ids.append(self.user_name)
        return results
