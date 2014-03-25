import logging

from vFense.core.customer import *
from vFense.core.group._constants import *
from vFense.core.user import *
from vFense.core.user._constants import *
from vFense.core.decorators import return_status_tuple, time_it
from vFense.db.client import db_create_close, r

logging.config.fileConfig('/opt/TopPatch/conf/logging.config')
logger = logging.getLogger('rvapi')


@time_it
@db_create_close
def fetch_customer(customer_name, keys_to_pluck=None, conn=None):
    """Retrieve customer information
    Args:
        customer_name (str):   Name of the customer.

    Kwargs:
        keys_to_pluck (array): list of keys you want to retreive from the db.

    Basic Usage::
        >>> from vFense.customer._db import fetch_customer
        >>> customer_name = 'default'
        >>> fetch_customer(customer_name)

    Returns:
        Returns a Dict of the properties of a customer
        {
            u'cpu_throttle': u'normal',
            u'package_download_url_base': u'http: //10.0.0.21/packages/',
            u'operation_ttl': 10,
            u'net_throttle': 0,
            u'customer_name': u'default'
        }
    """
    data = []
    try:
        if customer_name and keys_to_pluck:
            data = (
                r
                .table(CustomerCollections.Customers)
                .get(customer_name)
                .pluck(keys_to_pluck)
                .run(conn)
            )
        elif customer_name and not keys_to_pluck:
            data = (
                r
                .table(CustomerCollections.Customers)
                .get(customer_name)
                .run(conn)
            )

    except Exception as e:
        logger.exception(e)

    return(data)


@time_it
@db_create_close
def fetch_customers(match=None, keys_to_pluck=None, conn=None):
    """Retrieve all customers or just customers based on regular expressions
    Kwargs:
        match (str): Regular expression of the customer name
            you are searching for.
        keys_to_pluck (array): list of keys you want to retreive from the db.

    Returns:
        Returns a List of customers

    Basic Usage::
        >>> from vFense.customer._db import fetch_customers
        >>> fetch_customers()

    Return:
        List of customer properties.
        [
            {
                u'cpu_throttle': u'normal',
                u'package_download_url_base': u'http: //10.0.0.21/packages/',
                u'operation_ttl': 10,
                u'net_throttle': 0,
                u'customer_name': u'default'
            },
            {
                u'cpu_throttle': u'normal',
                u'package_download_url_base': u'http: //10.0.0.21/packages/',
                u'operation_ttl': 10,
                u'net_throttle': 0,
                u'customer_name': u'TopPatch'
            }
        ]
    """
    data = []
    try:
        if match and keys_to_pluck:
            data = list(
                r
                .table(CustomerCollections.Customers)
                .filter(
                    lambda name:
                    name[CustomerKeys.CustomerName].match("(?i)" + match)
                )
                .pluck(keys_to_pluck)
                .run(conn)
            )

        elif match and not keys_to_pluck:
            data = list(
                r
                .table(CustomerCollections.Customers)
                .filter(
                    lambda name:
                    name[CustomerKeys.CustomerName].match("(?i)" + match)
                )
                .run(conn)
            )

        elif not match and not keys_to_pluck:
            data = list(
                r
                .table(CustomerCollections.Customers)
                .run(conn)
            )

        elif not match and keys_to_pluck:
            data = list(
                r
                .table(CustomerCollections.Customers)
                .pluck(keys_to_pluck)
                .run(conn)
            )

    except Exception as e:
        logger.exception(e)

    return(data)


@time_it
@db_create_close
def fetch_users_for_customer(customer_name, keys_to_pluck=None, conn=None):
    """Retrieve all the users for a customer
    Args:
        customer_name (str):  Name of the customer.

    Kwargs:
        keys_to_pluck (list):  list of keys you want to retreive from the db.

    Basic Usage:
        >>> from vFense.customer._db import fetch_users_for_customer
        >>> customer_name = 'default'
        >>> fetch_users_for_customer(customer_name)

    Returns:
        Returns a List of users for a customer

        [
            {
                u'user_name': u'alien',
                u'id': u'ba9682ef-7adf-4916-8002-9637485b30d8',
                u'customer_name': u'default'
            },
            {
                u'user_name': u'admin',
                u'id': u'6bd86dcd-43fc-424e-88f1-684ce2189d88',
                u'customer_name': u'default'
            }
        ]
    """
    data = []
    try:
        if customer_name and keys_to_pluck:
            data = list(
                r
                .table(CustomerCollections.CustomersPerUser)
                .get_all(customer_name, index=CustomerPerUserIndexes.CustomerName)
                .pluck(keys_to_pluck)
                .run(conn)
            )
        elif customer_name and not keys_to_pluck:
            data = list(
                r
                .table(CustomerCollections.CustomersPerUser)
                .get_all(customer_name, index=CustomerPerUserIndexes.CustomerName)
                .run(conn)
            )

    except Exception as e:
        logger.exception(e)

    return(data)


@time_it
@db_create_close
def fetch_customers_for_user(username, keys_to_pluck=None, conn=None):
    """Retrieve all the customers for a user
    Args:
        username (str):  Name of the user.

    Kwargs:
        keys_to_pluck (list):  list of keys you want to retreive from the db.

    Basic Usage::
        >>> from vFense.customer._db import fetch_customers_for_user
        >>> customer_name = 'default'
        >>> fetch_customers_for_user(username)

    Returns:
        Returns a List of customers for a user.
        [
            {
                u'user_name': u'admin',
                u'id': u'6bd86dcd-43fc-424e-88f1-684ce2189d88',
                u'customer_name': u'default'
            }
        ]
    """
    data = []
    try:
        if username and keys_to_pluck:
            data = list(
                r
                .table(CustomerCollections.CustomersPerUser)
                .get_all(username, index=CustomerPerUserIndexes.UserName)
                .pluck(keys_to_pluck)
                .run(conn)
            )
        elif username and not keys_to_pluck:
            data = list(
                r
                .table(CustomerCollections.CustomersPerUser)
                .get_all(username, index=CustomerPerUserIndexes.UserName)
                .run(conn)
            )

    except Exception as e:
        logger.exception(e)

    return(data)


