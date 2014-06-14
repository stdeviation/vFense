import json
import logging
import logging.config
from vFense import VFENSE_LOGGING_CONFIG

from vFense.core._constants import CPUThrottleValues
from vFense.core.api._constants import ApiArguments, ApiValues
from vFense.core.api.base import BaseHandler
from vFense.core.decorators import authenticated_request, convert_json_to_arguments

from vFense.core.permissions._constants import *
from vFense.core.permissions.permissions import verify_permission_for_user, \
    return_results_for_permissions

from vFense.core.permissions.decorators import check_permissions
from vFense.core.agent import *
from vFense.core.user._constants import DefaultUsers
from vFense.core.agent.agents import change_view_for_all_agents_in_view, \
    remove_all_agents_for_view

from vFense.core.view._db_model import ViewKeys
from vFense.core.view import View
from vFense.core.view.manager import ViewManager

from vFense.core.view.views import get_properties_for_view, \
    get_properties_for_all_views, get_view, remove_view, \
    remove_views, edit_view, create_view

from vFense.core.user.users import add_users_to_view, \
    remove_users_from_view

from vFense.errorz._constants import ApiResultKeys
from vFense.errorz.error_messages import GenericResults
from vFense.errorz.results import Results
from vFense.errorz.status_codes import ViewFailureCodes, ViewCodes
from vFense.plugins.patching.patching import remove_all_apps_for_view, \
    change_view_for_apps_in_view

logging.config.fileConfig(VFENSE_LOGGING_CONFIG)
logger = logging.getLogger('rvapi')


