import logging

from vFense.core.user import *
from vFense.core.user._constants import *
from vFense.core.group import *
from vFense.core.group._constants import *
from vFense.core.customer import *
from vFense.core.customer._constants import *
from vFense.core.decorators import return_status_tuple, time_it
from vFense.db.client import db_create_close, r

logging.config.fileConfig('/opt/TopPatch/conf/logging.config')
logger = logging.getLogger('rvapi')


@time_it
@db_create_close
def fetch_user(username, without_fields=None, conn=None):
    """Retrieve a user from the database
    Args:
        username (str): Name of the user.

    Kwargs:
        without_fields (list): List of fields you do not want to include.

    Basic Usage:
        >>> from vFense.user._db import fetch_user
        >>> username = 'admin'
        >>> fetch_user(username, without_fields=['password'])

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
    data = {}
    try:
        if not without_fields:
            data = (
                r
                .table(UserCollections.Users)
                .get(username)
                .run(conn)
            )

        else:
            data = (
                r
                .table(UserCollections.Users)
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
def fetch_users(
    customer_name=None, username=None,
    without_fields=None, conn=None
    ):
    """Retrieve all users that is in the database by customer_name or
        all of the customers or by regex.

    Kwargs:
        customer_name (str): Name of the customer, where the agent
            is located.
        username (str): Name of the user you are searching for.
            This is a regular expression match.
        without_fields (list): List of fields you do not want to include.

    Basic Usage:
        >>> from vFense.user._db import fetch_users
        >>> customer_name = 'default'
        >>> username = 'al'
        >>> without_fields = ['password']
        >>> fetch_users(customer_name, username, without_field)

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
    data = []
    try:
        if not customer_name and not username and not without_fields:
            data = list(
                r
                .table(UserCollections.Users)
                .run(conn)
            )

        elif not customer_name and not username and without_fields:
            data = list(
                r
                .table(UserCollections.Users)
                .without(without_fields)
                .run(conn)
            )

        elif not customer_name and username and without_fields:
            data = list(
                r
                .table(CustomerCollections.CustomersPerUser)
                .filter(
                    lambda x:
                    x[CustomerPerUserKeys.UserName].match("(?i)" + username)
                )
                .eq_join(
                    lambda x:
                    x[CustomerPerUserKeys.UserName],
                    r.table(UsersCollection)
                )
                .zip()
                .without(without_fields)
                .run(conn)
            )

        elif customer_name and username and without_fields:
            data = list(
                r
                .table(CustomerCollections.CustomersPerUser)
                .get_all(
                    customer_name, index=CustomerPerUserIndexes.CustomerName
                )
                .filter(
                    lambda x:
                    x[CustomerPerUserKeys.UserName].match("(?i)" + username)
                )
                .eq_join(
                    lambda x:
                    x[CustomerPerUserKeys.UserName],
                    r.table(UsersCollection)
                )
                .zip()
                .without(without_fields)
                .run(conn)
            )

        elif customer_name and not username and not without_fields:
            data = list(
                r
                .table(CustomerCollections.CustomersPerUser)
                .get_all(
                    customer_name, index=CustomerPerUserIndexes.CustomerName
                )
                .eq_join(
                    lambda x:
                    x[CustomerPerUserKeys.UserName],
                    r.table(UsersCollection)
                )
                .zip()
                .run(conn)
            )

        elif customer_name and not username and without_fields:
            data = list(
                r
                .table(CustomerCollections.CustomersPerUser)
                .get_all(
                    customer_name, index=CustomerPerUserIndexes.CustomerName
                )
                .eq_join(
                    lambda x:
                    x[CustomerPerUserKeys.UserName],
                    r.table(UsersCollection)
                )
                .zip()
                .without(without_fields)
                .run(conn)
            )

        elif customer_name and username and not without_fields:
            data = list(
                r
                .table(CustomerCollections.CustomersPerUser)
                .get_all(
                    customer_name, index=CustomerPerUserIndexes.CustomerName
                )
                .filter(
                    lambda x:
                    x[CustomerPerUserKeys.UserName].match("(?i)" + username)
                )
                .eq_join(
                    lambda x:
                    x[CustomerPerUserKeys.UserName],
                    r.table(UsersCollection)
                )
                .zip()
                .run(conn)
            )

    except Exception as e:
        logger.exception(e)

    return(data)


@time_it
@db_create_close
@return_status_tuple
def insert_user(user_data, conn=None):
    """ Insert a new user and its properties into the database
        This function should not be called directly.
    Args:
        user_data(list|dict): Can either be a list of dictionaries or a dictionary
            of the data you are inserting.

    Basic Usage:
        >>> from vFense.user._db import insert_user_data
        >>> user_data = {'customer_name': 'vFense', 'needs_reboot': 'no'}
        >>> insert_user_data(user_data)

    Return:
        Tuple (status_code, count, error, generated ids)
        >>> (2001, 1, None, [])
    """
    data = {}
    try:
        data = (
            r
            .table(UserCollections.Users)
            .insert(user_data)
            .run(conn)
        )

    except Exception as e:
        logger.exception(e)

    return(data)


@time_it
@db_create_close
@return_status_tuple
def update_user(username, user_data, conn=None):
    """Update  user's properties
    Args:
        username (str): username of the user you are updating
        user_data (list|dict): Dictionary of the data you are updating

    Basic Usage::
        >>> from vFense.user._db import update_user
        >>> username = 'admin'
        >>> data = {'production_level': 'Development', 'needs_reboot': 'no'}
        >>> update_user(username, data)

    Return:
        Tuple (status_code, count, error, generated ids)
        >>> (2001, 1, None, [])
    """
    data = {}
    try:
        data = (
            r
            .table(UserCollections.Users)
            .get(username)
            .update(user_data)
            .run(conn)
        )

    except Exception as e:
        logger.exception(e)

    return(data)


@time_it
@db_create_close
@return_status_tuple
def delete_user(username, conn=None):
    """ Delete a user and all of its properties
    Args:
        username (str): username of the user you are deleteing.

    Basic Usage::
        >>> from vFense.user._db import delete_user
        >>> username = 'admin'
        >>> delete_user(username)

    Return:
        Tuple (status_code, count, error, generated ids)
        >>> (2001, 1, None, [])
    """
    data = {}
    try:
        data = (
            r
            .table(UserCollections.Users)
            .get(username)
            .delete()
            .run(conn)
        )

    except Exception as e:
        logger.exception(e)

    return(data)
