import simplejson as json
import logging
import logging.config
from vFense import VFENSE_LOGGING_CONFIG

from vFense.core.api.base import BaseHandler
from vFense.db.client import *
from vFense.utils.common import *

from vFense.errorz.error_messages import GenericResults
from vFense.plugins.patching._db_stats import get_all_app_stats_by_view
from vFense.plugins.patching.stats import *
from vFense.core.decorators import authenticated_request

from vFense.core.user import UserKeys
from vFense.core.user.manager import UserManager

from vFense.core.decorators import (
    convert_json_to_arguments, authenticated_request, results_message
)

logging.config.fileConfig(VFENSE_LOGGING_CONFIG)
logger = logging.getLogger('rvapi')


class ViewStatsByOsHandler(BaseHandler):
    @authenticated_request
    def get(self):
        username = self.get_current_user().encode('utf-8')
        view_name = (
            UserManager(username).get_attribute(UserKeys.CurrentView)
        )
        uri = self.request.uri
        method = self.request.method
        try:
            count = self.get_argument('limit', 3)
            results =  (
                self.get_view_stats_by_os(view_name, count)
            )
            self.set_status(results['http_status'])
            self.set_header('Content-Type', 'application/json')
            self.write(json.dumps(results, indent=4))
        except Exception as e:
            results = (
                GenericResults(
                    username, uri, method
                ).something_broke('view os stats', 'os stats', e)
            )
            logger.exception(results)
            self.set_status(results['http_status'])
            self.set_header('Content-Type', 'application/json')
            self.write(json.dumps(results, indent=4))

    @results_message
    def get_view_stats_by_os(self, view_name, count):
        results = view_stats_by_os(view_name, count)
        return results


class TagStatsByOsHandler(BaseHandler):
    @authenticated_request
    def get(self, tag_id):
        username = self.get_current_user().encode('utf-8')
        view_name = (
            UserManager(username).get_attribute(UserKeys.CurrentView)
        )
        uri = self.request.uri
        method = self.request.method
        try:
            count = self.get_argument('limit', 3)
            results = self.get_tag_stats_by_os(tag_id, count)
            self.set_status(results['http_status'])
            self.set_header('Content-Type', 'application/json')
            self.write(json.dumps(results, indent=4))
        except Exception as e:
            results = (
                GenericResults(
                    username, uri, method
                ).something_broke('view os stats', 'os stats', e)
            )
            logger.exception(results)
            self.set_status(results['http_status'])
            self.set_header('Content-Type', 'application/json')
            self.write(json.dumps(results, indent=4))

    @results_message
    def get_tag_stats_by_os(self, tag_id, count):
        results = tag_stats_by_os(tag_id, count)
        return results


class WidgetHandler(BaseHandler):
    @authenticated_request
    def get(self):
        username = self.get_current_user().encode('utf-8')
        view_name = (
            UserManager(username).get_attribute(UserKeys.CurrentView)
        )
        uri = self.request.uri
        method = self.request.method
        try:
            results = (
                self.get_all_app_stats_for_view(view_name)
            )
            self.set_status(results['http_status'])
            self.set_header('Content-Type', 'application/json')
            self.write(json.dumps(results, indent=4))
        except Exception as e:
            results = (
                GenericResults(
                    username, uri, method
                ).something_broke('widget handler', 'widgets', e)
            )
            logger.exception(results)
            self.set_status(results['http_status'])
            self.set_header('Content-Type', 'application/json')
            self.write(json.dumps(results, indent=4))

    @results_message
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
    def get(self):
        username = self.get_current_user().encode('utf-8')
        view_name = (
            UserManager(username).get_attribute(UserKeys.CurrentView)
        )
        appid = self.get_argument('id', None)
        results = (
            self.get_bar_chart_for_appid_by_status(appid, view_name)
        )
        self.set_header('Content-Type', 'application/json')
        self.write(json.dumps(results, indent=4))

    @results_message
    def get_bar_chart_for_appid_by_status(self, app_id, view_name):
        results = (
            bar_chart_for_appid_by_status(
                app_id=app_id, view_name=view_name
            )
        )
        return results



