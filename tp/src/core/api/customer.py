import json
import logging
import logging.config

from vFense.core._constants import CPUThrottleValues
from vFense.core.api._constants import ApiArguments, ApiValues
from vFense.core.api.base import BaseHandler
from vFense.core.decorators import authenticated_request, convert_json_to_arguments

from vFense.core.permissions._constants import *
from vFense.core.permissions.permissions import verify_permission_for_user, \
    return_results_for_permissions

from vFense.core.permissions.decorators import check_permissions
from vFense.core.agent import *
from vFense.core.user._constants import DefaultUsers
from vFense.core.agent.agents import change_customer_for_all_agents_in_customer, \
    remove_all_agents_for_customer

from vFense.core.user import *
from vFense.core.customer import CustomerKeys

from vFense.core.customer.customers import get_properties_for_customer, \
    get_properties_for_all_customers, get_customer, remove_customer, \
    remove_customers, edit_customer, create_customer

from vFense.core.user.users import add_users_to_customer, \
    remove_users_from_customer

from vFense.errorz._constants import ApiResultKeys
from vFense.errorz.error_messages import GenericResults
from vFense.errorz.results import Results
from vFense.errorz.status_codes import CustomerFailureCodes, CustomerCodes
from vFense.plugins.patching.patching import remove_all_apps_for_customer, \
    change_customer_for_apps_in_customer

logging.config.fileConfig('/opt/TopPatch/conf/logging.config')
logger = logging.getLogger('rvapi')


class Customer(object):
    """Used to represent an instance of a customer."""

    def __init__(
        self, name, net_throttle=None, cpu_throttle=None,
        server_queue_ttl=None, agent_queue_ttl=None,
        package_download_url=None
    ):
        self.name = name
        self.net_throttle = net_throttle
        self.cpu_throttle = cpu_throttle
        self.server_queue_ttl = server_queue_ttl
        self.agent_queue_ttl = agent_queue_ttl
        self.package_download_url = package_download_url

        if net_throttle:
            self.net_throttle = int(net_throttle)

        if server_queue_ttl:
            self.server_queue_ttl = int(server_queue_ttl)

        if agent_queue_ttl:
            self.agent_queue_ttl = int(agent_queue_ttl)

    def get_invalid_fields(self):
        """Check the customer for any invalid fields.
        
        Returns:
            (list): List of key/value pair dictionaries corresponding
                to the invalid fields.
        """
        invalid_fields = []

        if not isinstance(self.name, basestring):
            invalid_fields.append(
                {CustomerKeys.CustomerName: self.name}
            )

        if self.net_throttle and not isinstance(self.net_throttle, int):
            invalid_fields.append(
                {CustomerKeys.NetThrottle: self.net_throttle}
            )

        if self.cpu_throttle:
            if self.cpu_throttle not in CPUThrottleValues.VALID_VALUES:
                invalid_fields.append(
                    {CustomerKeys.CpuThrottle: self.cpu_throttle}
                )

        if self.server_queue_ttl and not isinstance(self.server_queue_ttl, int):
            invalid_fields.append(
                {CustomerKeys.ServerQueueTTL: self.server_queue_ttl}
            )

        if self.agent_queue_ttl and not isinstance(self.agent_queue_ttl, int):
            invalid_fields.append(
                {CustomerKeys.AgentQueueTTL: self.agent_queue_ttl}
            )

        # TODO: check for invalid package url

        return invalid_fields

    def to_dict(self):
        return {
            CustomerKeys.CustomerName: self.name,
            CustomerKeys.NetThrottle: self.net_throttle,
            CustomerKeys.CpuThrottle: self.cpu_throttle,
            CustomerKeys.ServerQueueTTL: self.server_queue_ttl,
            CustomerKeys.AgentQueueTTL: self.agent_queue_ttl,
            CustomerKeys.PackageUrl: self.package_download_url
        }

    def to_dict_non_null(self):
        """ Use to get non None attributes of customer. Useful when
        filling out just a few fields to update the customer in the db.

        Returns:
            (dict): a dictionary with non None items.
        """
        customer_dict = self.to_dict()

        return {k:customer_dict[k] for k in customer_dict
                if customer_dict[k] != None}


