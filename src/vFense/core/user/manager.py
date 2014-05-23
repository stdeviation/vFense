import re
import logging
from vFense import VFENSE_LOGGING_CONFIG
from vFense.core._constants import *
from vFense.errorz._constants import *
from vFense.core.user import *
from vFense.core.user._constants import DefaultUsers
from vFense.core.group import *
from vFense.core.group._db import (
    fetch_groups_for_user, delete_groups_from_user,
    fetch_group_by_name, user_exist_in_group,
    fetch_groupids_for_user
)

from vFense.core.group._constants import DefaultGroups
from vFense.core.customer import *

from vFense.core.customer._db import (
    users_exists_in_customer, insert_user_per_customer,
    delete_users_in_customer
)

from vFense.core.customer._constants import DefaultCustomers

from vFense.core.user._db import insert_user, fetch_user, fetch_users, \
    delete_user, update_user, fetch_user_and_all_properties, \
    fetch_users_and_all_properties, delete_users, user_status_toggle

from vFense.core.group._db import user_exist_in_group, insert_group_per_user, \
    delete_users_in_group

from vFense.core.group.groups import validate_group_ids, \
    add_user_to_groups, remove_groups_from_user, get_group

from vFense.core.customer.customers import get_customer, \
    add_user_to_customers, remove_customers_from_user, \
    validate_customer_names

from vFense.utils.security import Crypto, check_password
from vFense.core.decorators import results_message, time_it
from vFense.errorz.status_codes import *

logging.config.fileConfig(VFENSE_LOGGING_CONFIG)
logger = logging.getLogger('rvapi')



