import logging                                                                                                     

from vFense.core.user import *
from vFense.core.group import *
from vFense.core.user._db import insert_user, fetch_user, fetch_users, \
    delete_user
from vFense.core.group.groups import validate_group_ids, \
    add_user_to_groups, remove_groups_from_user
from vFense.core.customer.customers import get_customer, \
    add_user_to_customers, remove_customers_from_user
from vFense.utils.security import Crypto, check_password
from vFense.core.decorators import results_message, time_it
from vFense.errorz.status_codes import DbCodes

logging.config.fileConfig('/opt/TopPatch/conf/logging.config')
logger = logging.getLogger('rvapi')


@time_it
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


@time_it
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
        >>> username = 'al'
        >>> get_users(customer_name, username)
        [
            {
                u'user_name': u'alien',
                u'id': u'b157fdb8-a268-4b98-894e-1ef456e7ac88',
                u'customer_name': u'default'
            },
            {
                u'user_name': u'alllllen',
                u'id': u'bfe53dae-fb46-4a17-8453-312675b21aa2',
                u'customer_name': u'default'
            }
        ]
    """
    data = fetch_users(customer_name, username) 
    return(data)


@time_it
@results_message
def create_user(
    username, fullname, password, group_ids,
    customer_name, email, user_name=None,
    uri=None, method=None
    ):
    """
    Add a new user into vFense
    :param username: (Unique) The name of the user you are creating.
    :param fullname: The full name of the user you are creating.
    :param password: The unencrypted password of the user.
    :param group_ids: List of vFense group ids to add the user too.
    :param customer_name: The customer, this user will be part of.
    :param email: Email address of the user.
    Basic Usage::
        >>> from vFense.user.users import create_user
        >>> username = 'testing123'
        >>> fullname = 'testing 4 life'
        >>> password = 'Testing123#'
        >>> group_ids = ['8757b79c-7321-4446-8882-65457f28c78b']
        >>> customer_name = 'default'
        >>> email = 'test@test.org'
        >>> create_user(
                username, fullname, password,
                group_ids, customer_name, email
            )
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
            'email': 'test@test.org'
        }
    }
    """

    user_exist = get_user(username)
    pass_strength = check_password(password)
    try:
        if not user_exist and pass_strength[0]:
            encrypted_password = Crypto().hash_bcrypt(password)
            customer_is_valid = get_customer(customer_name)
            groups_are_valid = validate_group_ids(group_ids, customer_name)
            if customer_is_valid and groups_are_valid[0]:
                user_data = (
                    {
                        UserKeys.CurrentCustomer: customer_name,
                        UserKeys.DefaultCustomer: customer_name,
                        UserKeys.FullName: fullname,
                        UserKeys.Password: encrypted_password,
                        UserKeys.UserName: username,
                        #UserKeys.UserId: username,
                        UserKeys.Email: email
                    }
                )
                object_status, object_count, error, generated_ids = (
                    insert_user(user_data)
                )

                add_user_to_customers(
                    username, [customer_name],
                    user_name, uri, method
                )

                add_user_to_groups(
                    username, customer_name, group_ids,
                    user_name, uri, method
                )
                results = (
                    object_status, username, 'create user', user_data, error,
                    user_name, uri, method
                )

            elif not customer_is_valid and groups_are_valid[0]:
                error = 'customer name %s does not exist' % (customer_name)
                results = (
                    DbCodes.Errors, username, 'create user failed', error, error,
                    user_name, uri, method
                )

            elif not groups_are_valid[0] and customer_is_valid:
                error = 'group ids %s does not exist' % (groups_are_valid[2])
                results = (
                    DbCodes.Errors, None, 'create user failed', error, error,
                    user_name, uri, method
                )

            else:
                group_error = (
                    'group ids %s does not exist' % (groups_are_valid[2])
                )
                customer_error = (
                    'customer name %s does not exist' % (customer_name)
                )
                error = group_error + ' and ' + customer_error
                results = (
                    DbCodes.Errors, username, 'create user failed', error, error,
                    user_name, uri, method
                )

        elif user_exist:
            error = 'username %s already exists' % (username)
            results = (
                DbCodes.Errors, username, 'create_user failed', error, error,
                user_name, uri, method
            )

        elif not pass_strength[0]:
            error = (
                    'password does not meet the min requirements: strength=%s'
                    % (pass_strength[1])
            )

            results = (
                DbCodes.Errors, username, 'create_user failed', error, error,
                user_name, uri, method
            )

    except Exception as e:
        logger.exception(e)
        results = (
            DbCodes.Errors, username, 'create user failed', e, e,
            user_name, uri, method
        )

    return(results)


@time_it
@results_message
def remove_user(username, user_name=None, uri=None, method=None):
    """
    Add a new user into vFense
    :param username: The name of the user you are deleteing.
    """

    user_exist = get_user(username)
    try:
        if user_exist:
            remove_groups_from_user(username)
            remove_customers_from_user(username)

            object_status, object_count, error, generated_ids = (
                delete_user(username)
            )

            status = 'User removed %s' % (username)

            results = (
                object_status, username, status, [], error,
                user_name, uri, method
            )

        else:
            status = 'User does not exist %s' % (username)

            results = (
                DbCodes.Skipped, username, status, [], status,
                user_name, uri, method
            )

    except Exception as e:
        logger.exception(e)
        status = 'Failed to remove user %s' % (username)

        results = (
            DbCodes.Errors, username, status, [], e,
            user_name, uri, method
        )

    return(results)
