import logging
from vFense import VFENSE_LOGGING_CONFIG
from vFense.errorz._constants import ApiResultKeys
from vFense.core.user import User
from vFense.core.user._db_model import UserKeys
from vFense.core.user._constants import DefaultUsers
from vFense.core.group import GroupKeys, GroupsPerUserKeys
from vFense.core.group._db import (
    delete_groups_from_user,
    fetch_group_by_name, user_exist_in_group,
    fetch_groupids_for_user, fetch_group
)

from vFense.core.group._constants import DefaultGroups

from vFense.core.customer._db import (
    users_exists_in_customer, insert_user_per_customer,
    delete_user_in_customers, fetch_customer_names_for_user,
    fetch_all_customer_names
)

from vFense.core.customer import CustomerPerUserKeys
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
from vFense.core.decorators import time_it
from vFense.errorz.status_codes import (
    UserFailureCodes, UserCodes, GenericFailureCodes, GenericCodes,
    DbCodes, CustomerFailureCodes, GroupFailureCodes, GroupCodes,
    CustomerCodes
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
            >>> customer_name = 'default'
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
            >>> manager.create(user, customer_name, group_ids)

        Return:
            Dictionary of the status of the operation.
            {
                'rv_status_code': 1010,
                'errors': [],
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
                current_customer_is_valid = get_customer(user.current_customer)
                default_customer_is_valid = get_customer(user.default_customer)
                validated_groups, _, invalid_groups = (
                    validate_group_ids(
                        group_ids, user.current_customer, user.is_global
                    )
                )

                if (
                        current_customer_is_valid and
                        default_customer_is_valid and
                        validated_groups
                    ):
                    object_status, _, _, generated_ids = (
                        insert_user(user_data)
                    )

                    if object_status == DbCodes.Inserted:
                        msg = 'user name %s created' % (self.username)
                        self.properties = self._user_attributes()
                        generated_ids.append(self.username)
                        customers = (
                            list(
                                set(
                                    [
                                        user.current_customer,
                                        user.default_customer
                                    ]
                                )
                            )
                        )
                        if user.is_global:
                            customers = fetch_all_customer_names()

                        self.add_to_customers(customers)
                        self.add_to_groups(group_ids)
                        generic_status_code = GenericCodes.ObjectCreated
                        vfense_status_code = UserCodes.UserCreated
                        user_data.pop(UserKeys.Password)

                elif (
                        not current_customer_is_valid or
                        not default_customer_is_valid and
                        validated_groups
                    ):
                    msg = (
                        'customer name %s does not exist' %
                        (user.current_customer)
                    )
                    generic_status_code = GenericCodes.InvalidId
                    vfense_status_code = (
                        CustomerFailureCodes.CustomerDoesNotExist
                    )

                elif (
                        current_customer_is_valid or
                        default_customer_is_valid and
                        not validated_groups
                    ):
                    msg = 'group ids %s does not exist' % (invalid_groups)
                    generic_status_code = GenericCodes.InvalidId
                    vfense_status_code = GroupFailureCodes.InvalidGroupId

                else:
                    group_error = (
                        'group ids %s does not exist' % (invalid_groups)
                    )
                    customer_error = (
                        'customer name %s does not exist' %
                        (user.current_customer)
                    )
                    msg = group_error + ' and ' + customer_error
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
    def add_to_customers(self, customer_names):
        """Add a multiple customers to a user
        Args:
            customer_names (list): List of customer names,
                this user will be added to.

        Basic Usage:
            >>> from vFense.core.customer.customer import add_user_to_customers
            >>> username = 'admin'
            >>> customer_names = ['default', 'TopPatch', 'vFense']
            >>> add_user_to_customers(username, customer_names)

        Returns:
            Dictionary of the status of the operation.
            {
                'rv_status_code': 1017,
                'message': "None - add_user_to_customers - customer names existed 'default', 'TopPatch', 'vFense' unchanged",
                'data': []
            }
        """
        if isinstance(customer_names, str):
            customer_names = customer_names.split(',')

        customers_are_valid = validate_customer_names(customer_names)
        results = None
        user_exist = self.properties
        data_list = []
        status = self.add_to_customers.func_name + ' - '
        msg = ''
        status_code = 0
        generic_status_code = 0
        vfense_status_code = 0
        generated_ids = []
        if customers_are_valid[0]:
            data_list = []
            for customer_name in customer_names:
                if not users_exists_in_customer(self.username, customer_name):
                    data_to_add = (
                        {
                            CustomerPerUserKeys.CustomerName: customer_name,
                            CustomerPerUserKeys.UserName: self.username,
                        }
                    )
                    data_list.append(data_to_add)

            if user_exist and data_list:
                status_code, _, _, generated_ids = (
                    insert_user_per_customer(data_list)
                )
                if status_code == DbCodes.Inserted:
                    msg = (
                        'user %s added to %s' % (
                            self.username, ' and '.join(customer_names)
                        )
                    )
                    generic_status_code = GenericCodes.ObjectCreated
                    vfense_status_code = CustomerCodes.CustomersAddedToUser

            elif user_exist and not data_list:
                msg = 'customer names existed for user %s' % (self.username)
                generic_status_code = GenericCodes.ObjectExists
                vfense_status_code = CustomerFailureCodes.UsersExistForCustomer

            elif not user_exist:
                msg = 'User name is invalid: %s' % (self.username)
                generic_status_code = GenericCodes.InvalidId
                vfense_status_code = UserFailureCodes.UserNameDoesNotExist

        elif not customers_are_valid[0]:
            msg = (
                'Customer names are invalid: %s' % (
                    ' and '.join(customers_are_valid[2])
                )
            )
            generic_status_code = GenericCodes.InvalidId
            vfense_status_code = CustomerFailureCodes.InvalidCustomerName

        results = {
            ApiResultKeys.GENERIC_STATUS_CODE: generic_status_code,
            ApiResultKeys.VFENSE_STATUS_CODE: vfense_status_code,
            ApiResultKeys.GENERATED_IDS: generated_ids,
            ApiResultKeys.MESSAGE: status + msg,
            ApiResultKeys.ERRORS: [],
            ApiResultKeys.DATA: [],
        }

        return results

    @time_it
    def add_to_groups(self, group_ids):
        """Add a user into a vFense group
        Args:
            username (str):  Name of the user already in vFense.
            customer_name (str): The customer this user is part of.
            group_ids (list): List of group ids.

        Basic Usage:
            >>> from vFense.group.groups import add_user_to_groups
            >>> username = 'alien'
            >>> customer_name = 'default'
            >>> group_ids = ['0834e656-27a5-4b13-ba56-635797d0d1fc']
            >>> add_user_to_groups(username, customer_name, group_ids)

        Returns:
            Returns the results in a dictionary
        {
            'rv_status_code': 1010,
            'message': "None - groups per user [u'ee54820c-cb4e-46a1-9d11-73afe8c4c4e3'] was created",
            'data': {
                'group_name': u'FooLah',
                'user_name': 'alien',
                'group_id': '0834e656-27a5-4b13-ba56-635797d0d1fc',
                'customer_name': 'default'
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
                            GroupsPerUserKeys.CustomerName: (
                                group.get(GroupKeys.CustomerName)
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
            }
        """
        status = self.remove_from_groups.func_name + ' - '
        exist_in_groupids = False
        admin_group_id = None
        admin_group_id_exists_in_group_ids = False
        group_ids_in_db = fetch_groupids_for_user(self.username)
        if self.username == DefaultUsers.ADMIN:
            admin_group_id = fetch_group_by_name(
                DefaultGroups.ADMIN, DefaultCustomers.DEFAULT,
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
    def remove_from_customers(self, customer_names=None):
        """Remove a customer from a user
        Args:
            username (str): Username of the user, you are
                removing the customer from.

        Kwargs:
            customer_names (list): List of customer_names,
                you want to remove from this user

        Basic Usage:
            >>> from vFense.customer.customers remove_customers_from_user
            >>> username = 'agent_api'
            >>> remove_customers_from_user(username)

        Returns:
            Dictionary of the status of the operation.
            >>>
            {
                'rv_status_code': 1004,
                'message': 'None - remove_customers_from_user - removed customers from user alien: TopPatch and vFense does not exist',
            }
        """
        status = self.remove_from_customers.func_name + ' - '
        customer_names_in_db = fetch_customer_names_for_user(self.username)
        exist = False
        if not customer_names:
            customer_names = customer_names_in_db
            exist = True
        else:
            exist = set(customer_names).issubset(customer_names_in_db)

        if exist:
            status_code, count, errors, generated_ids = (
                delete_user_in_customers(self.username, customer_names)
            )
            if status_code == DbCodes.Deleted:
                msg = 'removed customers from user %s' % (self.username)
                generic_status_code = GenericCodes.ObjectDeleted
                vfense_status_code = CustomerCodes.CustomersRemovedFromUser

            elif status_code == DbCodes.Skipped:
                msg = 'invalid customer name or invalid username'
                generic_status_code = GenericCodes.InvalidId
                vfense_status_code = CustomerFailureCodes.InvalidCustomerName

            elif status_code == DbCodes.DoesNotExist:
                msg = 'customer name or username does not exist'
                generic_status_code = GenericCodes.DoesNotExist
                vfense_status_code = (
                    CustomerFailureCodes.UsersDoNotExistForCustomer
                )

        else:
            msg = (
                'customer names do not exist: %s' %
                (', '.join(customer_names))
            )
            generic_status_code = GenericCodes.DoesNotExist
            vfense_status_code = CustomerFailureCodes.UsersDoNotExistForCustomer

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

        Kwargs:
            user_name (str): The name of the user who called this function.
            uri (str): The uri that was used to call this function.
            method (str): The HTTP methos that was used to call this function.

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
        user_exist = self.properaties
        status = self.change_password.func_name + ' - '
        generic_status_code = 0
        vfense_status_code = 0
        results = {}
        if user_exist:
            valid_passwd, strength = check_password(new_password)
            original_encrypted_password = (
                user_exist[UserKeys.Password].encode('utf-8')
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
    def __edit_user_properties(self, user):
        """ Edit the properties of a customer.
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
