import json
import logging
import logging.config
from vFense import VFENSE_LOGGING_CONFIG

from vFense.core.api.base import BaseHandler
from vFense.core.decorators import (
    convert_json_to_arguments, authenticated_request, results_message
)

from vFense.core._constants import CommonKeys
from vFense.core.api._constants import ApiArguments, ApiValues
from vFense.core.permissions._constants import Permissions
from vFense.core.permissions.permissions import verify_permission_for_user, \
    return_results_for_permissions

from vFense.core.permissions.decorators import check_permissions
from vFense.core.operations.decorators import log_operation
from vFense.core.operations._admin_constants import AdminActions
from vFense.core.operations._constants import vFenseObjects

from vFense.core.user._db_model import UserKeys

from vFense.core.user.manager import UserManager, \
    get_properties_for_all_users, \
    remove_user, remove_users, change_password, \
    edit_user_properties, toggle_user_status

from vFense.core.user import User
from vFense.core.user.manager import UserManager
from vFense.core.view.views import add_user_to_views, \
    remove_views_from_user

from vFense.core.group.groups import add_user_to_groups, \
    remove_groups_from_user

from vFense.errorz._constants import *
from vFense.errorz.status_codes import GenericCodes
from vFense.errorz.error_messages import GenericResults

logging.config.fileConfig(VFENSE_LOGGING_CONFIG)
logger = logging.getLogger('rvapi')


