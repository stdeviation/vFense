import re
import json
import logging
import logging.config
from vFense import VFENSE_LOGGING_CONFIG

from vFense.core.api.base import BaseHandler

from vFense.core.api._constants import ApiArguments, ApiValues
from vFense.core.permissions._constants import Permissions
from vFense.core.permissions.permissions import (
    verify_permission_for_user, return_results_for_permissions
)

from vFense.core.permissions.decorators import check_permissions
from vFense.core.operations.decorators import log_operation
from vFense.core.operations._admin_constants import AdminActions
from vFense.core.operations._constants import vFenseObjects

from vFense.core.decorators import (
    convert_json_to_arguments, authenticated_request, results_message
)

from vFense.core.user._db_model import UserKeys
from vFense.core.user.manager import UserManager

from vFense.core.group import Group
from vFense.core.group._db_model import GroupKeys
from vFense.core.group.manager import GroupManager
from vFense.core.group.search.search import RetrieveGroups

from vFense.errorz._constants import ApiResultKeys
from vFense.errorz.error_messages import GenericResults
from vFense.errorz.results import Results
from vFense.errorz.status_codes import (
    GenericCodes, GenericFailureCodes, GroupCodes, GroupFailureCodes
)

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
            results = self.remove_group()

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
        def remove_group(self):
            results = self.manager.remove()
            return results


