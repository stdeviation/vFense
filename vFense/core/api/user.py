import json
import logging
import logging.config
from vFense import VFENSE_LOGGING_CONFIG

from vFense.core.api.base import BaseHandler
from vFense.core.decorators import (
    convert_json_to_arguments, authenticated_request, results_message
)

from vFense.core.api._constants import ApiArguments, ApiValues
from vFense.core.permissions._constants import Permissions
from vFense.core.permissions.permissions import (
    verify_permission_for_user, return_results_for_permissions
)

from vFense.core.permissions.decorators import check_permissions
from vFense.core.operations.decorators import log_operation
from vFense.core.operations._admin_constants import AdminActions
from vFense.core.operations._constants import vFenseObjects

from vFense.core.user._db_model import UserKeys

from vFense.core.user import User
from vFense.core.user.manager import UserManager
from vFense.core.user.search.search import RetrieveUsers

from vFense.core.results import ApiResultKeys, Results
from vFense.core.user.status_codes import (
    UserCodes, UserFailureCodes
)

logging.config.fileConfig(VFENSE_LOGGING_CONFIG)
logger = logging.getLogger('rvapi')


class UserHandler(BaseHandler):

    @authenticated_request
    @check_permissions(Permissions.ADMINISTRATOR)
    def get(self, username):
        active_user = self.get_current_user()
        is_global = UserManager(active_user).get_attribute(UserKeys.Global)
        try:
            granted, status_code = (
                verify_permission_for_user(
                    active_user, Permissions.ADMINISTRATOR
                )
            )
            if not username or username == active_user:
                results = self.get_user(active_user, is_global)

            elif username and granted:
                results = self.get_user(username, is_global)

            elif username and not granted:
                results = (
                    return_results_for_permissions(
                        active_user, granted, status_code,
                        Permissions.ADMINISTRATOR, self.request.uri,
                        self.request.method
                    )
                )

            self.set_status(results['http_status'])
            self.set_header('Content-Type', 'application/json')
            self.write(json.dumps(results, indent=4))

        except Exception as e:
            data = {
                ApiResultKeys.MESSAGE: (
                    'Retrieving user {0} broke: {1}'
                    .format(username, e)
                )
            }
            results = (
                Results(
                    active_user, self.request.uri, self.request.method
                ).something_broke(**data)
            )
            logger.exception(e)
            self.set_status(results['http_status'])
            self.set_header('Content-Type', 'application/json')
            self.write(json.dumps(results, indent=4))


    @results_message
    def get_user(self, user_name, is_global):
        fetch_users = RetrieveUsers(is_global=is_global)
        results = fetch_users.by_name(user_name)
        if results[ApiResultKeys.COUNT] > 0:
            results[ApiResultKeys.DATA] = results[ApiResultKeys.DATA][0]
        return results


    @authenticated_request
    @convert_json_to_arguments
    def post(self, username):
        active_user = self.get_current_user()
        user = UserManager(username)
        try:
            action = self.arguments.get(ApiArguments.ACTION, ApiValues.ADD)

            ###Update Groups###
            group_ids = self.arguments.get(ApiArguments.GROUP_IDS, None)
            force_remove = self.arguments.get(ApiArguments.FORCE_REMOVE, False)
            if group_ids and isinstance(group_ids, list):
                if action == ApiValues.ADD:
                    results = self.add_to_groups(user, group_ids)
                if action == ApiValues.DELETE:
                    results = (
                        self.remove_from_groups(user, group_ids, force_remove)
                    )
            ###Update Views###
            view_names = self.arguments.get('view_names')
            if view_names and isinstance(view_names, list):
                if action == 'add':
                    results = self.add_to_views(user, view_names)

                elif action == 'delete':
                    results = self.remove_from_views(user, view_names)

            if results:
                self.set_status(results['http_status'])
                self.set_header('Content-Type', 'application/json')
                self.write(json.dumps(results, indent=4))

            else:
                data = {
                    ApiResultKeys.MESSAGE: (
                        'Incorrect arguments while editing user {0}'
                        .format(username)
                    )
                }
                results = (
                    Results(
                        active_user, self.request.uri, self.request.method
                    ).incorrect_arguments(**data)
                )

                self.set_status(results['http_status'])
                self.set_header('Content-Type', 'application/json')
                self.write(json.dumps(results, indent=4))

        except Exception as e:
            data = {
                ApiResultKeys.MESSAGE: (
                    'Editing user {0} broke: {1}'
                    .format(username, e)
                )
            }
            results = (
                Results(
                    active_user, self.request.uri, self.request.method
                ).something_broke(**data)
            )
            logger.exception(e)
            self.set_status(results['http_status'])
            self.set_header('Content-Type', 'application/json')
            self.write(json.dumps(results, indent=4))

    @results_message
    @check_permissions(Permissions.ADMINISTRATOR)
    @log_operation(AdminActions.ADD_USER_TO_VIEW, vFenseObjects.USER)
    def add_to_views(self, user, views):
        results = user.add_to_views(views)
        return results

    @results_message
    @check_permissions(Permissions.ADMINISTRATOR)
    @log_operation(AdminActions.ADD_USER_TO_GROUP, vFenseObjects.USER)
    def add_to_groups(self, user, group_ids):
        results = user.add_to_groups(group_ids)
        return results

    @results_message
    @check_permissions(Permissions.ADMINISTRATOR)
    @log_operation(AdminActions.REMOVE_USER_FROM_VIEW, vFenseObjects.USER)
    def remove_from_views(self, user, views):
        results = user.remove_from_views(views)
        return results

    @results_message
    @log_operation(AdminActions.REMOVE_USER_FROM_GROUP, vFenseObjects.USER)
    @check_permissions(Permissions.ADMINISTRATOR)
    def remove_from_groups(self, user, group_ids, force):
        results = user.remove_from_groups(group_ids, force)
        return results


    @authenticated_request
    @convert_json_to_arguments
    def put(self, username):
        active_user = self.get_current_user()
        self.manager = UserManager(username)
        try:
            ###Password Changer###
            password = self.arguments.get('password', None)
            new_password = self.arguments.get('new_password', None)
            if password and new_password:
                results = (
                    self.change_password(password, new_password)
                )
            ###Update Personal Settings###
            fullname = self.arguments.get('fullname', None)
            if fullname:
                results = (
                    self.change_full_name(username, fullname)
                )

            email = self.arguments.get('email', None)
            if email:
                results = (
                    self.change_email(username, email)
                )

            current_view = self.arguments.get('current_view', None)
            if current_view:
                results = (
                    self.change_current_view(username, current_view)
                )

            default_view = self.arguments.get('default_view', None)
            if default_view:
                results = (
                    self.change_default_view(username, default_view)
                )

            ###Disable or Enable a User###
            enabled = self.arguments.get('enabled', None)
            if enabled:
                enabled.lower()
                if enabled == 'toggle':
                    results = (
                        self.toggle_status()
                    )

            if results:
                self.set_status(results['http_status'])
                self.set_header('Content-Type', 'application/json')
                self.write(json.dumps(results, indent=4))

            else:
                data = {
                    ApiResultKeys.MESSAGE: (
                        'Incorrect arguments while editing user {0}'
                        .format(username)
                    )
                }
                results = (
                    Results(
                        active_user, self.request.uri, self.request.method
                    ).incorrect_arguments(**data)
                )
                self.set_status(results['http_status'])
                self.set_header('Content-Type', 'application/json')
                self.write(json.dumps(results, indent=4))

        except Exception as e:
            data = {
                ApiResultKeys.MESSAGE: (
                    'Editing user {0} broke: {1}'
                    .format(username, e)
                )
            }
            results = (
                Results(
                    active_user, self.request.uri, self.request.method
                ).something_broke(**data)
            )
            logger.exception(e)
            self.set_status(results['http_status'])
            self.set_header('Content-Type', 'application/json')
            self.write(json.dumps(results, indent=4))

    @results_message
    @check_permissions(Permissions.ADMINISTRATOR)
    @log_operation(AdminActions.EDIT_USER_PASSWORD, vFenseObjects.USER)
    def change_password(self, orig_password, new_password):
        results = self.manager.change_password(orig_password, new_password)
        return results

    @results_message
    @check_permissions(Permissions.ADMINISTRATOR)
    @log_operation(AdminActions.RESET_USER_PASSWORD, vFenseObjects.USER)
    def reset_password(self, password):
        results = self.manager.reset_password(password)
        return results

    @results_message
    @check_permissions(Permissions.ADMINISTRATOR)
    @log_operation(AdminActions.EDIT_USER_FULL_NAME, vFenseObjects.USER)
    def change_full_name(self, username, full_name):
        results = self.manager.edit_full_name(full_name)
        return results

    @results_message
    @check_permissions(Permissions.ADMINISTRATOR)
    @log_operation(AdminActions.EDIT_USER_EMAIL, vFenseObjects.USER)
    def change_email(self, username, email):
        results = self.manager.edit_email(email)
        return results

    @results_message
    @check_permissions(Permissions.ADMINISTRATOR)
    @log_operation(AdminActions.EDIT_CURRENT_VIEW, vFenseObjects.USER)
    def change_current_view(self, username, view):
        user = User(username, current_view=view)
        results = self.manager.change_view(user)
        return results

    @results_message
    @check_permissions(Permissions.ADMINISTRATOR)
    @log_operation(AdminActions.EDIT_DEFAULT_VIEW, vFenseObjects.USER)
    def change_default_view(self, username, view):
        user = User(username, default_view=view)
        results = self.manager.change_view(user)
        return results

    @results_message
    @check_permissions(Permissions.ADMINISTRATOR)
    @log_operation(AdminActions.TOGGLE_USER_STATUS, vFenseObjects.USER)
    def toggle_status(self):
        results = self.manager.toggle_status()
        return results


    @authenticated_request
    def delete(self, username):
        active_user = self.get_current_user()
        self.manager = UserManager(username)
        try:
            results = self.remove_user()
            self.set_status(results['http_status'])
            self.set_header('Content-Type', 'application/json')
            self.write(json.dumps(results, indent=4))

        except Exception as e:
            data = {
                ApiResultKeys.MESSAGE: (
                    'Deleting user {0} broke: {1}'
                    .format(username, e)
                )
            }
            results = (
                Results(
                    active_user, self.request.uri, self.request.method
                ).something_broke(**data)
            )
            logger.exception(e)
            self.set_status(results['http_status'])
            self.set_header('Content-Type', 'application/json')
            self.write(json.dumps(results, indent=4))

    @results_message
    @check_permissions(Permissions.ADMINISTRATOR)
    @log_operation(AdminActions.REMOVE_USER, vFenseObjects.USER)
    def remove_user(self):
        results = self.manager.remove()
        return results


