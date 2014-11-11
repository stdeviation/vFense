import simplejson as json

from vFense.core.api.base import BaseHandler
from vFense.core.decorators import (
    authenticated_request, results_message, api_catch_it
)
from vFense.core.user.manager import UserManager
from vFense.plugins.patching._db_stats import get_all_app_stats_by_view
from vFense.plugins.patching.stats import *


class ViewStatsByOsHandler(BaseHandler):
    @api_catch_it
    @authenticated_request
    def get(self):
        username = self.get_current_user().encode('utf-8')
        view_name = UserManager(username).properties.current_view
        count = self.get_argument('limit', 3)
        results =  self.get_view_stats_by_os(view_name, count)
        self.set_status(results.http_status_code)
        self.set_header('Content-Type', 'application/json')
        self.write(json.dumps(results.to_dict_non_null(), indent=4))

    @results_message
    @check_permissions(Permissions.READ)
    def get_view_stats_by_os(self, view_name, count):
        results = view_stats_by_os(view_name, count)
        return results


class TagStatsByOsHandler(BaseHandler):
    @api_catch_it
    @authenticated_request
    def get(self, tag_id):
        count = self.get_argument('limit', 3)
        results = self.get_tag_stats_by_os(tag_id, count)
        self.set_status(results.http_status_code)
        self.set_header('Content-Type', 'application/json')
        self.write(json.dumps(results.to_dict_non_null(), indent=4))

    @results_message
    @check_permissions(Permissions.READ)
    def get_tag_stats_by_os(self, tag_id, count):
        results = tag_stats_by_os(tag_id, count)
        return results


class WidgetHandler(BaseHandler):
    @api_catch_it
    @authenticated_request
    def get(self):
        username = self.get_current_user().encode('utf-8')
        view_name = UserManager(username).properties.current_view
        results = self.get_all_app_stats_for_view(view_name)
        self.set_status(results.http_status_code)
        self.set_header('Content-Type', 'application/json')
        self.write(json.dumps(results.to_dict_non_null(), indent=4))

    @results_message
    @check_permissions(Permissions.READ)
    def get_all_app_stats_for_view(self, view_name):
        data = get_all_app_stats_by_view(view_name)

        results = {
            ApiResultKeys.GENERIC_STATUS_CODE: (
                GenericCodes.InformationRetrieved
            ),
            ApiResultKeys.VFENSE_STATUS_CODE: (
                GenericCodes.InformationRetrieved
            ),
            ApiResultKeys.DATA: data,
            ApiResultKeys.COUNT: len(data),
        }
        return results



class BarChartByAppIdByStatusHandler(BaseHandler):
    @api_catch_it
    def get(self):
        username = self.get_current_user().encode('utf-8')
        view_name = UserManager(username).properties.current_view
        appid = self.get_argument('id', None)
        results = (
            self.get_bar_chart_for_appid_by_status(appid, view_name)
        )
        self.set_status(results.http_status_code)
        self.set_header('Content-Type', 'application/json')
        self.write(json.dumps(results.to_dict_non_null(), indent=4))

    @results_message
    @check_permissions(Permissions.READ)
    def get_bar_chart_for_appid_by_status(self, app_id, view_name):
        results = (
            bar_chart_for_appid_by_status(
                app_id=app_id, view_name=view_name
            )
        )
        return results



class OsAppsOverTimeHandler(BaseHandler):
    @api_catch_it
    @authenticated_request
    def get(self):
        username = self.get_current_user().encode('utf-8')
        view_name = UserManager(username).properties.current_view
        status = self.get_argument('status', 'available')
        start_date = self.get_argument('start_date', None)
        end_date = self.get_argument('end_date', None)
        if start_date:
            start_date = int(start_date)
        if end_date:
            end_date = int(end_date)

        results = (
            self.get_system_apps_history(
                view_name, status, start_date, end_date
            )
        )
        self.set_status(results.http_status_code)
        self.set_header('Content-Type', 'application/json')
        self.write(json.dumps(results.to_dict_non_null(), indent=4))


    @results_message
    @check_permissions(Permissions.READ)
    def get_system_apps_history(self, view_name, status,
                                start_date, end_date):
        results = (
            get_os_apps_history(
                view_name, status, start_date, end_date
            )
        )
        return results


