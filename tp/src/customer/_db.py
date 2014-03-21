from vFense.customer import *
import logging
from datetime import datetime
from time import mktime
from vFense.db.client import db_create_close, r, db_connect, return_status_tuple
from vFense.errorz.error_messages import AgentResults, GenericResults
from vFense.errorz.status_codes import DbCodes

logging.config.fileConfig('/opt/TopPatch/conf/logging.config')
logger = logging.getLogger('rvapi')

@db_create_close
def fetch_customer_info(customer_name, keys_to_pluck=None, conn=None):
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


@db_create_close
@return_status_tuple
def insert_customer_data(customer_data, conn=None):
    """
    :param customer_data: Can either be a list of dictionaries or a dictionary
        of the data you are inserting.

    Basic Usage::
        >>> from vFense.customer._db import insert_customer_data
        >>> customer_data = {'customer_name': 'vFense', 'operation_queue_ttl': 10}
        >>> insert_customer_data(data)
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
        logger.exception(status)

    return(data)
 
@db_create_close
@return_status_tuple
def update_customer_data(customer_name, customer_data, conn=None):
    """
    :param customer_data: Dictionary of the data you are inserting.

    Basic Usage::
        >>> from vFense.customer._db import update_customer_data
        >>> customer_data = {'customer_name': 'vFense', 'operation_queue_ttl': 10}
        >>> update_customer_data(data)
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
        logger.exception(status)

    return(data)
 
