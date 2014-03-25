import logging                                                                                                     

from vFense.core.user import *
from vFense.core.user._constants import *
from vFense.core.group import *
from vFense.core.group._constants import *
from vFense.core.user._db import insert_user, fetch_user, fetch_users, \
    delete_user, update_user
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
    """Retrieve a user from the database
    Args:
        username (str): Name of the user.

    Kwargs:
        without_fields (list): List of fields you do not want to include.

    Basic Usage:
        >>> from vFense.user.users import get_user
        >>> username = 'admin'
        >>> get_user(username, without_fields=['password'])

    Return:
        Dictionary of user properties.
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
def get_users(customer_name=None, username=None, without_fields=None):
    """Retrieve all users that is in the database by customer_name or
        all of the customers or by regex.

    Kwargs:
        customer_name (str): Name of the customer, where the agent
            is located.
        username (str): Name of the user you are searching for.
            This is a regular expression match.
        without_fields (list): List of fields you do not want to include.

    Basic Usage::
        >>> from vFense.user.users import get_users
        >>> customer_name = 'default'
        >>> username = 'al'
        >>> without_fields = ['password']
        >>> get_users(customer_name, username, without_fields)

    Returns:
        List of users:
        [
            {
                "current_customer": "default", 
                "email": "test@test.org", 
                "full_name": "is doing it", 
                "default_customer": "default", 
                "user_name": "alien", 
                "id": "ba9682ef-7adf-4916-8002-9637485b30d8", 
                "customer_name": "default"
            }
        ]
    """
    data = fetch_users(customer_name, username, without_fields) 
    return(data)


@time_it
@results_message
def create_user(
    username, fullname, password, group_ids,
    customer_name, email, enabled=True, user_name=None,
    uri=None, method=None
    ):
    """Add a new user into vFense
    Args:
        username (str): The name of the user you are creating.
        fullname (str): The full name of the user you are creating.
        password (str): The unencrypted password of the user.
        group_ids (list): List of vFense group ids to add the user too.
        customer_name (str): The customer, this user will be part of.
        email (str): Email address of the user.
        enabled (boolean): True or False
            Default=True

    Kwargs:
        user_name (str): The name of the user who called this function.
        uri (str): The uri that was used to call this function.
        method (str): The HTTP methos that was used to call this function.

    Basic Usage:
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
                'enabled': True,
                'email': 'test@test.org'
            }
        }
    """

    user_exist = get_user(username)
    pass_strength = check_password(password)
    status = create_user.func_name + ' - '
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
                        UserKeys.Enabled: enabled,
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
                    object_status, username, status, user_data, error,
                    user_name, uri, method
                )

            elif not customer_is_valid and groups_are_valid[0]:
                error = 'customer name %s does not exist' % (customer_name)
                results = (
                    DbCodes.Errors, username, status + error, error, error,
                    user_name, uri, method
                )

            elif not groups_are_valid[0] and customer_is_valid:
                error = 'group ids %s does not exist' % (groups_are_valid[2])
                results = (
                    DbCodes.Errors, None, status + error, error, error,
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
                    DbCodes.Errors, username, status + error, error, error,
                    user_name, uri, method
                )

        elif user_exist:
            error = 'username %s already exists' % (username)
            results = (
                DbCodes.Errors, username, status + error, error, error,
                user_name, uri, method
            )

        elif not pass_strength[0]:
            error = (
                    'password does not meet the min requirements: strength=%s'
                    % (pass_strength[1])
            )

            results = (
                DbCodes.Errors, username, status + error, error, error,
                user_name, uri, method
            )

    except Exception as e:
        logger.exception(e)
        results = (
            DbCodes.Errors, username, status, e, e,
            user_name, uri, method
        )

    return(results)


@time_it
@results_message
def remove_user(username, user_name=None, uri=None, method=None):
    """Remove a user from vFense
    Args:
        username (str): The name of the user you are deleteing.

    Kwargs:
        user_name (str): The name of the user who called this function.
        uri (str): The uri that was used to call this function.
        method (str): The HTTP methos that was used to call this function.

    Return:
        Dictionary of the status of the operation.
    """

    user_exist = get_user(username)
    status = remove_user.func_name + ' - '
    try:
        if user_exist:
            remove_groups_from_user(username)
            remove_customers_from_user(username)

            object_status, object_count, error, generated_ids = (
                delete_user(username)
            )

            status = status + 'User removed %s' % (username)

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


@time_it
@results_message
def change_password(
    username, password, new_password,
    user_name=None, uri=None, method=None
    ):
    """Change password for a user.
    Args:
        username (str): The name of the user you are deleteing.
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
    user_exist = get_user(username, without_fields=None)
    status = change_password.func_name + ' - '
    try:
        if user_exist:
            pass_strength = check_password(new_password)
            original_encrypted_password = user_exist[UserKeys.Password].encode('utf-8')
            original_password_verified = (
                Crypto().verify_bcrypt_hash(password, original_encrypted_password)
            )
            encrypted_new_password = Crypto().hash_bcrypt(new_password)
            new_password_verified_against_orignal_password = (
                Crypto().verify_bcrypt_hash(new_password, original_encrypted_password)
            )
            if (original_password_verified and pass_strength[0] and
                    not new_password_verified_against_orignal_password):

                user_data = {UserKeys.Password: encrypted_new_password}

                object_status, object_count, error, generated_ids = (
                    update_user(username, user_data)
                )

                msg = 'Password changed for user %s - ' % (username)
                results = (
                    object_status, username, status + msg, [], error,
                    user_name, uri, method
                )

            elif new_password_verified_against_orignal_password:
                error = 'New password is the same as the original - user %s - ' % (username)

                results = (
                    DbCodes.Unchanged, username, status + error, [], error,
                    user_name, uri, method
                )

            elif original_password_verified and not pass_strength[0]:
                error = 'New password is to weak for user %s - ' % (username)

                results = (
                    DbCodes.Unchanged, username, status + error, [], error,
                    user_name, uri, method
                )

            elif not original_password_verified:
                error = 'Password not verified for user %s - ' % (username)

                results = (
                    DbCodes.Unchanged, username, status + error, [], error,
                    user_name, uri, method
                )

        else:
            error = 'User %s does not exist - ' % (username)

            results = (
                DbCodes.Skipped, username, status + error, [], error,
                user_name, uri, method
            )

    except Exception as e:
        logger.exception(e)

        results = (
            DbCodes.Errors, username, status, [], e,
            user_name, uri, method
        )

    return(results)


