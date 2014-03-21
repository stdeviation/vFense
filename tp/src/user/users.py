import logging                                                                                                     
from datetime import datetime                                                                                      
from time import mktime

from vFense.user import *
from vFense.group import *
from vFense.utils.security import Crypto
from vFense.user._db import insert_user, fetch_user, fetch_users, \
    insert_user_per_customer, insert_user_per_group
from vFense.group.groups import validate_group_ids, get_group
from vFense.customer.customers import get_customer, validate_customer_names
from vFense.db.client import r, return_status_tuple, results_message
from vFense.errorz.error_messages import GenericResults
from vFense.errorz.status_codes import DbCodes

logging.config.fileConfig('/opt/TopPatch/conf/logging.config')
logger = logging.getLogger('rvapi')

def get_user(username, without_fields=['password']):
    """
    Retrieve a user from the database
    :param username: Name of the user.
    :param without_fields: (Optional) List of fields you do not want to include.
    Basic Usage::
        >>> from vFense.user.users import get_user
        >>> username = 'admin'
        >>> get_user(username, without_fields=['password'])
        {
            u'current_customer': u'default',
            u'enabled': True,
            u'full_name': u'TopPatchAgentCommunicationAccount',
            u'default_customer': u'default',
            u'user_name': u'agent',
            u'email': u'admin@toppatch.com'
        }
    """
    data = fetch_user(username, without_fields)
    return(data)

def get_users(customer_name=None, username=None):
    """
    Retrieve all customers that is in the database by customer_name or
        all of the customers or by regex.

    :param customer_name: (Optional) Name of the customer, where the agent
        is located.
    :param username: (Optional) Name of the user you are searching for.
        This is a regular expression match.

    Basic Usage::
        >>> from vFense.user.users import get_users
        >>> customer_name = 'default'
        >>> username = 'ag'
        >>> get_users(customer_name, username)
        [
            {
                u'customer_name': u'default',
                u'user_name': u'agent',
                u'id': u'ccac5136-3077-4d2c-a391-9bb15acd79fe'
            }
        ]
    """
    data = fetch_users(customer_name, username) 
    return(data)


@results_message
def add_user_to_customers(
    username, customer_names, 
    user_name=None, uri=None, method=None
    ):
    """
    Add a user into a vFense group
    :param username:  Name of the user already in vFense.
    :param customer_names:List of  customer this user will be added too.
    """
    customers_are_valid = validate_customer_names(customer_names)
    user_exist = get_user(username)
    results = None
    if customers_are_valid[0] and user_exist:
        data_list = []
        for customer_name in customer_names:
            data_to_add = (
                {
                    UserPerCustomerKeys.CustomerName: customer_name,
                    UserPerCustomerKeys.UserName: username,
                }
            )
            data_list.append(data_to_add)

        object_status, object_count, error, generated_ids = (
            insert_user_per_customer(data_to_add)
        )

        results = (
            object_status, generated_ids, 'users add to customers',
            data_to_add, error, user_name, uri, method
        )

    elif not customers_are_valid[0]:
        status_code = DbCodes.Errors
        status_error = 'Customer names are invalid: %s' % (customers_are_valid[2])
        results = (
            status_code, None, 'users add to customers',
            customer_names, status_error, user_name, uri, method
        )

    elif not user_exist:
        status_code = DbCodes.Errors
        status_error = 'User name is invalid: %s' % (username)
        results = (
            status_code, None, 'users add to customers',
            customer_names, status_error, user_name, uri, method
        )

    return(results)


