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

from vFense.result._constants import ApiResultKeys
from vFense.result.error_messages import GenericResults
from vFense.result.results import Results
from vFense.result.status_codes import (
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
        results[ApiResultKeys.DATA] = results[ApiResultKeys.DATA][0]
        return results

    @authenticated_request
    @convert_json_to_arguments
    @check_permissions(Permissions.ADMINISTRATOR)
    def post(self, group_id):
        active_user = self.get_current_user()
        uri = self.request.uri
        http_method = self.request.method
        group = GroupManager(group_id)
        try:
            action = self.arguments.get(ApiArguments.ACTION)
            force = self.arguments.get(ApiArguments.FORCE_REMOVE, False)
            ###Add Users###
            usernames = self.arguments.get(ApiArguments.USERNAMES, [])
            if usernames and isinstance(usernames, list):
                if action == ApiValues.ADD:
                    results = self.add_users(group, usernames)

                if action == ApiValues.DELETE:
                    results = self.remove_users(group, usernames, force)

            ###Add Views###
            views = self.arguments.get(ApiArguments.VIEW_NAMES, [])
            if views and isinstance(views, list):
                if action == ApiValues.ADD:
                    results = self.add_views(group, views)

                if action == ApiValues.DELETE:
                    results = self.remove_views(group, views, force)

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
    def add_views(self, group, views):
        results = group.add_views(views)
        return results

    @results_message
    def add_users(self, group, users):
        results = group.add_users(users)
        return results

    @log_operation(AdminActions.REMOVE_VIEWS_FROM_GROUP, vFenseObjects.GROUP)
    @results_message
    def remove_views(self, group, views, force):
        results = group.remove_views(views, force)
        return results

    @log_operation(AdminActions.REMOVE_USERS_FROM_GROUP, vFenseObjects.GROUP)
    @results_message
    def remove_users(self, group, users, force):
        results = group.remove_users(users, force)
        return results


    @authenticated_request
    @convert_json_to_arguments
    @check_permissions(Permissions.ADMINISTRATOR)
    def delete(self, group_id):
        active_user = self.get_current_user()
        uri = self.request.uri
        http_method = self.request.method
        manager = GroupManager(group_id)
        try:
            ###Remove GroupId###
            results = self.remove_group(manager)

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
    def remove_group(self, manager):
        results = manager.remove()
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
        is_global = user.get_attribute(UserKeys.Global)
        view_context = self.get_argument('view_context', None)
        group_id = self.get_argument('group_id', None)
        all_views = self.get_argument('all_views', None)
        count = int(self.get_argument('count', 30))
        offset = int(self.get_argument('offset', 0))
        sort = self.get_argument('sort', 'asc')
        sort_by = self.get_argument('sort_by', GroupKeys.GroupName)
        regex = self.get_argument('regex', None)
        try:
            granted, status_code = (
                verify_permission_for_user(
                    active_user, Permissions.ADMINISTRATOR, view_context
                )
            )
            if granted:
                if not view_context and not all_views and not group_id:
                    fetch_groups = (
                        RetrieveGroups(
                            active_view, count=count, offset=offset,
                            sort=sort, sort_key=sort_by,
                            is_global=is_global
                        )
                    )

                elif view_context and not all_views and not group_id:
                    fetch_groups = (
                        RetrieveGroups(
                            view_context, count=count, offset=offset,
                            sort=sort, sort_key=sort_by,
                            is_global=is_global
                        )
                    )

                else:
                    fetch_groups = (
                        RetrieveGroups(
                            view_context, count=count, offset=offset,
                            sort=sort, sort_key=sort_by,
                            is_global=is_global
                        )
                    )

                if group_id:
                    results = self.get_group_by_id(fetch_groups, group_id)

                elif regex:
                    results = (
                        self.get_all_groups_by_regex(fetch_groups, regex)
                    )

                else:
                    results = (
                        self.get_all_groups(fetch_groups)
                    )


            else:
                results = (
                    return_results_for_permissions(
                        active_user, granted, status_code,
                        Permissions.ADMINISTRATOR, uri, http_method
                    )
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
    def get_all_groups(self, fetch_groups):
        results = fetch_groups.all()
        return results

    @results_message
    def get_all_groups_by_regex(self, fetch_groups, regex):
        results = fetch_groups.by_regex(regex)
        return results

    @results_message
    def get_group_by_id(self, fetch_groups, group_id):
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
            group = Group(
                group_name, permissions, views, is_global
            )
            if not invalid_value:
                results = self.create_group(group)
            else:
                msg = {
                    ApiResultKeys.MESSAGE: (
                        'Invalid value for argument is_global: %s' %
                        (is_global)
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
    def create_group(self, group):
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
            msg = 'group ids deleted: %s' % (', '.join(groups_deleted))
            end_results[ApiResultKeys.GENERIC_STATUS_CODE] = (
                GenericCodes.ObjectsDeleted
            )
            end_results[ApiResultKeys.VFENSE_STATUS_CODE] = (
                GroupCodes.GroupsDeleted
            )
            end_results[ApiResultKeys.MESSAGE] = msg

        elif groups_unchanged and not groups_deleted:
            msg = 'group ids unchanged: %s' % (', '.join(groups_unchanged))
            end_results[ApiResultKeys.GENERIC_STATUS_CODE] = (
                GenericCodes.ObjectsUnchanged
            )
            end_results[ApiResultKeys.VFENSE_STATUS_CODE] = (
                GroupCodes.GroupsUnchanged
            )
            end_results[ApiResultKeys.MESSAGE] = msg

        return end_results
