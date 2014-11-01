import json
import logging
import logging.config
from vFense._constants import VFENSE_LOGGING_CONFIG

from vFense.core._constants import CPUThrottleValues
from vFense.core.api._constants import (
    ViewApiArguments, ApiArguments, ApiValues
)
from vFense.core.api.base import BaseHandler
from vFense.core.decorators import (
    authenticated_request, convert_json_to_arguments, results_message,
    api_catch_it
)

from vFense.core.permissions._constants import Permissions
from vFense.core.permissions.permissions import (
    verify_permission_for_user, return_results_for_permissions
)

from vFense.core.permissions.decorators import check_permissions
from vFense.core.user._constants import DefaultUsers
from vFense.core.user.manager import UserManager

from vFense.core.user._db_model import UserKeys
from vFense.core.view._db_model import ViewKeys
from vFense.core.view import View
from vFense.core.view.manager import ViewManager
from vFense.core.view.search.search import RetrieveViews

from vFense.core.operations.decorators import log_operation
from vFense.core.operations._admin_constants import AdminActions
from vFense.core.operations._constants import vFenseObjects

from vFense.core.results import ApiResults, ExternalApiResults
from vFense.core.view.status_codes import ViewFailureCodes, ViewCodes

logging.config.fileConfig(VFENSE_LOGGING_CONFIG)
logger = logging.getLogger('rvapi')