class OsAppsOverTimeHandler(BaseHandler):
    @authenticated_request
    def get(self):
        username = self.get_current_user().encode('utf-8')
        view_name = (
            UserManager(username).get_attribute(UserKeys.CurrentView)
        )
        uri = self.request.uri
        method = self.request.method
        try:
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
            self.set_status(results['http_status'])
            self.set_header('Content-Type', 'application/json')
            self.write(json.dumps(results, indent=4))

        except Exception as e:
            results = (
                GenericResults(
                    username, uri, method
                ).something_broke('view os stats', 'os stats', e)
            )
            logger.exception(results)
            self.set_status(results['http_status'])
            self.set_header('Content-Type', 'application/json')
            self.write(json.dumps(results, indent=4))

    @results_message
    def get_system_apps_history(self, view_name, status,
                                start_date, end_date):
        results = (
            get_os_apps_history(
                view_name, status, start_date, end_date
            )
        )
        return results


class AgentOsAppsOverTimeHandler(BaseHandler):
    @authenticated_request
    def get(self, agent_id):
        username = self.get_current_user().encode('utf-8')
        view_name = (
            UserManager(username).get_attribute(UserKeys.CurrentView)
        )
        uri = self.request.uri
        method = self.request.method
        try:
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
            self.set_status(results['http_status'])
            self.set_header('Content-Type', 'application/json')
            self.write(json.dumps(results, indent=4))

        except Exception as e:
            results = (
                GenericResults(
                    username, uri, method
                ).something_broke('view os stats', 'os stats', e)
            )
            logger.exception(results)
            self.set_status(results['http_status'])
            self.set_header('Content-Type', 'application/json')
            self.write(json.dumps(results, indent=4))

    @results_message
    def get_system_apps_history_for_agent(self, agent_id, status,
                                          start_date, end_date):
        results = (
            get_os_apps_history_for_agent(
                agent_id, status, start_date, end_date
            )
        )
        return results


class TagOsAppsOverTimeHandler(BaseHandler):
    @authenticated_request
    def get(self, tag_id):
        username = self.get_current_user().encode('utf-8')
        view_name = (
            UserManager(username).get_attribute(UserKeys.CurrentView)
        )
        uri = self.request.uri
        method = self.request.method
        try:
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
            self.set_status(results['http_status'])
            self.set_header('Content-Type', 'application/json')
            self.write(json.dumps(results, indent=4))

        except Exception as e:
            results = (
                GenericResults(
                    username, uri, method
                ).something_broke('view os stats', 'os stats', e)
            )
            logger.exception(results)
            self.set_status(results['http_status'])
            self.set_header('Content-Type', 'application/json')
            self.write(json.dumps(results, indent=4))

    @results_message
    def get_system_apps_history_for_tag(self, tag_id, status,
                                          start_date, end_date):
        results = (
            get_os_apps_history_for_tag(
                agent_id, status, start_date, end_date
            )
        )
        return results


class TopAppsNeededHandler(BaseHandler):
    @authenticated_request
    def get(self):
        username = self.get_current_user().encode('utf-8')
        view_name = (
            UserManager(username).get_attribute(UserKeys.CurrentView)
        )
        count = int(self.get_argument('count', '5'))
        uri = self.request.uri
        method = self.request.method
        try:
            results = self.get_top_packages_needed(view_name, count)
            self.set_status(results['http_status'])
            self.set_header('Content-Type', 'application/json')
            self.write(json.dumps(results, indent=4))

        except Exception as e:
            results = (
                GenericResults(
                    username, uri, method
                ).something_broke('view os stats', 'os stats', e)
            )
            logger.exception(results)
            self.set_status(results['http_status'])
            self.set_header('Content-Type', 'application/json')
            self.write(json.dumps(results, indent=4))

    @results_message
    def get_top_packages_needed(self, view_name, count):
        results = top_packages_needed(view_name, count)
        return results