class UserManager(object):
    def __init__(self, username):
        self.username = username
        self.properties = self._all_attributes_for_user()

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
                "current_customer": "default",
                "enabled": "yes",
                "full_name": "vFense Admin Account",
                "default_customer": "default",
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
                example attributes.. password, current_customer, email

        Basic Usage:
            >>> from vFense.user.manager import UserManager
            >>> name = 'admin'
            >>> user = UserManager(name)
            >>> property = 'current_customer'
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
                "current_customer": "default",
                "customers": [
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
                "default_customer": "default",
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
            if self.properties[UserKeys.Enabled] == CommonKeys.YES:
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
    def create(
        self, fullname, password, group_ids,
        customer_name, email, enabled=CommonKeys.YES
    ):
        """Add a new user into vFense
        Args:
            fullname (str): The full name of the user you are creating.
            password (str): The unencrypted password of the user.
            group_ids (list): List of vFense group ids to add the user too.
            customer_name (str): The customer, this user will be part of.
            email (str): Email address of the user.

        Kwargs:
            enabled (str): yes or no
                Default=yes

        Basic Usage:
            >>> from vFense.user.manager import UserManager
            >>> username = 'admin'
            >>> fullname = 'testing 4 life'
            >>> password = 'Testing123#'
            >>> group_ids = ['8757b79c-7321-4446-8882-65457f28c78b']
            >>> customer_name = 'default'
            >>> email = 'test@test.org'
            >>> enabled = 'yes'
            >>> user.create(
                fullname, password, group_ids,
                customer_name, email, enabled
            )

        Return:
            Dictionary of the status of the operation.
            {
                'uri': None,
                'rv_status_code': 1010,
                'http_method': None,
                'http_status': 200,
                'message': 'None - create user testing123 was created',
                'data': {
                    'current_customer': 'default',
                    'full_name': 'tester4life',
                    'default_customer': 'default',
                    'password': '$2a$12$HFAEabWwq8Hz0TIZ.jV59eHLoy0DdogdtR9TgvZnBCye894oljZOe',
                    'user_name': 'testing123',
                    'enabled': 'yes',
                    'email': 'test@test.org'
                }
            }
        """
        user_exist = self.properties
        pass_strength = check_password(password)
        status = self.create.func_name + ' - '
        generated_ids = []
        generic_status_code = 0
        vfense_status_code = 0
        user_data = (
            {
                UserKeys.CurrentCustomer: customer_name,
                UserKeys.DefaultCustomer: customer_name,
                UserKeys.FullName: fullname,
                UserKeys.UserName: self.username,
                UserKeys.Enabled: enabled,
                UserKeys.Email: email
            }
        )
        if enabled != CommonKeys.YES or enabled != CommonKeys.NO:
            enabled = CommonKeys.NO


        valid_user_name = (
            re.search('([A-Za-z0-9_-]{1,24})', self.username)
        )
        valid_user_length = (
            len(self.username) <= DefaultStringLength.USER_NAME
        )

        try:
            if (not user_exist and pass_strength[0] and
                valid_user_length and valid_user_name):

                encrypted_password = Crypto().hash_bcrypt(password)
                user_data[UserKeys.Password] = encrypted_password
                customer_is_valid = get_customer(customer_name)
                validated_groups, _, invalid_groups = validate_group_ids(
                    group_ids, customer_name
                )

                if customer_is_valid and validated_groups:
                    object_status, _, _, generated_ids = (
                        insert_user(user_data)
                    )
                    generated_ids.append(self.username)

                    self.add_to_customers([customer_name])
                    self.add_to_groups(group_ids)

                    if object_status == DbCodes.Inserted:
                        msg = 'user name %s created' % (self.username)
                        generic_status_code = GenericCodes.ObjectCreated
                        vfense_status_code = UserCodes.UserCreated
                        user_data.pop(UserKeys.Password)

                elif not customer_is_valid and validated_groups:
                    msg = 'customer name %s does not exist' % (customer_name)
                    object_status = DbCodes.Skipped
                    generic_status_code = GenericCodes.InvalidId
                    vfense_status_code = CustomerFailureCodes.CustomerDoesNotExist

                elif not validated_groups and customer_is_valid:
                    msg = 'group ids %s does not exist' % (invalid_groups)
                    object_status = DbCodes.Skipped
                    generic_status_code = GenericCodes.InvalidId
                    vfense_status_code = GroupFailureCodes.InvalidGroupId

                else:
                    group_error = (
                        'group ids %s does not exist' % (invalid_groups)
                    )
                    customer_error = (
                        'customer name %s does not exist' % (customer_name)
                    )
                    msg = group_error + ' and ' + customer_error
                    object_status = DbCodes.Errors
                    generic_status_code = GenericFailureCodes.FailedToCreateObject
                    vfense_status_code = UserFailureCodes.FailedToCreateUser

            elif user_exist:
                msg = 'username %s already exists' % (self.username)
                object_status = GenericCodes.ObjectExists
                generic_status_code = GenericCodes.ObjectExists
                vfense_status_code = UserFailureCodes.UserNameExists

            elif not pass_strength[0]:
                msg = (
                    'password does not meet the min requirements: strength=%s'
                    % (pass_strength[1])
                )
                object_status = GenericFailureCodes.FailedToCreateObject
                generic_status_code = GenericFailureCodes.FailedToCreateObject
                vfense_status_code = UserFailureCodes.WeakPassword

            elif not valid_user_name or not valid_user_length:
                status_code = DbCodes.Errors
                msg = (
                    'user name is not within the 24 character range '+
                    'or contains unsupported characters :%s' %
                    (self.username)
                )
                generic_status_code = GenericCodes.InvalidId
                vfense_status_code = UserFailureCodes.InvalidUserName

            results = {
                ApiResultKeys.DB_STATUS_CODE: object_status,
                ApiResultKeys.GENERIC_STATUS_CODE: generic_status_code,
                ApiResultKeys.VFENSE_STATUS_CODE: vfense_status_code,
                ApiResultKeys.MESSAGE: status + msg,
                ApiResultKeys.GENERATED_IDS: generated_ids,
                ApiResultKeys.DATA: [user_data],
            }

        except Exception as e:
            logger.exception(e)
            msg = 'Failed to create user %s: %s' % (self.username, str(e))
            status_code = DbCodes.Errors
            generic_status_code = GenericFailureCodes.FailedToCreateObject
            vfense_status_code = UserFailureCodes.FailedToCreateUser

            results = {
                ApiResultKeys.DB_STATUS_CODE: status_code,
                ApiResultKeys.GENERIC_STATUS_CODE: generic_status_code,
                ApiResultKeys.VFENSE_STATUS_CODE: vfense_status_code,
                ApiResultKeys.MESSAGE: status + msg,
                ApiResultKeys.GENERATED_IDS: [],
                ApiResultKeys.DATA: [user_data],
            }

        return results


    @time_it
    @results_message
    def remove(self):
        """Remove a user from vFense
        Return:
            Dictionary of the status of the operation.
        """
        user_exist = self.properties
        status = self.remove.func_name + ' - '
        username_not_to_delete = []
        username_to_delete = []
        results = {}
        try:
            if user_exist and self.username != DefaultUsers.ADMIN:
                self.remove_from_groups()
                self.remove_from_customers()
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


        except Exception as e:
            logger.exception(e)
            msg = 'Failed to remove user %s: %s' % (self.username, str(e))
            status_code = DbCodes.Errors
            generic_status_code = GenericFailureCodes.FailedToDeleteObject
            vfense_status_code = UserFailureCodes.FailedToRemoveUser

            results = {
                ApiResultKeys.DB_STATUS_CODE: status_code,
                ApiResultKeys.GENERIC_STATUS_CODE: generic_status_code,
                ApiResultKeys.VFENSE_STATUS_CODE: vfense_status_code,
                ApiResultKeys.MESSAGE: status + msg,
                ApiResultKeys.UNCHANGED_IDS: username_not_to_delete,
                ApiResultKeys.DELETED_IDS: username_to_delete,
                ApiResultKeys.DATA: [],
            }

        return results

    @time_it
    def remove_from_groups(self, group_ids=None):
        """Remove a group from a user
        Kwargs:
            group_ids(list): List of group_ids.

        Basic Usage::
            >>> from vFense.core.group.groups remove_groups_from_user
            >>> username = 'alien'
            >>> group_ids = ['0834e656-27a5-4b13-ba56-635797d0d1fc', '8757b79c-7321-4446-8882-65457f28c78b']
            >>> remove_groups_from_user(username, group_ids)

        Returns:
            Returns the results in a dictionary
            {
                'rv_status_code': 1004,
                'message': 'None - remove_groups_from_user - group ids: 0834e656-27a5-4b13-ba56-635797d0d1fc, 8757b79c-7321-4446-8882-65457f28c78b does not exist',
                'http_method': None,
                'uri': None,
                'http_status': 409
            }
        """
        status = self.remove_from_groups.func_name + ' - '
        user_does_not_exist_in_group = False
        admin_group_id = None
        admin_group_id_exists_in_group_ids = False
        if self.username == DefaultUsers.ADMIN:
            admin_group_id = fetch_group_by_name(
                DefaultGroups.ADMIN, DefaultCustomers.DEFAULT,
                GroupKeys.GroupId)[GroupKeys.GroupId]

        try:
            if not group_ids:
                group_ids = fetch_groupids_for_user(self.username)

            if group_ids:
                if not admin_group_id in group_ids:
                    msg = 'group ids: ' + 'and '.join(group_ids)
                    for gid in group_ids:
                        user_in_group = user_exist_in_group(self.username, gid)
                        if not user_in_group:
                            user_does_not_exist_in_group = True
                else:
                    admin_group_id_exists_in_group_ids = True
                    msg = (
                        'Cannot remove the %s group from the %s user' %
                        (DefaultGroups.ADMIN, DefaultUsers.ADMIN)
                    )
            else:
                user_does_not_exist_in_group = True

            if (not user_does_not_exist_in_group and
                not admin_group_id_exists_in_group_ids):

                status_code, count, errors, generated_ids = (
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

        except Exception as e:
            logger.exception(e)
            status_code = DbCodes.Errors
            generic_status_code = GenericFailureCodes.FailedToDeleteObject
            vfense_status_code = GroupFailureCodes.FailedToRemoveGroupFromUser

            results = {
                ApiResultKeys.DB_STATUS_CODE: status_code,
                ApiResultKeys.GENERIC_STATUS_CODE: generic_status_code,
                ApiResultKeys.VFENSE_STATUS_CODE: vfense_status_code,
                ApiResultKeys.MESSAGE: status + msg,
                ApiResultKeys.DATA: [],
            }

        return results
