import re
import json
import logging
import logging.config
from vFense import VFENSE_LOGGING_CONFIG

from vFense.core.api.base import BaseHandler

from vFense.core.api._constants import ApiArguments, ApiValues
from vFense.core._constants import DefaultQueryValues
from vFense.core.permissions._constants import Permissions
from vFense.core.permissions.permissions import (
    verify_permission_for_user, return_results_for_permissions
)

from vFense.core.permissions.decorators import check_permissions
from vFense.core.operations.decorators import log_operation
from vFense.core.operations._admin_constants import AdminActions
from vFense.core.operations._constants import vFenseObjects

from vFense.core.decorators import (
    convert_json_to_arguments, authenticated_request, results_message,
    catch_it
)

from vFense.core.user._db_model import UserKeys
from vFense.core.user.manager import UserManager

from vFense.core.group import Group
from vFense.core.group._db_model import GroupKeys
from vFense.core.group.manager import GroupManager
from vFense.core.group.search.search import RetrieveGroups

from vFense.core.results import ApiResults, ExternalApiResults
from vFense.core.group.status_codes import (
    GroupCodes, GroupFailureCodes
)

logging.config.fileConfig(VFENSE_LOGGING_CONFIG)
logger = logging.getLogger('rvapi')


class GroupHandler(BaseHandler):
    @catch_it
    @authenticated_request
    def get(self, group_id):
        active_user = self.get_current_user()
        is_global = UserManager(active_user).get_attribute(UserKeys.IsGlobal)
        output = self.get_argument(ApiArguments.OUTPUT, 'json')
        results = self.get_group(group_id, is_global)
        self.set_status(results.http_status_code)
        self.modified_output(results, output, 'group')


    @results_message
    @check_permissions(Permissions.ADMINISTRATOR)
    def get_group(self, group_id, is_global):
        fetch_groups = RetrieveGroups(is_global=is_global)
        results = fetch_groups.by_id(group_id)
        if results.count > 0:
            results.data = results.data[0]
        return results

    @catch_it
    @authenticated_request
    @convert_json_to_arguments
    def post(self, group_id):
        results = None
        active_user = self.get_current_user()
        group = GroupManager(group_id)
        action = self.arguments.get(ApiArguments.ACTION)
        force = self.arguments.get(ApiArguments.FORCE_REMOVE, False)
        ###Users###
        usernames = self.arguments.get(ApiArguments.USER_NAMES, [])
        if usernames and isinstance(usernames, list):
            if action == ApiValues.ADD:
                results = self.add_users(group, usernames)

            if action == ApiValues.DELETE:
                results = self.remove_users(group, usernames, force)

        ###Views###
        views = self.arguments.get(ApiArguments.VIEW_NAMES, [])
        if views and isinstance(views, list):
            if action == ApiValues.ADD:
                results = self.add_views(group, views)

            if action == ApiValues.DELETE:
                results = self.remove_views(group, views, force)

        ###Permissions###
        permissions = self.arguments.get(ApiArguments.VIEW_NAMES, [])
        if views and isinstance(views, list):
            if action == ApiValues.ADD:
                results = self.add_permissions(group, permissions)

            if action == ApiValues.DELETE:
                results = self.remove_permissions(group, permissions)


        if results:
            self.set_status(results.http_status_code)
            self.set_header('Content-Type', 'application/json')
            self.write(json.dumps(results.to_dict_non_null(), indent=4))

        else:
            results = ExternalApiResults()
            results.fill_in_defaults()
            results.generic_status_code = GroupCodes.IncorrectArguments
            results.vfense_status_code = GroupCodes.IncorrectArguments
            results.message = 'Incorrect arguments:'
            results.uri = self.request.uri
            results.http_method = self.request.method
            results.username = active_user
            results.http_status_code = 400
            self.set_status(results.http_status_code)
            self.set_header('Content-Type', 'application/json')
            self.write(json.dumps(results.to_dict_non_null(), indent=4))


    @results_message
    @check_permissions(Permissions.ADMINISTRATOR)
    @log_operation(AdminActions.ADD_VIEWS_TO_GROUP, vFenseObjects.GROUP)
    def add_views(self, group, views):
        results = group.add_views(views)
        return results

    @results_message
    @check_permissions(Permissions.ADMINISTRATOR)
    @log_operation(AdminActions.ADD_USERS_TO_GROUP, vFenseObjects.GROUP)
    def add_users(self, group, users):
        results = group.add_users(users)
        return results

    @results_message
    @check_permissions(Permissions.ADMINISTRATOR)
    @log_operation(AdminActions.ADD_PERMISSIONS_TO_GROUP, vFenseObjects.GROUP)
    def add_permissions(self, group, permissions):
        results = group.add_permissions(permissions)
        return results

    @results_message
    @check_permissions(Permissions.ADMINISTRATOR)
    @log_operation(AdminActions.REMOVE_VIEWS_FROM_GROUP, vFenseObjects.GROUP)
    def remove_views(self, group, views, force):
        results = group.remove_views(views, force)
        return results

    @results_message
    @check_permissions(Permissions.ADMINISTRATOR)
    @log_operation(AdminActions.REMOVE_USERS_FROM_GROUP, vFenseObjects.GROUP)
    def remove_users(self, group, users, force):
        results = group.remove_users(users, force)
        return results

    @results_message
    @check_permissions(Permissions.ADMINISTRATOR)
    @log_operation(AdminActions.REMOVE_PERMISSIONS_FROM_GROUP, vFenseObjects.GROUP)
    def remove_permissions(self, group, permissions):
        results = group.remove_permissions(permissions)
        return results

    @catch_it
    @authenticated_request
    @convert_json_to_arguments
    def delete(self, group_id):
        manager = GroupManager(group_id)
        ###Remove GroupId###
        results = self.remove_group(manager)

        self.set_status(results.http_status_code)
        self.set_header('Content-Type', 'application/json')
        self.write(json.dumps(results.to_dict_non_null(), indent=4))

    @results_message
    @check_permissions(Permissions.ADMINISTRATOR)
    @log_operation(AdminActions.REMOVE_GROUP, vFenseObjects.GROUP)
    def remove_group(self, manager):
        results = manager.remove()
        return results