class ViewHandler(BaseHandler):

    @authenticated_request
    @check_permissions(Permissions.ADMINISTRATOR)
    def get(self, view_name):
        active_user = self.get_current_user()
        uri = self.request.uri
        method = self.request.method
        count = 0
        view_data = {}
        try:
            view_data = get_properties_for_view(view_name)
            if view_data:
                count = 1
                results = (
                    GenericResults(
                        active_user, uri, method
                    ).information_retrieved(view_data, count)
                )
            else:
                results = (
                    GenericResults(
                        active_user, uri, method
                    ).invalid_id(view_name, 'view')
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
    def post(self, view_name):
        active_user = self.get_current_user()
        uri = self.request.uri
        method = self.request.method
        results = None
        try:
            action = self.arguments.get(ApiArguments.ACTION, ApiValues.ADD)
            ### Add Users to this view
            usernames = self.arguments.get(ApiArguments.USERNAMES)
            if not isinstance(usernames, list) and isinstance(usernames, str):
                usernames = usernames.split(',')

            if usernames:
                if action == ApiValues.ADD:
                    results = (
                        add_users_to_view(
                            usernames, view_name,
                            active_user, uri, method
                        )
                    )

                elif action == ApiValues.DELETE:
                    results = (
                        remove_users_from_view(
                            usernames, view_name,
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
                ).something_broke(active_user, 'Views', e)
            )
            logger.exception(e)
            self.set_status(results['http_status'])
            self.set_header('Content-Type', 'application/json')
            self.write(json.dumps(results, indent=4))


    @authenticated_request
    @convert_json_to_arguments
    @check_permissions(Permissions.ADMINISTRATOR)
    def put(self, view_name):
        active_user = self.get_current_user()
        uri = self.request.uri
        method = self.request.method
        results = None
        try:
            net_throttle = self.arguments.get(ApiArguments.NET_THROTTLE, None)
            cpu_throttle = self.arguments.get(ApiArguments.CPU_THROTTLE, None)
            server_queue_ttl = self.arguments.get(ApiArguments.SERVER_QUEUE_TTL, None)
            agent_queue_ttl = self.arguments.get(ApiArguments.AGENT_QUEUE_TTL, None)
            download_url = self.arguments.get(ApiArguments.DOWNLOAD_URL, None)

            view = View(
                view_name,
                net_throttle,
                cpu_throttle,
                server_queue_ttl,
                agent_queue_ttl,
                download_url
            )

            call_info = {
                ApiResultKeys.HTTP_METHOD: method,
                ApiResultKeys.URI: uri,
                ApiResultKeys.USERNAME: active_user,
            }

            results = edit_view(view, **call_info)

            self.set_status(results['http_status'])
            self.set_header('Content-Type', 'application/json')
            self.write(json.dumps(results, indent=4))

        except Exception as e:
            results = (
                GenericResults(
                    active_user, uri, method
                ).something_broke(active_user, 'Views', e)
            )
            logger.exception(e)
            self.set_status(results['http_status'])
            self.set_header('Content-Type', 'application/json')
            self.write(json.dumps(results, indent=4))


    @authenticated_request
    @convert_json_to_arguments
    @check_permissions(Permissions.ADMINISTRATOR)
    def delete(self, view_name):
        active_user = self.get_current_user()
        uri = self.request.uri
        method = self.request.method
        try:
            deleted_agents = (
                self.arguments.get(
                    ApiArguments.DELETE_ALL_AGENTS
                )
            )
            move_agents_to_view = (
                self.arguments.get(
                    ApiArguments.MOVE_AGENTS_TO_CUSTOMER, None
                )
            )

            if move_agents_to_view:
                view_exist = get_view(move_agents_to_view)
                if not view_exist:
                    msg = 'view %s does not exist' % (move_agents_to_view)
                    data = {
                        ApiResultKeys.INVALID_ID: move_agents_to_view,
                        ApiResultKeys.MESSAGE: msg,
                        ApiResultKeys.VFENSE_STATUS_CODE: ViewFailureCodes.ViewDoesNotExist
                    }
                    results = (
                        Results(
                            active_user, uri, method
                        ).invalid_id(**data)
                    )
                    self.set_status(results['http_status'])
                    self.set_header('Content-Type', 'application/json')
                    self.write(json.dumps(results, indent=4))

                else:
                    results = (
                        remove_view(
                            view_name,
                            active_user, uri, method
                        )
                    )
                    self.set_status(results['http_status'])
                    self.set_header('Content-Type', 'application/json')
                    self.write(json.dumps(results, indent=4))
                    if (results[ApiResultKeys.VFENSE_STATUS_CODE] ==
                            ViewCodes.ViewDeleted):

                        change_view_for_all_agents_in_view(
                            view_name, move_agents_to_view
                        )
                        change_view_for_apps_in_view(
                            view_name, move_agents_to_view
                        )

            elif deleted_agents == ApiValues.YES:
                results = (
                    remove_view(
                        view_name,
                        active_user, uri, method
                    )
                )
                self.set_status(results['http_status'])
                self.set_header('Content-Type', 'application/json')
                self.write(json.dumps(results, indent=4))
                if (results[ApiResultKeys.VFENSE_STATUS_CODE] ==
                        ViewCodes.ViewDeleted):

                    remove_all_agents_for_view(view_name)
                    remove_all_apps_for_view(view_name)

            elif deleted_agents == ApiValues.NO:
                results = (
                    remove_view(
                        view_name,
                        active_user, uri, method
                    )
                )
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


class ViewsHandler(BaseHandler):

    @authenticated_request
    @check_permissions(Permissions.ADMINISTRATOR)
    def get(self):
        active_user = self.get_current_user()
        uri = self.request.uri
        method = self.request.method
        all_views = None
        view_context = self.get_argument('view_context', None)
        count = 0
        view_data = {}
        if not view_context and active_user == DefaultUsers.ADMIN:
            all_views = True

        try:
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
                view_data = get_properties_for_all_views(active_user)

            elif granted and all_views and not view_context:
                view_data = get_properties_for_all_views()

            elif granted and view_context and not all_views:
                view_data = get_properties_for_view(view_context)

            elif not granted:
                results = (
                    return_results_for_permissions(
                        active_user, granted, status_code,
                        Permissions.ADMINISTRATOR, uri, method
                    )
                )

            if view_data:
                count = len(view_data)
                results = (
                    GenericResults(
                        active_user, uri, method
                    ).information_retrieved(view_data, count)
                )
            self.set_status(results['http_status'])
            self.set_header('Content-Type', 'application/json')
            self.write(json.dumps(results, indent=4))

        except Exception as e:
            results = (
                GenericResults(
                    active_user, uri, method
                ).something_broke(active_user, 'Views', e)
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
        try:
            view_name = (
                self.arguments.get(ApiArguments.CUSTOMER_NAME)
            )
            pkg_url = (
                self.arguments.get(ApiArguments.DOWNLOAD_URL, None)
            )
            net_throttle = (
                self.arguments.get(ApiArguments.NET_THROTTLE, 0)
            )
            cpu_throttle = (
                self.arguments.get(
                    ApiArguments.CPU_THROTTLE, CPUThrottleValues.NORMAL
                )
            )
            server_queue_ttl = (
                self.arguments.get(ApiArguments.SERVER_QUEUE_TTL, 10)
            )
            agent_queue_ttl = (
                self.arguments.get(ApiArguments.AGENT_QUEUE_TTL, 10)
            )

            view = View(
                view_name,
                net_throttle,
                cpu_throttle,
                server_queue_ttl,
                agent_queue_ttl,
                pkg_url
            )

            results = create_view(
                view, active_user,
                user_name=active_user, uri=uri, method=method
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
        try:
            view_names = (
                self.arguments.get(ApiArguments.CUSTOMER_NAMES)
            )

            if not isinstance(view_names, list):
                view_names = view_names.split(',')

            results = (
                remove_views(
                    view_names,
                    active_user, uri, method
                )
            )
            self.set_status(results['http_status'])
            self.set_header('Content-Type', 'application/json')
            self.write(json.dumps(results, indent=4))

            if (results[ApiResultKeys.VFENSE_STATUS_CODE] ==
                    ViewCodes.ViewDeleted):

                remove_all_agents_for_view(view_name)
                remove_all_apps_for_view(view_name)

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