class ViewHandler(BaseHandler):
    @api_catch_it
    @authenticated_request
    @check_permissions(Permissions.ADMINISTRATOR)
    def get(self, view_name):
        active_user = self.get_current_user()
        user = UserManager(active_user)
        is_global = user.get_attribute(UserKeys.IsGlobal)
        current_view = user.get_attribute(UserKeys.CurrentView)
        output = self.get_argument(ApiArguments.OUTPUT, 'json')
        results = self.get_view(view_name, is_global, current_view)
        self.set_status(results.http_status_code)
        self.modified_output(results, output, 'view')

    @results_message
    def get_view(self, view, is_global, current_view):
        if is_global:
            fetch_views = RetrieveViews()
        else:
            fetch_views = RetrieveViews(parent_view=current_view)

        results = fetch_views.by_name(view)
        if results.count > 0:
            results.data = results.data[0]
        return results

    @api_catch_it
    @authenticated_request
    @convert_json_to_arguments
    @check_permissions(Permissions.ADMINISTRATOR)
    def post(self, view_name):
        view = ViewManager(view_name)
        action = self.arguments.get(ApiArguments.ACTION, ApiValues.ADD)
        ### Add Users to this view or Remove users from this view
        usernames = self.arguments.get(ApiArguments.USERNAMES, None)
        if not isinstance(usernames, list) and isinstance(usernames, str):
            usernames = usernames.split(',')

        if usernames:
            if action == ApiValues.ADD:
                results = self.add_users(view, usernames)

            elif action == ApiValues.DELETE:
                results = self.remove_users(view, usernames)

        ### Add groups to this view or Remove groups from this view
        group_ids = self.arguments.get(ApiArguments.GROUP_IDS, None)
        if not isinstance(group_ids, list) and isinstance(group_ids, str):
            group_ids = group_ids.split(',')

        if group_ids:
            if action == ApiValues.ADD:
                results = self.add_groups(view, group_ids)

            elif action == ApiValues.DELETE:
                results = self.remove_groups(view, group_ids)

        self.set_status(results.http_status_code)
        self.set_header('Content-Type', 'application/json')
        self.write(json.dumps(results.to_dict_non_null(), indent=4))

    @results_message
    @log_operation(AdminActions.ADD_USERS_TO_VIEW, vFenseObjects.VIEW)
    def add_users(self, view, users):
        results = view.add_users(users)
        return results

    @results_message
    @log_operation(AdminActions.ADD_GROUPS_TO_VIEW, vFenseObjects.VIEW)
    def add_groups(self, view, group_ids):
        results = view.add_groups(group_ids)
        return results

    @results_message
    @log_operation(AdminActions.REMOVE_USERS_FROM_VIEW, vFenseObjects.VIEW)
    def remove_users(self, view, users):
        results = view.remove_users(users)
        return results

    @results_message
    @log_operation(AdminActions.REMOVE_GROUPS_FROM_VIEW, vFenseObjects.VIEW)
    def remove_groups(self, view, group_ids):
        results = view.remove_groups(group_ids)
        return results

    @api_catch_it
    @authenticated_request
    @convert_json_to_arguments
    @check_permissions(Permissions.ADMINISTRATOR)
    def put(self, view_name):
        view = ViewManager(view_name)
        results = {}
        data = []
        net_throttle = self.arguments.get(ViewApiArguments.NET_THROTTLE, None)
        cpu_throttle = self.arguments.get(ViewApiArguments.CPU_THROTTLE, None)
        server_queue_ttl = self.arguments.get(ViewApiArguments.SERVER_QUEUE_TTL, None)
        agent_queue_ttl = self.arguments.get(ViewApiArguments.AGENT_QUEUE_TTL, None)
        download_url = self.arguments.get(ViewApiArguments.DOWNLOAD_URL, None)
        time_zone = self.arguments.get(ViewApiArguments.TIME_ZONE, None)
        token = self.arguments.get(ViewApiArguments.TOKEN, None)

        if net_throttle:
            results = self.edit_net_throttle(view, net_throttle)
            if results.data:
                data.append(results.data)

        if cpu_throttle:
            results = self.edit_cpu_throttle(view, cpu_throttle)
            if results.data:
                data.append(results.data)

        if server_queue_ttl:
            results = self.edit_server_queue_ttl(view, server_queue_ttl)
            if results.data:
                data.append(results.data)

        if agent_queue_ttl:
            results = self.edit_agent_queue_ttl(view, agent_queue_ttl)
            if results.data:
                data.append(results.data)

        if download_url:
            results = self.edit_download_url(view, download_url)
            if results.data:
                data.append(results.data)

        if time_zone:
            results = self.edit_time_zone(view, time_zone)
            if results.data:
                data.append(results.data)

        if token:
            results = self.update_token(view)
            if results.data:
                data.append(results.data)

        results.data = data

        self.set_status(results.http_status_code)
        self.set_header('Content-Type', 'application/json')
        self.write(json.dumps(results.to_dict_non_null(), indent=4))

    @results_message
    @log_operation(AdminActions.EDIT_NET_THROTTLE, vFenseObjects.VIEW)
    def edit_net_throttle(self, view, net_throttle):
        results = view.edit_net_throttle(net_throttle)
        return results

    @results_message
    @log_operation(AdminActions.EDIT_CPU_THROTTLE, vFenseObjects.VIEW)
    def edit_cpu_throttle(self, view, cpu_throttle):
        results = view.edit_cpu_throttle(cpu_throttle)
        return results

    @results_message
    @log_operation(AdminActions.EDIT_SERVER_QUEUE_TTL, vFenseObjects.VIEW)
    def edit_server_queue_ttl(self, view, server_queue_ttl):
        results = view.edit_server_queue_ttl(server_queue_ttl)
        return results

    @results_message
    @log_operation(AdminActions.EDIT_AGENT_QUEUE_TTL, vFenseObjects.VIEW)
    def edit_agent_queue_ttl(self, view, agent_queue_ttl):
        results = view.edit_agent_queue_ttl(agent_queue_ttl)
        return results

    @results_message
    @log_operation(AdminActions.EDIT_DOWNLOAD_URL, vFenseObjects.VIEW)
    def edit_download_url(self, view, package_download_url):
        results = view.edit_download_url(package_download_url)
        return results

    @results_message
    @log_operation(AdminActions.EDIT_TIME_ZONE, vFenseObjects.VIEW)
    def edit_time_zone(self, view, time_zone):
        results = view.edit_time_zone(time_zone)
        return results

    @results_message
    @log_operation(AdminActions.NEW_TOKEN, vFenseObjects.VIEW)
    def update_token(self, view):
        results = view.update_token()
        return results

    @api_catch_it
    @authenticated_request
    @convert_json_to_arguments
    @check_permissions(Permissions.ADMINISTRATOR)
    def delete(self, view_name):
        view = ViewManager(view_name)
        delete_agents = self.arguments.get(ApiArguments.DELETE_ALL_AGENTS)
        view_name= self.arguments.get(ApiArguments.VIEW_NAME, None)
        results = self.remove_view(view, delete_agents, view_name)

        self.set_status(results.http_status_code)
        self.set_header('Content-Type', 'application/json')
        self.write(json.dumps(results.to_dict_non_null(), indent=4))

    @results_message
    @log_operation(AdminActions.REMOVE_VIEW, vFenseObjects.VIEW)
    def remove_view(self, view, delete_agents, view_name):
        if delete_agents:
            view.delete_agents()

        elif view:
            agents = view.agents
            view.move_agents(agents, view_name)

        results = view.remove()
        return results