class CustomerHandler(BaseHandler):

    @authenticated_request
    @check_permissions(Permissions.ADMINISTRATOR)
    def get(self, customer_name):
        active_user = self.get_current_user()
        uri = self.request.uri
        method = self.request.method
        count = 0
        customer_data = {}
        try:
            customer_data = get_properties_for_customer(customer_name)
            if customer_data:
                count = 1
                results = (
                    GenericResults(
                        active_user, uri, method
                    ).information_retrieved(customer_data, count)
                ) 
            else:
                results = (
                    GenericResults(
                        active_user, uri, method
                    ).invalid_id(customer_name, 'customer')
                ) 
            self.set_status(results['http_status'])
            self.set_header('Content-Type', 'application/json')
            self.write(json.dumps(results, indent=4))

        except Exception as e:
            results = (
                GenericResults(
                    active_user, uri, method
                ).something_broke(active_user, 'User', e)
            )
            logger.exception(e)
            self.set_status(results['http_status'])
            self.set_header('Content-Type', 'application/json')
            self.write(json.dumps(results, indent=4))


    @authenticated_request
    @convert_json_to_arguments
    @check_permissions(Permissions.ADMINISTRATOR)
    def post(self, customer_name):
        active_user = self.get_current_user()
        uri = self.request.uri
        method = self.request.method
        results = None
        try:
            action = self.arguments.get(ApiArguments.ACTION, ApiValues.ADD)
            ### Add Users to this customer
            usernames = self.arguments.get(ApiArguments.USERNAMES)
            if not isinstance(usernames, list) and isinstance(usernames, str):
                usernames = usernames.split(',')

            if usernames:
                if action == ApiValues.ADD:
                    results = (
                        add_users_to_customer(
                            usernames, customer_name,
                            active_user, uri, method
                        )
                    )

                elif action == ApiValues.DELETE:
                    results = (
                        remove_users_from_customer(
                            usernames, customer_name,
                            active_user, uri, method
                        )
                    )
            self.set_status(results['http_status'])
            self.set_header('Content-Type', 'application/json')
            self.write(json.dumps(results, indent=4))

        except Exception as e:
            results = (
                GenericResults(
                    active_user, uri, method
                ).something_broke(active_user, 'Customers', e)
            )
            logger.exception(e)
            self.set_status(results['http_status'])
            self.set_header('Content-Type', 'application/json')
            self.write(json.dumps(results, indent=4))


    @authenticated_request
    @convert_json_to_arguments
    @check_permissions(Permissions.ADMINISTRATOR)
    def put(self, customer_name):
        active_user = self.get_current_user()
        uri = self.request.uri
        method = self.request.method
        results = None
        try:
            net_throttle = self.arguments.get(ApiArguments.NET_THROTTLE, None)
            cpu_throttle = self.arguments.get(ApiArguments.CPU_THROTTLE, None)
            server_queue_ttl = self.arguments.get(ApiArguments.SERVER_QUEUE_TTL, None)
            agent_queue_ttl = self.arguments.get(ApiArguments.AGENT_QUEUE_TTL, None)
            download_url = self.arguments.get(ApiArguments.DOWNLOAD_URL, None)

            customer = Customer(
                customer_name,
                net_throttle,
                cpu_throttle,
                server_queue_ttl,
                agent_queue_ttl,
                download_url
            )

            call_info = {
                ApiResultKeys.HTTP_METHOD: method,
                ApiResultKeys.URI: uri,
                ApiResultKeys.USERNAME: active_user,
            }

            results = edit_customer(customer, **call_info)

            self.set_status(results['http_status'])
            self.set_header('Content-Type', 'application/json')
            self.write(json.dumps(results, indent=4))

        except Exception as e:
            results = (
                GenericResults(
                    active_user, uri, method
                ).something_broke(active_user, 'Customers', e)
            )
            logger.exception(e)
            self.set_status(results['http_status'])
            self.set_header('Content-Type', 'application/json')
            self.write(json.dumps(results, indent=4))


    @authenticated_request
    @convert_json_to_arguments
    @check_permissions(Permissions.ADMINISTRATOR)
    def delete(self, customer_name):
        active_user = self.get_current_user()
        uri = self.request.uri
        method = self.request.method
        try:
            deleted_agents = (
                self.arguments.get(
                    ApiArguments.DELETE_ALL_AGENTS
                )
            )
            move_agents_to_customer = (
                self.arguments.get(
                    ApiArguments.MOVE_AGENTS_TO_CUSTOMER, None
                )
            )

            if move_agents_to_customer:
                customer_exist = get_customer(move_agents_to_customer)
                if not customer_exist:
                    msg = 'customer %s does not exist' % (move_agents_to_customer)
                    data = {
                        ApiResultKeys.INVALID_ID: move_agents_to_customer,
                        ApiResultKeys.MESSAGE: msg,
                        ApiResultKeys.VFENSE_STATUS_CODE: CustomerFailureCodes.CustomerDoesNotExist
                    }
                    results = (
                        Results(
                            active_user, uri, method
                        ).invalid_id(**data)
                    ) 
                    self.set_status(results['http_status'])
                    self.set_header('Content-Type', 'application/json')
                    self.write(json.dumps(results, indent=4))

                else:
                    results = (
                        remove_customer(
                            customer_name,
                            active_user, uri, method
                        )
                    )
                    self.set_status(results['http_status'])
                    self.set_header('Content-Type', 'application/json')
                    self.write(json.dumps(results, indent=4))
                    if (results[ApiResultKeys.VFENSE_STATUS_CODE] ==
                            CustomerCodes.CustomerDeleted):

                        change_customer_for_all_agents_in_customer(
                            customer_name, move_agents_to_customer
                        )
                        change_customer_for_apps_in_customer(
                            customer_name, move_agents_to_customer
                        )

            elif deleted_agents == ApiValues.YES:
                results = (
                    remove_customer(
                        customer_name,
                        active_user, uri, method
                    )
                )
                self.set_status(results['http_status'])
                self.set_header('Content-Type', 'application/json')
                self.write(json.dumps(results, indent=4))
                if (results[ApiResultKeys.VFENSE_STATUS_CODE] ==
                        CustomerCodes.CustomerDeleted):

                    remove_all_agents_for_customer(customer_name)
                    remove_all_apps_for_customer(customer_name)

            elif deleted_agents == ApiValues.NO:
                results = (
                    remove_customer(
                        customer_name,
                        active_user, uri, method
                    )
                )
                self.set_status(results['http_status'])
                self.set_header('Content-Type', 'application/json')
                self.write(json.dumps(results, indent=4))

            else:
                results = (
                    GenericResults(
                        active_user, uri, method
                    ).incorrect_arguments()
                )
                self.set_status(results['http_status'])
                self.set_header('Content-Type', 'application/json')
                self.write(json.dumps(results, indent=4))

        except Exception as e:
            results = (
                GenericResults(
                    active_user, uri, method
                ).something_broke(active_user, 'User', e)
            )
            logger.exception(e)
            self.set_status(results['http_status'])
            self.set_header('Content-Type', 'application/json')
            self.write(json.dumps(results, indent=4))