class RecentlyReleasedHandler(BaseHandler):
    @authenticated_request
    def get(self):
        username = self.get_current_user().encode('utf-8')
        view_name = (
            UserManager(username).get_attribute(UserKeys.CurrentView)
        )
        uri = self.request.uri
        method = self.request.method
        try:
            count = int(self.get_argument('count', 5))
            results = (
                self.get_recently_released_packages(view_name, count)
            )
            self.set_status(results['http_status'])
            self.set_header('Content-Type', 'application/json')
            self.write(json.dumps(results, indent=4))

        except Exception as e:
            results = (
                GenericResults(
                    username, uri, method
                ).something_broke('view os stats', 'os stats', e)
            )
            logger.exception(results)
            self.set_status(results['http_status'])
            self.set_header('Content-Type', 'application/json')
            self.write(json.dumps(results, indent=4))

    @results_message
    def get_recently_released_packages(self, view_name, count):
        results = recently_released_packages(view_name, count)
        return results


class ViewSeverityHandler(BaseHandler):
    @authenticated_request
    def get(self):
        username = self.get_current_user().encode('utf-8')
        view_name = (
            UserManager(username).get_attribute(UserKeys.CurrentView)
        )
        uri = self.request.uri
        method = self.request.method
        try:
            results = (
                self.get_sev_bar_chart_stats_for_view(view_name)
            )
            self.set_status(results['http_status'])
            self.set_header('Content-Type', 'application/json')
            self.write(json.dumps(results, indent=4))

        except Exception as e:
            results = (
                GenericResults(
                    username, uri, method
                ).something_broke('view severity stats', 'sev stats', e)
            )
            logger.exception(results)
            self.set_status(results['http_status'])
            self.set_header('Content-Type', 'application/json')
            self.write(json.dumps(results, indent=4))

    @results_message
    def get_sev_bar_chart_stats_for_view(self, view_name):
        results = get_severity_bar_chart_stats_for_view(view_name)
        return results


class AgentSeverityHandler(BaseHandler):
    @authenticated_request
    def get(self, agent_id):
        username = self.get_current_user().encode('utf-8')
        view_name = (
            UserManager(username).get_attribute(UserKeys.CurrentView)
        )
        uri = self.request.uri
        method = self.request.method
        try:
            results = (
                self.get_sev_bar_chart_stats_for_agent(agent_id)
            )
            self.set_status(results['http_status'])
            self.set_header('Content-Type', 'application/json')
            self.write(json.dumps(results, indent=4))

        except Exception as e:
            results = (
                GenericResults(
                    username, uri, method
                ).something_broke('agent severity stats', 'sev stats', e)
            )
            logger.exception(results)
            self.set_status(results['http_status'])
            self.set_header('Content-Type', 'application/json')
            self.write(json.dumps(results, indent=4))

    @results_message
    def get_sev_bar_chart_stats_for_agent(self, agent_id):
        results = get_severity_bar_chart_stats_for_agent(agent_id)
        return results


class TagSeverityHandler(BaseHandler):
    @authenticated_request
    def get(self, tag_id):
        username = self.get_current_user().encode('utf-8')
        view_name = (
            UserManager(username).get_attribute(UserKeys.CurrentView)
        )
        uri = self.request.uri
        method = self.request.method
        try:
            results = (
                self.get_sev_bar_chart_stats_for_tag(tag_id)
            )
            self.set_status(results['http_status'])
            self.set_header('Content-Type', 'application/json')
            self.write(json.dumps(results, indent=4))

        except Exception as e:
            results = (
                GenericResults(
                    username, uri, method
                ).something_broke('tag severity stats', 'sev stats', e)
            )
            logger.exception(results)
            self.set_status(results['http_status'])
            self.set_header('Content-Type', 'application/json')
            self.write(json.dumps(results, indent=4))

    @results_message
    def get_sev_bar_chart_stats_for_tag(self, tag_id):
        results = get_severity_bar_chart_stats_for_tag(tag_id)
        return results

