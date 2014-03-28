import json
import logging
import logging.config

from vFense.server.handlers import BaseHandler
from vFense.server.hierarchy.decorators import authenticated_request

from vFense.core.permissions._constants import *
from vFense.core.permissions.permissions import verify_permission_for_user, \
    return_results_for_permissions
from vFense.core.permissions.decorators import check_permissions
from vFense.core.agent import *
from vFense.core.user import *
from vFense.core.customer import *
from vFense.core.customer.customers import get_properties_for_customer, \
    get_properties_for_all_customers
from vFense.errorz.error_messages import GenericResults

logging.config.fileConfig('/opt/TopPatch/conf/logging.config')
logger = logging.getLogger('rvapi')


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


class CustomersHandler(BaseHandler):

    @authenticated_request
    @check_permissions(Permissions.ADMINISTRATOR)
    def get(self):
        active_user = self.get_current_user()
        uri = self.request.uri
        method = self.request.method
        all_customers = self.get_argument('all_customers', None)
        customer_context = self.get_argument('customer_context', None)
        count = 0
        customer_data = {}
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