class UsersHandler(BaseHandler):

    @authenticated_request
    def get(self):
        active_user = self.get_current_user()
        user = UserManager(active_user)
        active_view = user.get_attribute(UserKeys.CurrentView)
        is_global = user.get_attribute(UserKeys.Global)
        results = []
        try:
            view_context = self.get_argument(ApiArguments.VIEW_CONTEXT, None)
            all_views = self.get_argument(ApiArguments.ALL_VIEWS, None)
            user_name = self.get_argument(ApiArguments.USER_NAME, None)
            count = int(self.get_argument('count', 30))
            offset = int(self.get_argument('offset', 0))
            sort = self.get_argument('sort', 'asc')
            sort_by = self.get_argument('sort_by', UserKeys.UserName)
            regex = self.get_argument('regex', None)
            granted, status_code = (
                verify_permission_for_user(
                    active_user, Permissions.ADMINISTRATOR
                )
            )
            if granted:
                if not view_context and not all_views:
                    fetch_users = (
                        RetrieveUsers(
                            active_view, count=count, offset=offset,
                            sort=sort, sort_key=sort_by,
                            is_global=is_global
                        )
                    )

                elif view_context and not all_views:
                    fetch_users = (
                        RetrieveUsers(
                            view_context, count=count, offset=offset,
                            sort=sort, sort_key=sort_by,
                            is_global=is_global
                        )
                    )

                else:
                    fetch_users = (
                        RetrieveUsers(
                            count=count, offset=offset,
                            sort=sort, sort_key=sort_by,
                            is_global=is_global
                        )
                    )

                if user_name:
                    results = (
                        self.get_user_by_name(fetch_users, user_name)
                    )

                elif regex:
                    results = (
                        self.get_all_users_by_regex(fetch_users, regex)
                    )

                else:
                    results = (
                        self.get_all_users(fetch_users)
                    )

            else:
                results = (
                    return_results_for_permissions(
                        active_user, granted, status_code,
                        Permissions.ADMINISTRATOR, self.request.uri,
                        self.request.method
                    )
                )

            self.set_status(results['http_status'])
            self.set_header('Content-Type', 'application/json')
            self.write(json.dumps(results, indent=4))

        except Exception as e:
            data = {
                ApiResultKeys.MESSAGE: (
                    'Searching for users broke: {0}'.format(e)
                )
            }
            results = (
                Results(
                    active_user, self.request.uri, self.request.method
                ).something_broke(**data)
            )
            logger.exception(e)
            self.set_status(results['http_status'])
            self.set_header('Content-Type', 'application/json')
            self.write(json.dumps(results, indent=4))

    @results_message
    @check_permissions(Permissions.ADMINISTRATOR)
    def get_all_users(self, fetch_users):
        results = fetch_users.all()
        return results

    @results_message
    @check_permissions(Permissions.ADMINISTRATOR)
    def get_all_users_by_regex(self, fetch_users, username):
        results = fetch_users.by_regex(username)
        return results

    @results_message
    @check_permissions(Permissions.ADMINISTRATOR)
    def get_user_by_name(self, fetch_users, username):
        results = fetch_users.by_name(username)
        return results

    @authenticated_request
    @convert_json_to_arguments
    def post(self):
        active_user = self.get_current_user()
        active_view = (
            UserManager(self.active_user).get_attribute(UserKeys.CurrentView)
        )
        try:
            username = self.arguments.get(ApiArguments.USER_NAME)
            password = self.arguments.get(ApiArguments.PASSWORD)
            fullname = self.arguments.get(ApiArguments.FULL_NAME, None)
            email = self.arguments.get(ApiArguments.EMAIL, None)
            enabled = self.arguments.get(ApiArguments.ENABLED, True)
            is_global = self.arguments.get(ApiArguments.IS_GLOBAL, False)
            group_ids = self.arguments.get(ApiArguments.GROUP_IDS)
            view_context = (
                self.arguments.get(ApiArguments.VIEW_CONTEXT, active_view)
            )
            if not isinstance(is_global, bool):
                if is_global == 'false':
                    is_global = False
                else:
                    is_global = True

            if not isinstance(enabled, bool):
                if enabled == 'false':
                    enabled = False
                else:
                    enabled = True

            results = (
                self.create_user(
                    self, username, password,fullname, email,
                    view_context, enabled, is_global, group_ids
                )
            )
            self.set_status(results['http_status'])
            self.set_header('Content-Type', 'application/json')
            self.write(json.dumps(results, indent=4))

        except Exception as e:
            data = {
                ApiResultKeys.MESSAGE: (
                    'Create user broke: {0}'.format(e)
                )
            }
            results = (
                Results(
                    active_user, self.request.uri, self.request.method
                ).something_broke(**data)
            )
            logger.exception(e)
            self.set_status(results['http_status'])
            self.set_header('Content-Type', 'application/json')
            self.write(json.dumps(results, indent=4))

    @results_message
    @check_permissions(Permissions.ADMINISTRATOR)
    @log_operation(AdminActions.CREATE_USER, vFenseObjects.USER)
    def create_user(self, username, password,
                    fullname, email, view_context,
                    enabled, is_global, group_ids):
        user = User(
            username, password, fullname, email,
            current_view=view_context, default_view=view_context,
            enabled=enabled, is_global=is_global
        )
        manager = UserManager(user.name)
        results = manager.create(user, group_ids)
        return results


    @authenticated_request
    @convert_json_to_arguments
    def delete(self):
        active_user = self.get_current_user()
        usernames = self.arguments.get(ApiArguments.USER_NAMES)
        try:
            if not isinstance(usernames, list):
                usernames = usernames.split()

            if not active_user in usernames:
                results = self.remove_users(usernames)
            else:
                data = {
                    ApiResultKeys.MESSAGE: (
                        'Can not delete yourself {0}'
                        .format(active_user)
                    )
                }
                results = (
                    Results(
                        active_user, self.request.uri, self.request.method
                    ).invalid_id(**data)
                )
            self.set_status(results['http_status'])
            self.set_header('Content-Type', 'application/json')
            self.write(json.dumps(results, indent=4))

        except Exception as e:
            data = {
                ApiResultKeys.MESSAGE: (
                    'Deleting of users broke: {0}'.format(e)
                )
            }
            results = (
                Results(
                    active_user, self.request.uri, self.request.method
                ).something_broke(**data)
            )
            logger.exception(e)
            self.set_status(results['http_status'])
            self.set_header('Content-Type', 'application/json')
            self.write(json.dumps(results, indent=4))


    @results_message
    @check_permissions(Permissions.ADMINISTRATOR)
    @log_operation(AdminActions.REMOVE_USERS, vFenseObjects.USER)
    def remove_users(self, usernames, force=False):
        end_results = {}
        users_deleted = []
        users_unchanged = []
        for username in usernames:
            manager = UserManager(username)
            results = manager.remove()
            if (results[ApiResultKeys.VFENSE_STATUS_CODE]
                    == UserCodes.Deleted):
                users_deleted.append(username)
            else:
                users_unchanged.append(username)

        end_results[ApiResultKeys.UNCHANGED_IDS] = users_unchanged
        end_results[ApiResultKeys.DELETED_IDS] = users_deleted
        if users_unchanged and users_deleted:
            msg = (
                'user names deleted: %s, user names unchanged: %s'
                % (', '.join(users_deleted), ', '.join(users_unchanged))
            )
            end_results[ApiResultKeys.GENERIC_STATUS_CODE] = (
                UserFailureCodes.FailedToDeleteAllObjects
            )
            end_results[ApiResultKeys.VFENSE_STATUS_CODE] = (
                UserFailureCodes.FailedToDeleteAllUsers
            )
            end_results[ApiResultKeys.MESSAGE] = msg

        elif users_deleted and not users_unchanged:
            msg = 'user names deleted: %s' % (', '.join(users_deleted))
            end_results[ApiResultKeys.GENERIC_STATUS_CODE] = (
                UserCodes.ObjectsDeleted
            )
            end_results[ApiResultKeys.VFENSE_STATUS_CODE] = (
                UserCodes.UsersDeleted
            )
            end_results[ApiResultKeys.MESSAGE] = msg

        elif users_unchanged and not users_deleted:
            msg = 'user names unchanged: %s' % (', '.join(users_unchanged))
            end_results[ApiResultKeys.GENERIC_STATUS_CODE] = (
                UserCodes.ObjectsUnchanged
            )
            end_results[ApiResultKeys.VFENSE_STATUS_CODE] = (
                UserCodes.UsersUnchanged
            )
            end_results[ApiResultKeys.MESSAGE] = msg

        return end_results
