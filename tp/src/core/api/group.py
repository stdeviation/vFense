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
from vFense.core.user.users import get_user_property
from vFense.core.group.groups import get_group_properties, \
    get_properties_for_all_groups
from vFense.errorz.error_messages import GenericResults

logging.config.fileConfig('/opt/TopPatch/conf/logging.config')
logger = logging.getLogger('rvapi')


class GroupHandler(BaseHandler):

    @authenticated_request
    @check_permissions(Permissions.ADMINISTRATOR)
    def get(self, group_id):
        active_user = self.get_current_user()
        uri = self.request.uri
        method = self.request.method
        count = 0
        group_data = {}
        try:
            group_data = get_group_properties(group_id)
            if group_data:
                count = 1
                results = (
                    GenericResults(
                        active_user, uri, method
                    ).information_retrieved(group_data, count)
                ) 
            self.set_status(results['http_status'])
            self.set_header('Content-Type', 'application/json')
            self.write(json.dumps(results, indent=4))

        except Exception as e:
            results = (
                GenericResults(
                    active_user, uri, method
                ).something_broke(active_user, 'Group', e)
            )
            logger.exception(e)
            self.set_status(results['http_status'])
            self.set_header('Content-Type', 'application/json')
            self.write(json.dumps(results, indent=4))


class GroupsHandler(BaseHandler):

    @authenticated_request
    @check_permissions(Permissions.ADMINISTRATOR)
    def get(self):
        active_user = self.get_current_user()
        uri = self.request.uri
        method = self.request.method
        active_customer = (
            get_user_property(active_user, UserKeys.CurrentCustomer)
        )
        customer_context = self.get_argument('customer_context', None)
        group_id = self.get_argument('group_id', None)
        all_customers = self.get_argument('all_customers', None)
        count = 0
        group_data = {}
        try:
            granted, status_code = (
                verify_permission_for_user(
                    active_user, Permissions.ADMINISTRATOR, customer_context
                )
            )
            if granted and not customer_context and not all_customers and not group_id:
                group_data = get_properties_for_all_groups(active_customer)

            elif granted and customer_context and not all_customers and not group_id:
                group_data = get_properties_for_all_groups(customer_name)

            elif granted and all_customers and not customer_context and not group_id:
                group_data = get_properties_for_all_groups()

            elif granted and group_id and not customer_context and not all_customers:
                group_data = get_group_properties(group_id)
                if group_data:
                    group_data = [group_data]
                else:
                    group_data = []

            elif customer_context and not granted or all_customers and not granted:
                results = (
                    return_results_for_permissions(
                        active_user, granted, status_code,
                        Permissions.ADMINISTRATOR, uri, method
                    )
                )

            if group_data:
                count = len(group_data)
                results = (
                    GenericResults(
                        active_user, uri, method
                    ).information_retrieved(group_data, count)
                ) 
            self.set_status(results['http_status'])
            self.set_header('Content-Type', 'application/json')
            self.write(json.dumps(results, indent=4))


        except Exception as e:
            results = (
                GenericResults(
                    active_user, uri, method
                ).something_broke(active_user, 'Group', e)
            )
            logger.exception(e)
            self.set_status(results['http_status'])
            self.set_header('Content-Type', 'application/json')
            self.write(json.dumps(results, indent=4))
