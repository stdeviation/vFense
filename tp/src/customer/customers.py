import logging
from datetime import datetime
from time import mktime
from vFense.customer import *
from vFense.customer._db import insert_customer_data, fetch_customer_info
from vFense.db.client import r, return_status_tuple, results_message
from vFense.errorz.error_messages import GenericResults
from vFense.errorz.status_codes import DbCodes


def get_customer(customer_name, keys_to_pluck=None):
    """
    Retrieve customer information.
    :param customer_name:  Name of the customer.
    :param keys_to_pluck:  (Optional) list of keys you want to
        retreive from the db.
    Basic Usage::
        >>> from vFense.customer._db import fetch_customer_info
        >>> customer_name = 'default'
        >>> get_customer_info(customer_name)
    """
    customer_data = {}
    if keys_to_pluck:
        customer_data = fetch_customer_info(customer_name, keys_to_pluck)
    else:
        customer_data = fetch_customer_info(customer_name)

    return(customer_data)

def validate_customer_names(customer_names):
    """
    Validate a list if customer names.
    :param customer_names: List of customer names.

    Basic Usage::
        >>> from vFense.customer.customers import validate_customer_names
        >>> customer_names = ['default', 'linux']
        >>> validate_customer_names(customer_names)
        [
            {
                u'customer_name': u'default',
                u'user_name': u'agent',
                u'id': u'ccac5136-3077-4d2c-a391-9bb15acd79fe'
            }
        ]
    """
    validated = True
    invalid_names = []
    valid_names = []
    if isinstance(customer_names, list):
        for customer_name in customer_names:
            if get_customer(customer_name):
                valid_names.append(customer_name)
            else:
                invalid_names.append(customer_name)
                validated = False

    return(validated, valid_names, invalid_names)


@results_message
def create_customer(
    customer_name,
    http_application_url_location=None,
    net_throttle=0,
    cpu_throttle='normal',
    operation_queue_ttl=10,
    username=None,
    uri=None,
    method=None,
    conn=None):
    """
    Create a new customer
    :param customer_name:  Name of the customer.
    :param http_application_url_location:  (Optional) This is the http url
        from which the agents will download its applications from.
    :param net_throttle:  (Optional) Bandwidth throttling, the default
        is 0. which means not to throttle.
    :param cpu_throttle:  (Optional) Cpu throttling, the default
        is normal. which means not to throttle.
    :param operation_queue_ttl:  (Optional) How many minutes until
        an operation is considered expired after it was created 
        on the server. The default is 10 minutes.
    Basic Usage::
        >>> from vFense.customer._db import create_customer
        >>> customer_name = 'default'
        >>> http_application_url_location='https://10.0.0.16/packages/',
        >>> create_customer(customer_name, http_application_url_location)
    """
    if not http_application_url_location:
        http_application_url_location = (
            get_customer_info(
                DEFAULT_CUSTOMER,
                [CustomerKeys.PackageUrl]
            ).get(CustomerKeys.PackageUrl)
        )

    data = {
        CustomerKeys.CustomerName: customer_name,
        CustomerKeys.PackageUrl: http_application_url_location,
        CustomerKeys.NetThrottle: net_throttle,
        CustomerKeys.CpuThrottle: cpu_throttle,
        CustomerKeys.OperationTtl: operation_queue_ttl
    }
    object_status, object_count, error, generated_ids = (
        insert_customer_data(data)
    )
    try:
        results = (
            object_status, customer_name, 'customer', data, error,
            username, uri, method
        )

    except Exception as e:
        results = (
            object_status, None, 'customer', data, e,
            username, uri, method
        )

    return(results)