class UserHandler(BaseHandler):

    @authenticated_request
    @check_permissions(Permissions.ADMINISTRATOR)
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
                user_data = UserManager(active_user).get_all_attributes()
            elif username and granted:
                user_data = UserManager(username).get_all_attributes()
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


    @authenticated_request
    @convert_json_to_arguments
    @check_permissions(Permissions.ADMINISTRATOR)
    def post(self, username):
        active_user = self.get_current_user()
        active_view = (
            UserManager(username).get_attribute(UserKeys.CurrentView)
        )
        uri = self.request.uri
        method = self.request.method
        results = None
        try:
            view_context = (
                self.arguments.get(ApiArguments.VIEW_CONTEXT, active_view)
            )
            action = self.arguments.get(ApiArguments.ACTION, ApiValues.ADD)

            ###Update Groups###
            group_ids = self.arguments.get(ApiArguments.GROUP_IDS, None)
            if group_ids and isinstance(group_ids, list):
                if action == ApiValues.ADD:
                    results = (
                        add_user_to_groups(
                            username, view_context, group_ids,
                            username, uri, method
                        )
                    )
                if action == ApiValues.DELETE:
                    results = (
                        remove_groups_from_user(
                            username, group_ids,
                            username, uri, method
                        )
                    )
            ###Update Views###
            view_names = self.arguments.get('view_names')
            if view_names and isinstance(view_names, list):
                if action == 'add':
                    results = (
                        add_user_to_views(
                            username, view_names,
                            username, uri, method
                        )
                    )

                elif action == 'delete':
                    results = (
                        remove_views_from_user(
                            username, view_names,
                            username, uri, method
                        )
                    )

            if results:
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


    @authenticated_request
    @convert_json_to_arguments
    @check_permissions(Permissions.ADMINISTRATOR)
    def put(self, username):
        active_user = self.get_current_user()
        uri = self.request.uri
        method = self.request.method
        results = None
        try:
            ###Password Changer###
            password = self.arguments.get('password', None)
            new_password = self.arguments.get('new_password', None)
            if password and new_password:
                results = (
                    change_password(
                        username, password, new_password,
                        username, uri, method
                    )
                )
            ###Update Personal Settings###
            data_dict = {
                ApiResultKeys.HTTP_METHOD: method,
                ApiResultKeys.URI: uri,
                ApiResultKeys.USERNAME: username
            }

            fullname = self.arguments.get('fullname', None)
            if fullname:
                data_dict[UserKeys.FullName] = fullname
                results = (
                    edit_user_properties(username, **data_dict)
                )

            email = self.arguments.get('email', None)
            if email:
                data_dict[UserKeys.Email] = email
                results = (
                    edit_user_properties(username, **data_dict)
                )

            current_view = self.arguments.get('current_view', None)
            if current_view:
                data_dict[UserKeys.CurrentView] = current_view
                results = (
                    edit_user_properties(username, **data_dict)
                )

            default_view = self.arguments.get('default_view', None)
            if default_view:
                data_dict[UserKeys.DefaultView] = default_view
                results = (
                    edit_user_properties(username, **data_dict)
                )

            ###Disable or Enable a User###
            enabled = self.arguments.get('enabled', None)
            if enabled:
                enabled.lower()
                if enabled == 'toggle':
                    results = (
                        toggle_user_status(username, username, uri, method)
                    )

            if results:
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


    @authenticated_request
    @check_permissions(Permissions.ADMINISTRATOR)
    def delete(self, username):
        active_user = self.get_current_user()
        uri = self.request.uri
        method = self.request.method
        try:
            results = remove_user(
                username, active_user, uri, method
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
    @check_permissions(Permissions.ADMINISTRATOR)
    def get(self):
        active_user = self.get_current_user()
        uri = self.request.uri
        method = self.request.method
        active_view = (
            UserManager(active_user).get_attribute(UserKeys.CurrentView)
        )
        view_context = self.get_argument(ApiArguments.VIEW_CONTEXT, None)
        all_views = self.get_argument(ApiArguments.ALL_VIEWS, None)
        user_name = self.get_argument(ApiArguments.USER_NAME, None)
        count = 0
        user_data = []
        try:
            granted, status_code = (
                verify_permission_for_user(
                    active_user, Permissions.ADMINISTRATOR
                )
            )
            if granted and not view_context and not all_views and not user_name:
                user_data = get_properties_for_all_users(active_view)

            elif granted and view_context and not all_views and not user_name:

                user_data = get_properties_for_all_users(view_context)

            elif granted and all_views and not view_context and not user_name:
                user_data = get_properties_for_all_users()

            elif granted and user_name and not view_context and not all_views:
                user_data = UserManager(user_name).get_all_attributes()
                if user_data:
                    user_data = [user_data]
                else:
                    user_data = []

            elif view_context and not granted or all_views and not granted:
                results = (
                    return_results_for_permissions(
                        active_user, granted, status_code,
                        Permissions.ADMINISTRATOR, uri, method
                    )
                )

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


    @authenticated_request
    @convert_json_to_arguments
    @check_permissions(Permissions.ADMINISTRATOR)
    def post(self):
        self.active_user = self.get_current_user()
        self.active_view = (
            UserManager(active_user).get_attribute(UserKeys.CurrentView)
        )
        try:
            self.uri = self.request.uri
            self.http_method = self.request.method
            self.username = self.arguments.get(ApiArguments.USERNAME)
            self.password = self.arguments.get(ApiArguments.PASSWORD)
            self.fullname = self.arguments.get(ApiArguments.FULL_NAME, None)
            self.email = self.arguments.get(ApiArguments.EMAIL, None)
            self.enabled = self.arguments.get(ApiArguments.ENABLED, True)
            self.is_global = self.arguments.get(ApiArguments.IS_GLOBAL, False)
            self.group_ids = self.arguments.get(ApiArguments.GROUP_IDS)
            self.view_context = (
                self.arguments.get(ApiArguments.VIEW_CONTEXT, active_view)
            )
            results = self.create_user()
            results[ApiResultKeys.URI] = self.uri
            results[ApiResultKeys.HTTP_METHOD] = self.http_method
            results[ApiResultKeys.USERNAME] = self.active_user
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

    @log_operation(AdminActions.CREATE_USER, vFenseObjects.USER)
    @results_message
    def create_user(self):
        user = User(
            self.username, self.password, self.fullname, self.email,
            current_view=self.view_context, default_view=self.view_context,
            enabled=self.enabled, is_global=self.is_global
        )
        manager = UserManager(user.name)
        results = manager.create(user, self.group_ids)
        return results


    @authenticated_request
    @convert_json_to_arguments
    @check_permissions(Permissions.ADMINISTRATOR)
    def delete(self):
        active_user = self.get_current_user()
        uri = self.request.uri
        method = self.request.method
        usernames = self.arguments.get(ApiArguments.USERNAMES)
        try:
            if not isinstance(usernames, list):
                usernames = usernames.split()

            if not active_user in usernames:
                results = remove_users(
                    usernames, active_user, uri, method
                )
            else:
                results = (
                    GenericResults(
                        active_user, uri, method
                    ).something_broke(active_user, 'User', 'can not delete yourself')
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


