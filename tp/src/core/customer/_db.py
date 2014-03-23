import logging

from vFense.core.customer import *
from vFense.core.user import *
from vFense.core.decorators import return_status_tuple, time_it
from vFense.db.client import db_create_close, r

logging.config.fileConfig('/opt/TopPatch/conf/logging.config')
logger = logging.getLogger('rvapi')


@time_it
@db_create_close
def fetch_customer(customer_name, keys_to_pluck=None, conn=None):
    """
    Retrieve customer information
    :param customer_name:  Name of the customer.
    :param keys_to_pluck:  (Optional) list of keys you want to
        retreive from the db.
    Basic Usage::
        >>> from vFense.customer._db import fetch_customer_info
        >>> customer_name = 'default'
        >>> fetch_customer_info(customer_name)
    """
    data = []
    try:
        if customer_name and keys_to_pluck:
            data = (
                r
                .table(CustomersCollection)
                .get(customer_name)
                .pluck(keys_to_pluck)
                .run(conn)
            )
        elif customer_name and not keys_to_pluck:
            data = (
                r
                .table(CustomersCollection)
                .get(customer_name)
                .run(conn)
            )

    except Exception as e:
        logger.exception(e)

    return(data)

@time_it
@db_create_close
def fetch_customers_for_user(username, keys_to_pluck=None, conn=None):
    """
    Retrieve customer information
    :param username:  Name of the user.
    :param keys_to_pluck:  (Optional) list of keys you want to
        retreive from the db.
    Basic Usage::
        >>> from vFense.customer._db import fetch_customers_for_user
        >>> customer_name = 'default'
        >>> fetch_customers_for_user(username)
    """
    data = []
    try:
        if username and keys_to_pluck:
            data = (
                r
                .table(CustomersPerUserCollection)
                .get_all(username, index=CustomerPerUserIndexes.UserName)
                .pluck(keys_to_pluck)
                .run(conn)
            )
        elif username and not keys_to_pluck:
            data = (
                r
                .table(CustomersCollection)
                .get_all(username, index=CustomerPerUserIndexes.UserName)
                .run(conn)
            )

    except Exception as e:
        logger.exception(e)

    return(data)


@time_it
@db_create_close
def users_exists_in_customer(username, customer_name, conn=None):
    """
    Retrieve customer information
    :param customer_name:  Name of the customer.
    Basic Usage::
        >>> from vFense.core.customer._db import user_exists_in_customers
        >>> customer_name = 'default'
        >>> user_exists_in_customers(customer_name)
    """
    data = []
    try:
        data = (
            r
            .table(CustomersPerUserCollection)
            .get_all(customer_name, index=UserPerCustomerIndexes.CustomerName)
            .filter(
                {
                    CustomerPerUserKeys.UserName: username
                }
            )
            .run(conn)
        )

    except Exception as e:
        logger.exception(e)

    return(data)


@time_it
@db_create_close
@return_status_tuple
def insert_customer(customer_data, conn=None):
    """
    :param customer_data: Can either be a list of dictionaries or a dictionary
        of the data you are inserting.

    Basic Usage::
        >>> from vFense.customer._db import insert_customer
        >>> customer_data = {'customer_name': 'vFense', 'operation_queue_ttl': 10}
        >>> insert_customer(data)
        >>> (2001, 1, None, [])
    """
    data = {}
    try:
        data = (
            r
            .table(CustomersCollection)
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
    """
    :param customer_name: customer_name.
    :param customer_data: Dictionary of the data you are updateing.

    Basic Usage::
        >>> from vFense.customer._db import update_customer
        >>> customer_name = 'default'
        >>> customer_data = {'operation_queue_ttl': 10}
        >>> update_customer(customer_data)
        >>> (2001, 1, None, [])
    """
    data = {}
    try:
        data = (
            r
            .table(CustomersCollection)
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
    """
    This function should not be called directly.
    :param user_data: Can either be a list of dictionaries or a dictionary
        of the data you are inserting.

    Basic Usage::
        >>> from vFense.customer._db import insert_user_per_customer
        >>> user_data = {'customer_name': 'vFense', 'needs_reboot': 'no'}
        >>> insert_user_per_customer(user_data)
        >>> (2001, 1, None, [])
    """
    data = {}
    try:
        data = (
            r
            .table(CustomersPerUserCollection)
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
    """
    :param username: username
    :param customer_names: (Optional) List of customer_names

    Basic Usage::
        >>> from vFense.customer._db delete_user_in_customers
        >>> username = 'agent_api'
        >>> delete_user_in_customers(username)
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
                    .table(CustomersPerUserCollection)
                    .filter(
                        {
                            CustomersPerUserKeys.UserName: username,
                            CustomersPerUserKeys.CustomerName: customer_name
                        }
                    )
                    .delete()
                )
                .run(conn)
            )

        else:
            data = (
                r
                .table(CustomersPerUserCollection)
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
    """
    :param customer_name: customer_name

    Basic Usage::
        >>> from vFense.customer._db delete_customer
        >>> customer_name = 'test'
        >>> delete_customer(customer_name)
        >>> (2001, 1, None, [])
    """
    data = {}
    try:
        data = (
            r
            .table(CustomersCollection)
            .get(customer_name)
            .delete()
            .run(conn)
        )

    except Exception as e:
        logger.exception(e)

    return(data)
