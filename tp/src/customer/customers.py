import logging
from datetime import datetime
from time import mktime

from vFense._db import retrieve_object
from vFense.customer import *
from vFense.user import *
from vFense.customer._db import insert_customer_data, fetch_customer, \
    insert_user_per_customer
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
        >>> from vFense.customer._db import fetch_customer
        >>> customer_name = 'default'
        >>> get_customer(customer_name)
    """
    customer_data = {}
    if keys_to_pluck:
        customer_data = fetch_customer(customer_name, keys_to_pluck)
    else:
        customer_data = fetch_customer(customer_name)

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
    results = None
    user_exist = retrieve_object(username, UsersCollection)
    if customers_are_valid[0]:
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
def create_customer(
    customer_name,
    username,
    http_application_url_location=None,
    net_throttle=0,
    cpu_throttle='normal',
    operation_queue_ttl=10,
    uri=None,
    method=None,
    conn=None):
    """
    Create a new customer
    :param customer_name:  Name of the customer.
    :param username:  User which has permissions to this customer.
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
        >>> from vFense.customer.customers import create_customer
        >>> customer_name = 'vFense'
        >>> username = 'api_user'
        >>> http_application_url_location='https://10.0.0.16/packages/'
        >>> create_customer(
                customer_name, api_user,
                http_application_url_location
            )
            {
                'uri': None,
                'rv_status_code': 1010,
                'http_method': None,
                'http_status': 200,
                'message': 'api_user - create user test123 was created',
                'data': {
                    'current_customer': 'default',
                    'user_id': 'test123',
                    'full_name': 'tester 4 life and all',
                    'user_name': 'test123',
                    'default_customer': 'default',
                    'password': '$2a$12$TeFDS1.ZPiDTMfL0Xv24xu2jAIknrdZBSsWiKFhjR5JCikcta/Kei',
                    'enabled': True,
                    'email': 'test@test.org'
                }
            }
    """
    customer_exist = get_customer(customer_name)
    if not customer_exist:
        if not http_application_url_location:
            http_application_url_location = (
                get_customer(
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
        if object_status == DbCodes.Inserted:
            add_user_to_customers(
                username, customer_name, username, uri, method
            )

            if username != ADMIN_USER:
                add_user_to_customers(
                    ADMIN_USER, customer_name, username, uri, method
                )

        results = (
            object_status, customer_name, 'customer', data, error,
            username, uri, method
        )

    else:
        error = 'customer_name %s already exists' % (customer_name)
        results = (
            DbCodes.Unchanged, customer_name, error, [], None,
            username, uri, method
        )

    return(results)