class CustomersHandler(BaseHandler):

    @authenticated_request
    @check_permissions(Permissions.ADMINISTRATOR)
    def get(self):
        active_user = self.get_current_user()
        uri = self.request.uri
        method = self.request.method
        all_customers = None
        customer_context = self.get_argument('customer_context', None)
        count = 0
        customer_data = {}
        if not customer_context and active_user == DefaultUsers.ADMIN:
            all_customers = True

        try:
            if customer_context:
                granted, status_code = (
                    verify_permission_for_user(
                        active_user, Permissions.ADMINISTRATOR, customer_context
                    )
                )
            else:
                granted, status_code = (
                    verify_permission_for_user(
                        active_user, Permissions.ADMINISTRATOR
                    )
                )
            if granted and not all_customers and not customer_context:
                customer_data = get_properties_for_all_customers(active_user)

            elif granted and all_customers and not customer_context:
                customer_data = get_properties_for_all_customers()

            elif granted and customer_context and not all_customers:
                customer_data = get_properties_for_customer(customer_context)

            elif not granted:
                results = (
                    return_results_for_permissions(
                        active_user, granted, status_code,
                        Permissions.ADMINISTRATOR, uri, method
                    )
                )

            if customer_data:
                count = len(customer_data)
                results = (
                    GenericResults(
                        active_user, uri, method
                    ).information_retrieved(customer_data, count)
                ) 
            self.set_status(results['http_status'])
            self.set_header('Content-Type', 'application/json')
            self.write(json.dumps(results, indent=4))

        except Exception as e:
            results = (
                GenericResults(
                    active_user, uri, method
                ).something_broke(active_user, 'Customers', e)
            )
            logger.exception(e)
            self.set_status(results['http_status'])
            self.set_header('Content-Type', 'application/json')
            self.write(json.dumps(results, indent=4))


    @authenticated_request
    @convert_json_to_arguments
    @check_permissions(Permissions.ADMINISTRATOR)
    def post(self):
        active_user = self.get_current_user()
        uri = self.request.uri
        method = self.request.method
        try:
            customer_name = (
                self.arguments.get(ApiArguments.CUSTOMER_NAME)
            )
            pkg_url = (
                self.arguments.get(ApiArguments.DOWNLOAD_URL, None)
            )
            net_throttle = (
                self.arguments.get(ApiArguments.NET_THROTTLE, 0)
            )
            cpu_throttle = (
                self.arguments.get(
                    ApiArguments.CPU_THROTTLE, CPUThrottleValues.NORMAL
                )
            )
            server_queue_ttl = (
                self.arguments.get(ApiArguments.SERVER_QUEUE_TTL, 10)
            )
            agent_queue_ttl = (
                self.arguments.get(ApiArguments.AGENT_QUEUE_TTL, 10)
            )

            results = (
                create_customer(
                    customer_name, active_user, pkg_url,
                    net_throttle, cpu_throttle, server_queue_ttl,
                    agent_queue_ttl, user_name=active_user, uri=uri,
                    method=method
                )
            )
            self.set_status(results['http_status'])
            self.set_header('Content-Type', 'application/json')
            self.write(json.dumps(results, indent=4))

        except Exception as e:
            results = (
                GenericResults(
                    active_user, uri, method
                ).something_broke(active_user, 'User', e)
            )
            logger.exception(e)
            self.set_status(results['http_status'])
            self.set_header('Content-Type', 'application/json')
            self.write(json.dumps(results, indent=4))


    @authenticated_request
    @convert_json_to_arguments
    @check_permissions(Permissions.ADMINISTRATOR)
    def delete(self):
        active_user = self.get_current_user()
        uri = self.request.uri
        method = self.request.method
        try:
            customer_names = (
                self.arguments.get(ApiArguments.CUSTOMER_NAMES)
            )

            if not isinstance(customer_names, list):
                customer_names = customer_names.split(',')

            results = (
                remove_customers(
                    customer_names,
                    active_user, uri, method
                )
            )
            self.set_status(results['http_status'])
            self.set_header('Content-Type', 'application/json')
            self.write(json.dumps(results, indent=4))

            if (results[ApiResultKeys.VFENSE_STATUS_CODE] ==
                    CustomerCodes.CustomerDeleted):

                remove_all_agents_for_customer(customer_name)
                remove_all_apps_for_customer(customer_name)

        except Exception as e:
            results = (
                GenericResults(
                    active_user, uri, method
                ).something_broke(active_user, 'User', e)
            )
            logger.exception(e)
            self.set_status(results['http_status'])
            self.set_header('Content-Type', 'application/json')
            self.write(json.dumps(results, indent=4))