@time_it
@db_create_close
def users_exists_in_customer(username, customer_name, conn=None):
    """Verify if username is part of customer
    Args:
        username:  Name of the user.
        customer_name:  Name of the customer.

    Basic Usage:
        >>> from vFense.core.customer._db import user_exists_in_customers
        >>> username = 'admin'
        >>> customer_name = 'default'
        >>> user_exists_in_customers(username, customer_name)

    Return:
        Boolean

    """
    exist = False
    try:
        empty = (
            r
            .table(CustomerCollections.CustomersPerUser)
            .get_all(customer_name, index=CustomerPerUserIndexes.CustomerName)
            .is_empty()
            .run(conn)
        )
        if not empty:
            exist = True

    except Exception as e:
        logger.exception(e)

    return(exist)


@time_it
@db_create_close
@return_status_tuple
def insert_customer(customer_data, conn=None):
    """Insert a new customer into the database
    Args:
        customer_data (list|dict): Can either be a list of dictionaries or a dictionary
        of the data you are inserting.

    Basic Usage:
        >>> from vFense.customer._db import insert_customer
        >>> customer_data = {'customer_name': 'vFense', 'operation_queue_ttl': 10}
        >>> insert_customer(data)

    Return:
        Tuple (status_code, count, error, generated ids)
        >>> (2001, 1, None, [])
    """
    data = {}
    try:
        data = (
            r
            .table(CustomerCollections.Customers)
            .insert(customer_data)
            .run(conn)
        )

    except Exception as e:
        logger.exception(e)

    return(data)


@time_it
@db_create_close
@return_status_tuple
def update_customer(customer_name, customer_data, conn=None):
    """Update verious fields of a customer
    Args:
        customer_name(str): customer_name.
        customer_data(dict): Dictionary of the data you are updateing.

    Basic Usage::
        >>> from vFense.customer._db import update_customer
        >>> customer_name = 'default'
        >>> customer_data = {'operation_queue_ttl': 10}
        >>> update_customer(customer_data)

    Return:
        Tuple (status_code, count, error, generated ids)
        >>> (2001, 1, None, [])
    """
    data = {}
    try:
        data = (
            r
            .table(CustomerCollections.Customers)
            .get(customer_name)
            .update(customer_data)
            .run(conn)
        )

    except Exception as e:
        logger.exception(e)

    return(data)


@time_it
@db_create_close
@return_status_tuple
def insert_user_per_customer(user_data, conn=None):
    """Add a customer to a user, this function should not be called directly.
    Args:
        user_data(list|dict): Can either be a list of dictionaries or a
        dictionary of the data you are inserting.

    Basic Usage:
        >>> from vFense.customer._db import insert_user_per_customer
        >>> user_data = {'customer_name': 'vFense', 'needs_reboot': 'no'}
        >>> insert_user_per_customer(user_data)

    Return:
        Tuple (status_code, count, error, generated ids)
        >>> (2001, 1, None, [])
    """
    data = {}
    try:
        data = (
            r
            .table(CustomerCollections.CustomersPerUser)
            .insert(user_data)
            .run(conn)
        )

    except Exception as e:
        logger.exception(e)

    return(data)


@time_it
@db_create_close
@return_status_tuple
def delete_user_in_customers(username, customer_names=None, conn=None):
    """Remove a customer from a user or remove all customers for a user.
    Args:
        username (str): Name of the user.

    Kwargs:
        customer_names (list): List of customer_names.

    Basic Usage::
        >>> from vFense.customer._db delete_user_in_customers
        >>> username = 'agent_api'
        >>> delete_user_in_customers(username)

    Return:
        Tuple (status_code, count, error, generated ids)
        >>> (2001, 1, None, [])
    """
    data = {}
    try:
        if customer_names:
            data = (
                r
                .expr(customer_names)
                .for_each(
                    lambda customer_name:
                    r
                    .table(CustomerCollections.CustomersPerUser)
                    .filter(
                        {
                            CustomerPerUserKeys.UserName: username,
                            CustomerPerUserKeys.CustomerName: customer_name
                        }
                    )
                    .delete()
                )
                .run(conn)
            )

        else:
            data = (
                r
                .table(CustomerCollections.CustomersPerUser)
                .filter(
                    {
                        CustomerPerUserKeys.UserName: username,
                    }
                )
                .delete()
                .run(conn)
            )

    except Exception as e:
        logger.exception(e)

    return(data)


@time_it
@db_create_close
@return_status_tuple
def delete_customer(customer_name, conn=None):
    """Delete a customer from the database.
    Args:
        customer_name: Name of the customer

    Basic Usage::
        >>> from vFense.customer._db delete_customer
        >>> customer_name = 'test'
        >>> delete_customer(customer_name)

    Return:
        Tuple (status_code, count, error, generated ids)
        >>> (2001, 1, None, [])
    """
    data = {}
    try:
        data = (
            r
            .table(CustomerCollections.Customers)
            .get(customer_name)
            .delete()
            .run(conn)
        )

    except Exception as e:
        logger.exception(e)

    return(data)
