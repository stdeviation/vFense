import logging

from vFense.core._db import retrieve_object
from vFense.core.customer import *
from vFense.core.user import *
from vFense.core.customer._db import insert_customer, fetch_customer, \
    insert_user_per_customer, delete_user_in_customers , delete_customer, \
    users_exists_in_customers, update_customer

from vFense.core.decorators import results_message, time_it
from vFense.errorz.status_codes import DbCodes

logging.config.fileConfig('/opt/TopPatch/conf/logging.config')
logger = logging.getLogger('rvapi')


@time_it
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


@time_it
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


@time_it
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
                    CustomerPerUserKeys.CustomerName: customer_name,
                    CustomerPerUserKeys.UserName: username,
                }
            )
            data_list.append(data_to_add)

        if user_exist:
            object_status, object_count, error, generated_ids = (
                insert_user_per_customer(data_to_add)
            )
            results = (
                object_status, generated_ids, 'users add to customers',
                data_to_add, error, user_name, uri, method
            )

        elif not user_exist:
            status_code = DbCodes.Errors
            status_error = 'User name is invalid: %s' % (username)
            results = (
                status_code, username, 'users add to customers',
                customer_names, status_error, user_name, uri, method
            )

    elif not customers_are_valid[0]:
        status_code = DbCodes.Errors
        status_error = (
            'Customer names are invalid: %s' % (customers_are_valid[2])
        )
        results = (
            status_code, None, 'users add to customers',
            customer_names, status_error, user_name, uri, method
        )

    return(results)


@time_it
@results_message
def create_customer(
    customer_name, username=None,
    http_application_url_location=None,
    net_throttle=0, cpu_throttle='normal',
    operation_queue_ttl=10, uri=None,
    method=None, init=False
    ):
    """
    Create a new customer
    :param customer_name: Name  of the customer.

    :param username: (Optional, if passed with init)
        User which has permissions to this customer.

    :param http_application_url_location: (Optional)
        Default=http://ip_address/packages/
        This is the http url from which the agents will
        download its applications from.

    :param net_throttle:  (Optional) Default=0 (0, means not to throttle)
        Bandwidth throttling is calculated in kb.

    :param cpu_throttle:  (Optional) Default=normal (normal, means not to throttle)
        possbile values (idle, below_normal, normal, above_noraml, high)

    :param operation_queue_ttl:  (Optional) Default=10
        How many minutes until an operation is considered expired after
        it was created on the server.

    :param init:  (Optional) Default=False, If init is set to True,
        do not add a user to this customer

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
            'message': 'api_user - customer vFense was created',
            'data': {
                'cpu_throttle': 'normal',
                'package_download_url_base': 'https: //10.0.0.21/packages/',
                'operation_ttl': 10,
                'net_throttle': 0,
                'customer_name': 'vFense'
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
            insert_customer(data)
        )
        if object_status == DbCodes.Inserted and not init and username:
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


@time_it
@results_message
def edit_customer(customer_name, **kwargs):
    """
    Edit a customer properties.
    :param customer_name: Name  of the customer you are editing.

    :param http_application_url_location: (Optional)
        Default=http://ip_address/packages/
        This is the http url from which the agents will
        download its applications from.

    :param net_throttle:  (Optional) Default=0 (0, means not to throttle)
        Bandwidth throttling is calculated in kb.

    :param cpu_throttle:  (Optional) Default=normal (normal, means not to throttle)
        possbile values (idle, below_normal, normal, above_noraml, high)

    :param operation_queue_ttl:  (Optional) Default=10
        How many minutes until an operation is considered expired after
        it was created on the server.

    Basic Usage::
        >>> from vFense.core.customer.customers edit_customer
        >>> customer_name = 'agent_api'
        >>> edit_customer(customer_name, operation_queue_ttl=5)
        {
            'uri': None,
            'rv_status_code': 1008,
            'http_method': None,
            'http_status': 200,
            'message': 'None - customer modified - default was updated',
            'data': {
                'operation_queue_ttl': 5
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

    try:
        status_code, count, error, generated_ids = (
            update_customer(customer_name, kwargs)
        )

        status = 'customer modified - '
        results = (
            status_code, customer_name, status, kwargs, error,
            user_name, uri, method
        )

    except Exception as e:
        logger.exception(e)
        status = 'Failed to modify customer %s: - ' % (customer_name)
        results = (
            DbCodes.Errors, customer_name, status, [], e,
            user_name, uri, method
        )

    return(results)


@time_it
@results_message
def remove_customers_from_user(
    username, customer_names=None,
    user_name=None, uri=None, method=None
    ):
    """
    :param username: username
    :param customer_names: (Optional) List of customer_names

    Basic Usage::
        >>> from vFense.customer.customers remove_customers_from_user
        >>> username = 'agent_api'
        >>> remove_customers_from_user(username)
        >>> (2001, 1, None, [])
    """
    try:
        status_code, count, errors, generated_ids = (
            delete_user_in_customers(username, customer_names)
        )
        status = 'removed customers from user %s' % (username)
        results = (
            status_code, username, status, [], None,
            user_name, uri, method
        )

    except Exception as e:
        logger.exception(e)
        status = 'Failed to remove customers from user %s' % (username)
        results = (
            DbCodes.Errors, username, status, [], e,
            user_name, uri, method
        )

    return(results)


@time_it
@results_message
def remove_customer(customer_name, user_name=None, uri=None, method=None):
    """
    :param customer_name: customer_name

    Basic Usage::
        >>> from vFense.core.customer.customers remove_customer
        >>> customer_name = 'nyc'
        >>> remove_customer(customer_name)
        >>> (2001, 1, None, [])
    """
    status = remove_customer.func_name + ' - '
    try:
        customer_exist = get_customer(customer_name)
        users_exists_in_customers(customer_name)

        if customer_exist and not users_exists_in_customers:
            msg = 'removed customers from user %s' % (username)

            status_code, count, errors, generated_ids = (
                delete_customer(customer_name)
            )

            results = (
                status_code, customer_name, status + msg, [], errors,
                user_name, uri, method
            )


        elif customer_exist and users_exists_in_customers:
            msg = (
                'users still exist for customer %s' % customer_name
            )

            results = (
                DbCodes.Unchanged, customer_name, status + msg, [], None,
                user_name, uri, method
            )

        else:
            msg = 'customer %s does not exist' % (customer_name)
            results = (
                DbCodes.Skipped, customer_name, status + msg, [], None,
                user_name, uri, method
            )

    except Exception as e:
        logger.exception(e)
        msg = 'Failed to remove customers from user %s' % (username)
        results = (
            DbCodes.Errors, customer_name, status + msg, [], e,
            user_name, uri, method
        )

    return(results)