@time_it
@results_message
def update_user_properties(username, **kwargs):
    """ Edit the properties of a customer. 
    Args:
        username (str): Name of the user you are editing.

    Kwargs:
        full_name (str): The full name of the user
        email (str): The email address of the user
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
            'message': 'None-update_user_properties-adminwasupdated',
            'data': {
                'full_name': 'vFense Admin'
            }
        }
    """

    if not kwargs.get('user_name'):
        user_name = None
    else:
        user_name = kwargs.pop('user_name')

    if not kwargs.get('uri'):
        uri = None
    else:
        uri = kwargs.pop('uri')

    if not kwargs.get('method'):
        method = None
    else:
        method = kwargs.pop('method')

    if kwargs.get(UserKeys.Password):
        kwargs.pop(UserKeys.Password)

    user_exist = get_user(username, without_fields=None)
    status = update_user_properties.func_name + ' - '
    try:
        if user_exist:
            object_status, object_count, error, generated_ids = (
                update_user(username, kwargs)
            )

            results = (
                object_status, username, status, kwargs, error,
                user_name, uri, method
            )

        else:
            error = 'User %s does not exist - ' % (username)

            results = (
                DbCodes.Skipped, username, status + error, kwargs, error,
                user_name, uri, method
            )

    except Exception as e:
        logger.exception(e)
        error = 'Failed to update properties for user %s - ' % (username)

        results = (
            DbCodes.Errors, username, status, kwargs, e,
            user_name, uri, method
        )

    return(results)
