import json
import logging
import logging.config

from vFense.utils.security import check_password
from vFense.server.handlers import BaseHandler
from vFense.server.hierarchy.decorators import authenticated_request

from vFense.core.permissions._constants import *
from vFense.core.permissions.permissions import verify_permission_for_user, \
    return_results_for_permissions
from vFense.core.permissions.decorators import check_permissions
from vFense.core.agent import *
from vFense.core.user import *
from vFense.core.user.users import get_user_property, \
    get_user_properties, get_properties_for_all_users
from vFense.errorz.error_messages import GenericResults

logging.config.fileConfig('/opt/TopPatch/conf/logging.config')
logger = logging.getLogger('rvapi')


class UserHandler(BaseHandler):

    @authenticated_request
    def get(self, username):
        active_user = self.get_current_user()
        uri = self.request.uri
        method = self.request.method
        count = 0
        user_data = {}
        try:
            granted, status_code = (
                verify_permission_for_user(
                    active_user, Permissions.ADMINISTRATOR
                )
            )
            if not username or username == active_user:
                user_data = get_user_properties(active_user)
            elif username and granted:
                user_data = get_user_properties(username)
            elif username and not granted:
                results = (
                    return_results_for_permissions(
                        active_user, granted, status_code,
                        Permissions.ADMINISTRATOR, uri, method
                    )
                )

            if user_data:
                count = 1
                results = (
                    GenericResults(
                        active_user, uri, method
                    ).information_retrieved(user_data, count)
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


class UsersHandler(BaseHandler):

    @authenticated_request
    def get(self):
        active_user = self.get_current_user()
        uri = self.request.uri
        method = self.request.method
        active_customer = (
            get_user_property(active_user, UserKeys.CurrentCustomer)
        )
        customer_name = self.get_argument('customer_name', None)
        all_customers = self.get_argument('all_customers', None)
        count = 0
        user_data = {}
        try:
            granted, status_code = (
                verify_permission_for_user(
                    active_user, Permissions.ADMINISTRATOR
                )
            )
            if not customer_name and not all_customers:
                user_data = get_properties_for_all_users(active_customer)

            elif customer_name and granted and not all_customers:
                user_data = get_properties_for_all_users(customer_name)

            elif not customer_name and granted and all_customers:
                user_data = get_properties_for_all_users()

            elif customer_name and not granted or all_customers and not granted:
                results = (
                    return_results_for_permissions(
                        active_user, granted, status_code,
                        Permissions.ADMINISTRATOR, uri, method
                    )
                )

            if user_data:
                count = len(user_data)
                results = (
                    GenericResults(
                        active_user, uri, method
                    ).information_retrieved(user_data, count)
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