class ViewsHandler(BaseHandler):
    @api_catch_it
    @authenticated_request
    @check_permissions(Permissions.ADMINISTRATOR)
    def get(self):
        active_user = self.get_current_user()
        all_views = None
        user = UserManager(active_user)
        is_global = user.get_attribute(UserKeys.IsGlobal)
        view_context = self.get_argument('view_context', None)
        parent_view = self.get_argument('parent_view', None)
        query = self.get_argument('query', None)
        count = int(self.get_argument('count', 30))
        offset = int(self.get_argument('offset', 0))
        sort = self.get_argument('sort', 'asc')
        sort_by = self.get_argument('sort_by', ViewKeys.ViewName)
        output = self.get_argument(ApiArguments.OUTPUT, 'json')
        fetch_views = (
            RetrieveViews(
                parent_view, count, offset, sort, sort_by, is_global
            )
        )
        if not view_context and active_user == DefaultUsers.GLOBAL_ADMIN:
            all_views = True

        if view_context:
            granted, status_code = (
                verify_permission_for_user(
                    active_user, Permissions.ADMINISTRATOR, view_context
                )
            )
        else:
            granted, status_code = (
                verify_permission_for_user(
                    active_user, Permissions.ADMINISTRATOR
                )
            )
        if granted and not all_views and not view_context:
            results = self.get_all_views_for_user(fetch_views, active_user)

        elif granted and all_views and not view_context:
            results = self.get_all_views(fetch_views)

        elif granted and view_context and not all_views:
            results = self.get_view(fetch_views, view_context)

        elif granted and query:
            results = self.get_all_views_by_regex(fetch_views, query)

        elif not granted:
            results = (
                return_results_for_permissions(
                    active_user, granted, status_code,
                    Permissions.ADMINISTRATOR, self.request.uri,
                    self.request.method
                )
            )

        self.set_status(results.http_status_code)
        self.modified_output(results.to_dict_non_null(), output, 'views')

    @results_message
    def get_all_views(self, fetch_views):
        results = fetch_views.all()
        return results

    @results_message
    def get_all_views_for_user(self, fetch_views, username):
        results = fetch_views.for_user(username)
        return results

    @results_message
    def get_all_views_by_regex(self, fetch_views, regex):
        results = fetch_views.by_regex(regex)
        return results

    @results_message
    def get_view(self, fetch_views, view_name):
        results = fetch_views.by_name(view_name)
        return results

    @api_catch_it
    @authenticated_request
    @convert_json_to_arguments
    @check_permissions(Permissions.ADMINISTRATOR)
    def post(self):
        active_user = self.get_current_user()
        user = UserManager(active_user)
        active_view = user.get_attribute(UserKeys.CurrentView)
        parent_view = self.get_argument('view_context', active_view)
        view_name = self.arguments.get(ViewApiArguments.VIEW_NAME)
        pkg_url = self.arguments.get(ViewApiArguments.DOWNLOAD_URL, None)
        net_throttle = self.arguments.get(ViewApiArguments.NET_THROTTLE, 0)
        cpu_throttle = (
            self.arguments.get(
                ViewApiArguments.CPU_THROTTLE, CPUThrottleValues.NORMAL
            )
        )
        server_queue_ttl = (
            self.arguments.get(ViewApiArguments.SERVER_QUEUE_TTL, 10)
        )
        agent_queue_ttl = (
            self.arguments.get(ViewApiArguments.AGENT_QUEUE_TTL, 10)
        )
        time_zone = (
            self.arguments.get(ViewApiArguments.TIME_ZONE, 'UTC')
        )
        view = View(
            view_name, parent_view, users=[active_user],
            net_throttle=net_throttle, cpu_throttle=cpu_throttle,
            server_queue_ttl=server_queue_ttl,
            agent_queue_ttl=agent_queue_ttl, package_download_url=pkg_url,
            time_zone=time_zone
        )

        results = self.create_view(view)

        self.set_status(results.http_status_code)
        self.set_header('Content-Type', 'application/json')
        self.write(json.dumps(results.to_dict_non_null(), indent=4))

    @results_message
    @log_operation(AdminActions.CREATE_VIEW, vFenseObjects.VIEW)
    def create_view(self, view):
        manager = ViewManager(view.name)
        results = manager.create(view)
        return results

    @api_catch_it
    @authenticated_request
    @convert_json_to_arguments
    @check_permissions(Permissions.ADMINISTRATOR)
    def delete(self):
        view_names = self.arguments.get(ApiArguments.VIEW_NAMES)

        if not isinstance(view_names, list):
            view_names = view_names.split(',')

        results = self.remove_views(view_names, True)
        self.set_status(results.http_status_code)
        self.set_header('Content-Type', 'application/json')
        self.write(json.dumps(results.to_dict_non_null(), indent=4))

    @results_message
    @log_operation(AdminActions.REMOVE_VIEWS, vFenseObjects.VIEW)
    def remove_views(self, view_names, force=False):
        end_results = ApiResults()
        end_results.fill_in_defaults()
        views_deleted = []
        views_unchanged = []
        for view_name in view_names:
            manager = ViewManager(view_name)
            manager.remove_agents()
            results = manager.remove(force)
            if (results.vfense_status_code
                    == ViewCodes.ViewDeleted):
                views_deleted.append(view_name)
            else:
                views_unchanged.append(view_name)

        end_results.unchanged_ids = views_unchanged
        end_results.deleted_ids = views_deleted
        if views_unchanged and views_deleted:
            msg = (
                'view names deleted: %s, view names unchanged: %s'
                % (', '.join(views_deleted), ', '.join(views_unchanged))
            )
            end_results.generic_status_code = (
                ViewFailureCodes.FailedToDeleteAllObjects
            )
            end_results.vfense_status_code = (
                ViewFailureCodes.FailedToDeleteAllViews
            )
            end_results.message = msg

        elif views_deleted and not views_unchanged:
            msg = (
                'view names deleted: %s' % (', '.join(views_deleted))
            )
            end_results.generic_status_code = (
                ViewCodes.ObjectsDeleted
            )
            end_results.vfense_status_code = (
                ViewCodes.ViewsDeleted
            )
            end_results.message = msg

        elif views_unchanged and not views_deleted:
            end_results.generic_status_code = (
                ViewCodes.ObjectsUnchanged
            )
            end_results.vfense_status_code = (
                ViewCodes.ViewsUnchanged
            )
            end_results.message = (
                results.message
            )

        return end_results
