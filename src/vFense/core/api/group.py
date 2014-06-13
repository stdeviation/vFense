import json
import logging
import logging.config
from vFense import VFENSE_LOGGING_CONFIG

from vFense.core.api.base import BaseHandler

from vFense.core.api._constants import ApiArguments, ApiValues
from vFense.core.permissions._constants import *
from vFense.core.permissions.permissions import verify_permission_for_user, \
    return_results_for_permissions

from vFense.core.permissions.decorators import check_permissions
from vFense.core.operations.decorators import log_operation
from vFense.core.operations._admin_constants import AdminActions
from vFense.core.operations._constants import vFenseObjects

from vFense.core.decorators import (
    convert_json_to_arguments, authenticated_request, results_message
)

from vFense.core.agent import *
from vFense.core.user._db_model import UserKeys
from vFense.core.user.manager import UserManager

from vFense.core.group import Group
from vFense.core.group.manager import GroupManager
from vFense.core.group.search import RetrieveGroups

from vFense.errorz.error_messages import GenericResults

logging.config.fileConfig(VFENSE_LOGGING_CONFIG)
logger = logging.getLogger('rvapi')


class GroupHandler(BaseHandler):

    @authenticated_request
    @check_permissions(Permissions.ADMINISTRATOR)
    def get(self, group_id):
        active_user = self.get_current_user()
        uri = self.request.uri
        http_method = self.request.method
        is_global = UserManager(active_user).get_attribute(UserKeys.Global)
        try:
            results = self.get_group(group_id, is_global)
            self.set_status(results['http_status'])
            self.set_header('Content-Type', 'application/json')
            self.write(json.dumps(results, indent=4))

        except Exception as e:
            results = (
                GenericResults(
                    active_user, uri, http_method
                ).something_broke(active_user, 'Group', e)
            )
            logger.exception(e)
            self.set_status(results['http_status'])
            self.set_header('Content-Type', 'application/json')
            self.write(json.dumps(results, indent=4))

        @results_message
        def get_group(self, group_id, is_global):
            fetch_groups = RetrieveGroups(is_global=is_global)
            results = fetch_groups.by_id(group_id)

            return results

    @authenticated_request
    @convert_json_to_arguments
    @check_permissions(Permissions.ADMINISTRATOR)
    def post(self, group_id):
        active_user = self.get_current_user()
        uri = self.request.uri
        http_method = self.request.method
        self.group = GroupManager(group_id)
        try:
            action = self.arguments.get(ApiArguments.ACTION)
            force = self.arguments.get(ApiArguments.FORCE_REMOVE, False)
            ###Add Users###
            usernames = self.arguments.get(ApiArguments.USERNAMES, [])
            if usernames and isinstance(usernames, list):
                if action == ApiValues.ADD:
                    results = self.add_users(usernames)

                if action == ApiValues.DELETE:
                    results = self.remove_users(usernames, force)

            ###Add Views###
            views = self.arguments.get(ApiArguments.VIEW_NAMES, [])
            if views and isinstance(views, list):
                if action == ApiValues.ADD:
                    results = self.add_views(views)

                if action == ApiValues.DELETE:
                    results = self.remove_views(views, force)

            if results:
                self.set_status(results['http_status'])
                self.set_header('Content-Type', 'application/json')
                self.write(json.dumps(results, indent=4))

            else:
                results = (
                    GenericResults(
                        active_user, uri, http_method
                    ).incorrect_arguments()
                )

                self.set_status(results['http_status'])
                self.set_header('Content-Type', 'application/json')
                self.write(json.dumps(results, indent=4))

        except Exception as e:
            results = (
                GenericResults(
                    active_user, uri, http_method
                ).something_broke(active_user, 'User', e)
            )
            logger.exception(e)
            self.set_status(results['http_status'])
            self.set_header('Content-Type', 'application/json')
            self.write(json.dumps(results, indent=4))

        @results_message
        def add_views(self, views):
            results = self.group.add_views(views)
            return results

        @results_message
        def add_users(self, users):
            results = self.group.add_users(users)
            return results

        @log_operation(AdminActions.REMOVE_VIEWS_FROM_GROUP, vFenseObjects.GROUP)
        @results_message
        def remove_views(self, views, force):
            results = self.group.remove_views(views, force)
            return results

        @log_operation(AdminActions.REMOVE_USERS_FROM_GROUP, vFenseObjects.GROUP)
        @results_message
        def remove_users(self, users, force):
            results = self.group.remove_users(users, force)
            return results


    @authenticated_request
    @convert_json_to_arguments
    @check_permissions(Permissions.ADMINISTRATOR)
    def delete(self, group_id):
        active_user = self.get_current_user()
        uri = self.request.uri
        http_method = self.request.method
        self.manager = GroupManager(group_id)
        try:
            ###Remove GroupId###
            results = (
                remove_group(
                    group_id, active_user, uri, method
                )
            )

            self.set_status(results['http_status'])
            self.set_header('Content-Type', 'application/json')
            self.write(json.dumps(results, indent=4))

        except Exception as e:
            results = (
                GenericResults(
                    active_user, uri, http_method
                ).something_broke(active_user, 'User', e)
            )
            logger.exception(e)
            self.set_status(results['http_status'])
            self.set_header('Content-Type', 'application/json')
            self.write(json.dumps(results, indent=4))

        @log_operation(AdminActions.REMOVE_GROUP, vFenseObjects.GROUP)
        @results_message
        def remove_user(self):
            results = self.manager.remove()
            return results