class AgentOsAppsOverTimeHandler(BaseHandler):
    @api_catch_it
    @authenticated_request
    def get(self, agent_id):
        status = self.get_argument('status', 'available')
        start_date = self.get_argument('start_date', None)
        end_date = self.get_argument('end_date', None)
        if start_date:
            start_date = int(start_date)
        if end_date:
            end_date = int(end_date)

        results = (
            self.get_system_apps_history_for_agent(
                agent_id, status, start_date, end_date
            )
        )
        self.set_status(results.http_status_code)
        self.set_header('Content-Type', 'application/json')
        self.write(json.dumps(results.to_dict_non_null(), indent=4))

    @results_message
    @check_permissions(Permissions.READ)
    def get_system_apps_history_for_agent(self, agent_id, status,
                                          start_date, end_date):
        results = (
            get_os_apps_history_for_agent(
                agent_id, status, start_date, end_date
            )
        )
        return results


class TagOsAppsOverTimeHandler(BaseHandler):
    @api_catch_it
    @authenticated_request
    def get(self, tag_id):
        status = self.get_argument('status', 'available')
        start_date = self.get_argument('start_date', None)
        end_date = self.get_argument('end_date', None)
        if start_date:
            start_date = int(start_date)
        if end_date:
            end_date = int(end_date)

        results = (
            self.get_system_apps_history_for_tag(
                tag_id, status, start_date, end_date
            )
        )
        self.set_status(results.http_status_code)
        self.set_header('Content-Type', 'application/json')
        self.write(json.dumps(results.to_dict_non_null(), indent=4))

    @results_message
    @check_permissions(Permissions.READ)
    def get_system_apps_history_for_tag(self, tag_id, status,
                                          start_date, end_date):
        results = (
            get_os_apps_history_for_tag(
                tag_id, status, start_date, end_date
            )
        )
        return results


class TopAppsNeededHandler(BaseHandler):
    @api_catch_it
    @authenticated_request
    def get(self):
        username = self.get_current_user().encode('utf-8')
        view_name = UserManager(username).properties.current_view
        count = int(self.get_argument('count', '5'))
        results = self.get_top_packages_needed(view_name, count)
        self.set_status(results.http_status_code)
        self.set_header('Content-Type', 'application/json')
        self.write(json.dumps(results.to_dict_non_null(), indent=4))

    @results_message
    @check_permissions(Permissions.READ)
    def get_top_packages_needed(self, view_name, count):
        results = top_packages_needed(view_name, count)
        return results


class RecentlyReleasedHandler(BaseHandler):
    @api_catch_it
    @authenticated_request
    def get(self):
        username = self.get_current_user().encode('utf-8')
        view_name = UserManager(username).properties.current_view
        count = int(self.get_argument('count', 5))
        results = self.get_recently_released_packages(view_name, count)
        self.set_status(results.http_status_code)
        self.set_header('Content-Type', 'application/json')
        self.write(json.dumps(results.to_dict_non_null(), indent=4))


    @results_message
    @check_permissions(Permissions.READ)
    def get_recently_released_packages(self, view_name, count):
        results = recently_released_packages(view_name, count)
        return results


class ViewSeverityHandler(BaseHandler):
    @api_catch_it
    @authenticated_request
    def get(self):
        username = self.get_current_user().encode('utf-8')
        view_name = UserManager(username).properties.current_view
        results = self.get_sev_bar_chart_stats_for_view(view_name)
        self.set_status(results.http_status_code)
        self.set_header('Content-Type', 'application/json')
        self.write(json.dumps(results.to_dict_non_null(), indent=4))

    @results_message
    @check_permissions(Permissions.READ)
    def get_sev_bar_chart_stats_for_view(self, view_name):
        results = get_severity_bar_chart_stats_for_view(view_name)
        return results


class AgentSeverityHandler(BaseHandler):
    @api_catch_it
    @authenticated_request
    def get(self, agent_id):
        results = self.get_sev_bar_chart_stats_for_agent(agent_id)
        self.set_status(results.http_status_code)
        self.set_header('Content-Type', 'application/json')
        self.write(json.dumps(results.to_dict_non_null(), indent=4))


    @results_message
    @check_permissions(Permissions.READ)
    def get_sev_bar_chart_stats_for_agent(self, agent_id):
        results = get_severity_bar_chart_stats_for_agent(agent_id)
        return results


class TagSeverityHandler(BaseHandler):
    @api_catch_it
    @authenticated_request
    def get(self, tag_id):
        results = self.get_sev_bar_chart_stats_for_tag(tag_id)
        self.set_status(results.http_status_code)
        self.set_header('Content-Type', 'application/json')
        self.write(json.dumps(results.to_dict_non_null(), indent=4))

    @results_message
    @check_permissions(Permissions.READ)
    def get_sev_bar_chart_stats_for_tag(self, tag_id):
        results = get_severity_bar_chart_stats_for_tag(tag_id)
        return results