class GroupsHandler(BaseHandler):
    @catch_it
    @authenticated_request
    def get(self):
        active_user = self.get_current_user()
        user = UserManager(active_user)
        active_view = user.get_attribute(UserKeys.CurrentView)
        is_global = user.get_attribute(UserKeys.IsGlobal)
        view_context = self.get_argument(ApiArguments.VIEW_CONTEXT, None)
        group_id = self.get_argument(ApiArguments.GROUP_ID, None)
        all_views = self.get_argument(ApiArguments.ALL_VIEWS, None)
        count = int(
            self.get_argument(ApiArguments.COUNT, DefaultQueryValues.COUNT)
        )
        offset = int(
            self.get_argument(ApiArguments.OFFSET, DefaultQueryValues.OFFSET)
        )
        sort = (
            self.get_argument(ApiArguments.SORT, DefaultQueryValues.SORT)
        )
        sort_by = (
            self.get_argument(ApiArguments.SORT_BY, GroupKeys.GroupName)
        )
        regex = self.get_argument(ApiArguments.QUERY, None)
        output = self.get_argument(ApiArguments.OUTPUT, 'json')
        granted, status_code = (
            verify_permission_for_user(
                active_user, Permissions.ADMINISTRATOR, view_context
            )
        )
        if granted:
            if not view_context and not all_views and not group_id:
                fetch_groups = (
                    RetrieveGroups(
                        active_view, count=count, offset=offset, sort=sort,
                        sort_key=sort_by, is_global=is_global
                    )
                )

            elif view_context and not all_views and not group_id:
                fetch_groups = (
                    RetrieveGroups(
                        view_context, count=count, offset=offset, sort=sort,
                        sort_key=sort_by, is_global=is_global
                    )
                )

            else:
                fetch_groups = (
                    RetrieveGroups(
                        view_context, count=count, offset=offset, sort=sort,
                        sort_key=sort_by, is_global=is_global
                        )
                    )

            if group_id:
                results = self.get_group_by_id(fetch_groups, group_id)

            elif regex:
                results = (
                    self.get_all_groups_by_regex(fetch_groups, regex)
                )

            else:
                results = self.get_all_groups(fetch_groups)

        else:
            results = (
                return_results_for_permissions(
                    active_user, granted, status_code,
                    Permissions.ADMINISTRATOR, self.request.uri,
                    self.request.method
                )
            )

        self.set_status(results.http_status_code)
        self.modified_output(results, output, 'groups')

    @results_message
    @check_permissions(Permissions.ADMINISTRATOR)
    def get_all_groups(self, fetch_groups):
        results = fetch_groups.all()
        return results

    @results_message
    @check_permissions(Permissions.ADMINISTRATOR)
    def get_all_groups_by_regex(self, fetch_groups, regex):
        results = fetch_groups.by_regex(regex)
        return results

    @results_message
    @check_permissions(Permissions.ADMINISTRATOR)
    def get_group_by_id(self, fetch_groups, group_id):
        results = fetch_groups.by_id(group_id)
        return results

    @catch_it
    @authenticated_request
    @convert_json_to_arguments
    def post(self):
        active_user = self.get_current_user()
        results = None
        user = UserManager(active_user)
        active_view = (
            user.get_attribute(UserKeys.CurrentView)
        )
        invalid_value = False
        ###Create Group###
        group_name = self.arguments.get(ApiArguments.GROUP_NAME)
        permissions = self.arguments.get(ApiArguments.PERMISSIONS)
        is_global = self.arguments.get(ApiArguments.IS_GLOBAL, False)
        if is_global and not isinstance(self.is_global, bool):
            if re.search('true', self._is_global, re.IGNORECASE):
                is_global = True
            elif re.search('false', is_global, re.IGNORECASE):
                is_global = False
            else:
                invalid_value = True
        views = self.arguments.get(ApiArguments.VIEW_NAMES, [])
        views.append(active_view)
        views = list(set(self.views))
        group = Group(group_name, permissions, views, is_global)
        if not invalid_value:
            results = self.create_group(group)
        else:
            results = ExternalApiResults()
            results.fill_in_defaults()
            results.generic_status_code = GroupCodes.IncorrectArguments
            results.vfense_status_code = GroupCodes.IncorrectArguments
            results.message = 'Incorrect arguments:'
            results.uri = self.request.uri
            results.http_method = self.request.method
            results.username = active_user
            results.http_status_code = 400
            self.set_status(results.http_status_code)
            self.set_header('Content-Type', 'application/json')
            self.write(json.dumps(results.to_dict_non_null(), indent=4))

    @results_message
    @check_permissions(Permissions.ADMINISTRATOR)
    @log_operation(AdminActions.CREATE_GROUP, vFenseObjects.GROUP)
    def create_group(self, group):
        manager = GroupManager()
        results = manager.create(group)
        return results

    @catch_it
    @authenticated_request
    @convert_json_to_arguments
    def delete(self):
        ###Remove GroupId###
        group_ids = self.arguments.get(ApiArguments.GROUP_IDS)
        force = self.arguments.get(ApiArguments.FORCE_REMOVE, False)
        results = self.remove_groups(group_ids, force)

        self.set_status(results.http_status_code)
        self.set_header('Content-Type', 'application/json')
        self.write(json.dumps(results.to_dict_non_null(), indent=4))


    @results_message
    @check_permissions(Permissions.ADMINISTRATOR)
    @log_operation(AdminActions.REMOVE_GROUPS, vFenseObjects.GROUP)
    def remove_groups(self, group_ids, force=False):
        end_results = ApiResults()
        end_results.fill_in_defaults()
        groups_deleted = []
        groups_unchanged = []
        for group_id in group_ids:
            manager = GroupManager(group_id)
            results = manager.remove()
            if (results.vfense_status_code
                        == GroupCodes.Deleted):
                groups_deleted.append(group_id)
            else:
                groups_unchanged.append(group_id)

        end_results.unchanged_ids = groups_unchanged
        end_results.deleted_ids = groups_deleted
        if groups_unchanged and groups_deleted:
            msg = (
                'group ids deleted: %s, group ids unchanged: %s'
                % (', '.join(groups_deleted), ', '.join(groups_unchanged))
            )
            end_results.generic_status_code = (
                GroupFailureCodes.FailedToDeleteAllObjects
            )
            end_results.vfense_status_code = (
                GroupFailureCodes.FailedToDeleteAllGroups
            )
            end_results.message = msg

        elif groups_deleted and not groups_unchanged:
            msg = 'group ids deleted: %s' % (', '.join(groups_deleted))
            end_results.generic_status_code = (
                GroupCodes.ObjectsDeleted
            )
            end_results.vfense_status_code = (
                GroupCodes.GroupsDeleted
            )
            end_results.message = msg

        elif groups_unchanged and not groups_deleted:
            msg = 'group ids unchanged: %s' % (', '.join(groups_unchanged))
            end_results.generic_status_code = (
                GroupCodes.ObjectsUnchanged
            )
            end_results.vfense_status_code = (
                GroupCodes.GroupsUnchanged
            )
            end_results.message = msg

        return end_results