class GroupsHandler(BaseHandler):

    @authenticated_request
    @check_permissions(Permissions.ADMINISTRATOR)
    def get(self):
        active_user = self.get_current_user()
        uri = self.request.uri
        method = self.request.method
        active_view = (
            UserManager(active_user).get_attribute(UserKeys.CurrentView)
        )
        view_context = self.get_argument('view_context', None)
        group_id = self.get_argument('group_id', None)
        all_views = self.get_argument('all_views', None)
        count = 0
        group_data = {}
        try:
            granted, status_code = (
                verify_permission_for_user(
                    active_user, Permissions.ADMINISTRATOR, view_context
                )
            )
            if granted and not view_context and not all_views and not group_id:
                group_data = get_properties_for_all_groups(active_view)

            elif granted and view_context and not all_views and not group_id:
                group_data = get_properties_for_all_groups(view_context)

            elif granted and all_views and not view_context and not group_id:
                group_data = get_properties_for_all_groups()

            elif granted and group_id and not view_context and not all_views:
                group_data = get_group_properties(group_id)
                if group_data:
                    group_data = [group_data]
                else:
                    group_data = []

            elif view_context and not granted or all_views and not granted:
                results = (
                    return_results_for_permissions(
                        active_user, granted, status_code,
                        Permissions.ADMINISTRATOR, uri, method
                    )
                )

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


    @authenticated_request
    @convert_json_to_arguments
    @check_permissions(Permissions.ADMINISTRATOR)
    def post(self):
        active_user = self.get_current_user()
        uri = self.request.uri
        method = self.request.method
        results = None
        active_view = (
            UserManager(active_user).get_attribute(UserKeys.CurrentView)
        )
        try:
            ###Create Group###
            group_name = self.arguments.get(ApiArguments.GROUP_NAME)
            permissions = self.arguments.get(ApiArguments.PERMISSIONS)
            view_context = (
                    self.arguments.get(
                        ApiArguments.CUSTOMER_CONTEXT,
                        active_view
                    )
            )
            results = (
                create_group(
                    group_name, view_context, permissions,
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
        results = None
        try:
            ###Remove GroupId###
            group_ids = self.arguments.get(ApiArguments.GROUP_IDS)
            results = (
                remove_groups(
                    group_ids, active_user, uri, method
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
