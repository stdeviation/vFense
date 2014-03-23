import logging

from vFense.core.user import *
from vFense.core.group import *
from vFense.core.decorators import return_status_tuple, time_it
from vFense.db.client import db_create_close, r

logging.config.fileConfig('/opt/TopPatch/conf/logging.config')
logger = logging.getLogger('rvapi')


@time_it
@db_create_close
def fetch_user(username, without_fields=None, conn=None):
    """
    Retrieve a user from the database
    :param username: Name of the user.
    :param without_fields: (Optional) List of fields you do not want to include.
    Basic Usage::
        >>> from vFense.user._db import fetch_user
        >>> username = 'admin'
        >>> fetch_user(username, without_fields=['password'])
        {
            u'current_customer': u'default',
            u'enabled': True,
            u'full_name': u'TopPatchAgentCommunicationAccount',
            u'default_customer': u'default',
            u'user_name': u'agent',
            u'email': u'admin@toppatch.com'
        }
    """
    data = {}
    try:
        if not without_fields:
            data = (
                r
                .table(UsersCollection)
                .get(username)
                .run(conn)
            )

        else:
            data = (
                r
                .table(UsersCollection)
                .get_all(username)
                .without(without_fields)
                .run(conn)
            )
            if data:
                data = data[0]

    except Exception as e:
        logger.exception(e)

    return(data)

@time_it
@db_create_close
def fetch_users(customer_name=None, username=None, conn=None):
    """
    Retrieve all customers that is in the database by customer_name or
        all of the customers or by regex.

    :param customer_name: (Optional) Name of the customer, where the agent
        is located.
    :param username: (Optional) Name of the user you are searching for.
        This is a regular expression match.

    Basic Usage::
        >>> from vFense.user._db import fetch_users
        >>> customer_name = 'default'
        >>> username = 'ag'
        >>> fetch_users(customer_name, username)
        [
            {
                u'customer_name': u'default',
                u'user_name': u'agent',
                u'id': u'ccac5136-3077-4d2c-a391-9bb15acd79fe'
            }
        ]
    """
    data = []
    try:
        if not customer_name and not username:
            data = list(
                r
                .table(CustomersPerUserCollection)
                .run(conn)
            )

        elif not customer_name and username:
            data = list(
                r
                .table(CustomersPerUserCollection)
                .filter(
                    lambda x:
                    x[CustomerPerUserKeys.UserName].match("(?i)" + username)
                )
                .run(conn)
            )

        elif customer_name and not username:
            data = list(
                r
                .table(CustomersPerUserCollection)
                .get_all(
                    customer_name, index=CustomerPerUserIndexes.CustomerName
                )
                .run(conn)
            )

        elif customer_name and username:
            data = list(
                r
                .table(CustomersPerUserCollection)
                .get_all(
                    customer_name, index=CustomerPerUserIndexes.CustomerName
                )
                .filter(
                    lambda x:
                    x[CustomerPerUserKeys.UserName].match("(?i)" + username)
                )
                .run(conn)
            )

    except Exception as e:
        logger.exception(e)

    return(data)


@time_it
@db_create_close
@return_status_tuple
def insert_user(user_data, conn=None):
    """
    This function should not be called directly.
    :param user_data: Can either be a list of dictionaries or a dictionary
        of the data you are inserting.

    Basic Usage::
        >>> from vFense.user._db import insert_user_data
        >>> user_data = {'customer_name': 'vFense', 'needs_reboot': 'no'}
        >>> insert_user_data(user_data)
        >>> (2001, 1, None, [])
    """
    data = {}
    try:
        data = (
            r
            .table(UsersCollection)
            .insert(user_data)
            .run(conn)
        )

    except Exception as e:
        logger.exception(status)

    return(data)


@time_it
@db_create_close
@return_status_tuple
def update_user(username, user_data, conn=None):
    """
    :param username: username of the user you are updating
    :param user_data: Dictionary of the data you are updating

    Basic Usage::
        >>> from vFense.user._db import update_user_data
        >>> username = 'admin'
        >>> data = {'production_level': 'Development', 'needs_reboot': 'no'}
        >>> update_user_data(username, data)
        >>> (2001, 1, None, [])
    """
    data = {}
    try:
        data = (
            r
            .table(UsersCollection)
            .get(username)
            .update(user_data)
            .run(conn)
        )

    except Exception as e:
        logger.exception(status)

    return(data)


@time_it
@db_create_close
@return_status_tuple
def delete_user(username, conn=None):
    """
    :param username: username of the user you are deleteing.
    Basic Usage::
        >>> from vFense.user._db import delete_user
        >>> username = 'admin'
        >>> delete_user(username)
        >>> (2001, 1, None, [])
    """
    data = {}
    try:
        data = (
            r
            .table(UsersCollection)
            .get(username)
            .delete()
            .run(conn)
        )

    except Exception as e:
        logger.exception(e)

    return(data)