class GroupsHandler(BaseHandler):

    @authenticated_request
    @check_permissions(Permissions.ADMINISTRATOR)
    def get(self):
        active_user = self.get_current_user()
        uri = self.request.uri
        http_method = self.request.method
        user = UserManager(active_user)
        active_view = user.get_attribute(UserKeys.CurrentView)
        self.is_global = user.get_attribute(UserKeys.Global)
        view_context = self.get_argument('view_context', None)
        group_id = self.get_argument('group_id', None)
        all_views = self.get_argument('all_views', None)
        count = 0
        self.count = int(self.get_argument('count', 30))
        self.offset = int(self.get_argument('offset', 0))
        self.sort = self.get_argument('sort', 'asc')
        self.sort_by = self.get_argument('sort_by', GroupKeys.GroupName)
        group_data = []
        try:
            granted, status_code = (
                verify_permission_for_user(
                    active_user, Permissions.ADMINISTRATOR, view_context
                )
            )
            if granted and not view_context and not all_views and not group_id:
                group_data = self.get_groups(active_view)

            elif granted and view_context and not all_views and not group_id:
                group_data = self.get_groups(view_context)

            elif granted and all_views and not view_context and not group_id:
                group_data = self.get_groups()

            elif granted and group_id and not view_context and not all_views:
                group_data = self.get_groups(group_id=group_id)
                if group_data:
                    group_data = [group_data]
                else:
                    group_data = []

            elif view_context and not granted or all_views and not granted:
                results = (
                    return_results_for_permissions(
                        active_user, granted, status_code,
                        Permissions.ADMINISTRATOR, uri, http_method
                    )
                )

            count = len(group_data)
            results = (
                GenericResults(
                    active_user, uri, http_method
                ).information_retrieved(group_data, count)
            )
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
        def get_groups(self, view=None, group_id=None):
            if view:
                fetch_groups = (
                    RetrieveGroups(
                        view, count=self.count, offset=self.offset,
                        sort=self.sort, sort_key=self.sort_by,
                        is_global=self.is_global
                    )
                )

            else:
                fetch_groups = (
                    RetrieveGroups(
                        count=self.count, offset=self.offset, sort=self.sort,
                        sort_key=self.sort_by, is_global=self.is_global
                    )
                )

            if not group_id:
                results = fetch_groups.all()

            else:
                results = fetch_groups.by_id(group_id)

            return results


    @authenticated_request
    @convert_json_to_arguments
    @check_permissions(Permissions.ADMINISTRATOR)
    def post(self):
        active_user = self.get_current_user()
        uri = self.request.uri
        http_method = self.request.method
        results = None
        user = UserManager(active_user)
        active_view = (
            user.get_attribute(UserKeys.CurrentView)
        )
        invalid_value = False
        try:
            ###Create Group###
            self.group_name = self.arguments.get(ApiArguments.GROUP_NAME)
            self.permissions = self.arguments.get(ApiArguments.PERMISSIONS)
            self.is_global = self.arguments.get(ApiArguments.IS_GLOBAL, False)
            if self.is_global and not isinstance(self.is_global, bool):
                if re.search('true', self._is_global, re.IGNORECASE):
                    self.is_global = True
                elif re.search('false', self._is_global, re.IGNORECASE):
                    self.is_global = False
                else:
                    invalid_value = True
            self.views = self.arguments.get(ApiArguments.VIEW_NAMES, [])
            self.views.append(active_view)
            self.views = list(set(self.views))
            if not invalid_value:
                results = self.create_group()
            else:
                msg = {
                    ApiResultKeys.MESSAGE: (
                        'Invalid value for argument is_global: %s' %
                        (self.is_global)
                    )
                }

                results = (
                    Results(
                        active_user, uri, http_method
                    ).objects_failed_to_create(msg)
                )

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


        @log_operation(AdminActions.CREATE_GROUP, vFenseObjects.GROUP)
        @results_message
        def create_group(self):
            group = Group(
                self.group_name, self.permissions, self.views, self.is_global
            )
            manager = GroupManager()
            results = manager.create(group)
            return results

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
            force = self.arguments.get(ApiArguments.FORCE_REMOVE, False)
            results = self.remove_groups(group_ids, force)

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

        @log_operation(AdminActions.REMOVE_GROUPS, vFenseObjects.GROUP)
        @results_message
        def remove_groups(self, group_ids, force=False):
            end_results = {}
            groups_deleted = []
            groups_unchanged = []
            for group_id in group_ids:
                manager = GroupManager(group_id)
                results = manager.remove()
                if (results[ApiResultKeys.VFENSE_STATUS_CODE]
                        == GroupCodes.Deleted):
                    groups_deleted.append(group_id)
                else:
                    groups_unchanged.append(group_id)

            end_results[ApiResultKeys.UNCHANGED_IDS] = groups_unchanged
            end_results[ApiResultKeys.DELETED_IDS] = groups_deleted
            if groups_unchanged and groups_deleted:
                msg = (
                    'group ids deleted: %s, group ids unchanged: %s'
                    % (', '.join(groups_deleted), ', '.join(groups_unchanged))
                )
                end_results[ApiResultKeys.GENERIC_STATUS_CODE] = (
                    GenericFailureCodes.FailedToDeleteAllObjects
                )
                end_results[ApiResultKeys.VFENSE_STATUS_CODE] = (
                    GroupFailureCodes.FailedToDeleteAllGroups
                )
                end_results[ApiResultKeys.MESSAGE] = msg

            elif groups_deleted and not groups_unchanged:
                msg = (
                    'group ids deleted: %s'
                    % (', '.join(groups_deleted))
                )
                end_results[ApiResultKeys.GENERIC_STATUS_CODE] = (
                    GenericCodes.ObjectsDeleted
                )
                end_results[ApiResultKeys.VFENSE_STATUS_CODE] = (
                    GroupCodes.GroupsDeleted
                )
                end_results[ApiResultKeys.MESSAGE] = msg

            elif groups_unchanged and not groups_deleted:
                msg = (
                    'group ids unchanged: %s'
                    % (', '.join(groups_unchanged))
                )
                end_results[ApiResultKeys.GENERIC_STATUS_CODE] = (
                    GenericCodes.ObjectsUnchanged
                )
                end_results[ApiResultKeys.VFENSE_STATUS_CODE] = (
                    GroupCodes.GroupsUnchanged
                )
                end_results[ApiResultKeys.MESSAGE] = msg

            return end_results