@results_message
def add_user_to_groups(
    username, customer_name, group_ids,
    user_name=None, uri=None, method=None
    ):
    """
    Add a user into a vFense group
    :param username:  Name of the user already in vFense.
    :param customer_name: The customer this user is part of.
    :param group_ids: List of group ids.
    """
    groups_are_valid = validate_group_ids(group_ids)
    user_exist = get_user(username)
    customer_exist = get_customer(customer_name)
    results = None
    if groups_are_valid[0] and user_exist and customer_exist:
        data_list = []
        for group_id in group_ids:
            group_exist = get_group(group_id)
            data_to_add = (
                {
                    GroupsPerUserKeys.CustomerName: customer_name,
                    GroupsPerUserKeys.UserName: username,
                    GroupsPerUserKeys.GroupName: group_exist[GroupKeys.GroupName],
                    GroupsPerUserKeys.Id: group_id
                }
            )
            data_list.append(data_to_add)

        object_status, object_count, error, generated_ids = (
            insert_user_per_group(data_to_add)
        )

        results = (
            object_status, generated_ids, 'groups per user', data_to_add,
            error, user_name, uri, method
        )

    elif not groups_are_valid[0]:
        status_code = DbCodes.Errors
        status_error = 'Group Ids are invalid: %s' % (groups_are_valid[2])
        results = (
            status_code, None, 'groups per user', [],
            status_error, user_name, uri, method
        )

    elif not user_exist:
        status_code = DbCodes.Errors
        status_error = 'User name is invalid: %s' % (username)
        results = (
            status_code, None, 'groups per user', [],
            status_error, user_name, uri, method
        )

    elif not customer_exist:
        status_code = DbCodes.Errors
        status_error = 'Customer name is invalid: %s' % (customer_name)
        results = (
            status_code, None, 'groups per user', [],
            status_error, user_name, uri, method
        )

    return(results)

@results_message
def create_user(
    username, fullname, password, group_ids,
    customer_name, email, enabled=False, user_name=None,
    uri=None, method=None
    ):
    """
    Add a new user into vFense
    :param username: (Unique) The name of the user you are creating.
    :param fullname: The full name of the user you are creating.
    :param enabled: Create the user as enabled or disabled.
    :param password: The unencrypted password of the user.
    :param group_ids: List of vFense group ids to add the user too.
    :param customer_name: The customer, this user will be part of.
    :param email: Email address of the user.
    :param enabled: False by default.
    """

    user_exist = get_user(username)
    try:
        if not user_exist:
            encrypted_password = Crypto().hash_bcrypt(password)
            customer_is_valid = get_customer(customer_name)
            groups_are_valid = validate_group_ids(group_ids)
            if customer_is_valid and groups_are_valid[0]:
                user_data = (
                    {
                        UserKeys.CurrentCustomer: customer_name,
                        UserKeys.DefaultCustomer: customer_name,
                        UserKeys.Enabled: enabled,
                        UserKeys.FullName: fullname,
                        UserKeys.Password: encrypted_password,
                        UserKeys.UserName: username,
                        UserKeys.UserId: username,
                        UserKeys.Email: email
                    }
                )
                object_status, object_count, error, generated_ids = (
                    insert_user(user_data)
                )
                add_user_to_customer_results = (
                    add_user_to_customers(
                        username, [customer_name],
                        user_name, uri, method
                    )
                )
                group_add_results = (
                    add_user_to_groups(
                        username, customer_name, group_ids,
                        user_name, uri, method
                    )
                )
                results = (
                    object_status, username, 'create user', user_data, error,
                    user_name, uri, method
                )

            elif not customer_is_valid and groups_are_valid[0]:
                error = 'customer name %s does not exist' % (customer_name)
                results = (
                    DbCodes.Errors, None, 'create user', user_data, error,
                    user_name, uri, method
                )

            elif not groups_are_valid[0] and customer_is_valid:
                error = 'group ids %s does not exist' % (groups_are_valid[2])
                results = (
                    DbCodes.Errors, None, 'create user', user_data, error,
                    user_name, uri, method
                )

            else:
                group_error = 'group ids %s does not exist' % (groups_are_valid[2])
                customer_error = 'customer name %s does not exist' % (customer_name)
                error = group_error + ' and ' + customer_error
                results = (
                    DbCodes.Errors, None, 'create user', user_data, error,
                    user_name, uri, method
                )

        else:
            error = 'username %s already exists' % (username)
            results = (
                DbCodes.Errors, None, 'create_user', [], error,
                user_name, uri, method
            )
    except Exception as e:
        logger.exception(e)
        results = (
            DbCodes.Errors, None, 'create user', [], e,
            user_name, uri, method
        )

    return(results)
