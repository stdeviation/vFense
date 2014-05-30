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
from vFense.core.user.users import get_user_property

logging.config.fileConfig(VFENSE_LOGGING_CONFIG)
logger = logging.getLogger('rvapi')


class ViewStatsByOsHandler(BaseHandler):
    @authenticated_request
    def get(self):
        username = self.get_current_user().encode('utf-8')
        view_name = (
            get_user_property(username, UserKeys.CurrentView)
        )
        uri = self.request.uri
        method = self.request.method
        try:
            count = self.get_argument('limit', 3)
            results = (
                view_stats_by_os(
                    view_name, count,
                    username, uri, method
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


class TagStatsByOsHandler(BaseHandler):
    @authenticated_request
    def get(self, tag_id):
        username = self.get_current_user().encode('utf-8')
        view_name = (
            get_user_property(username, UserKeys.CurrentView)
        )
        uri = self.request.uri
        method = self.request.method
        try:
            count = self.get_argument('limit', 3)
            results = (
                tag_stats_by_os(
                    tag_id, count,
                    username, uri, method
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


class WidgetHandler(BaseHandler):
    @authenticated_request
    def get(self):
        username = self.get_current_user().encode('utf-8')
        view_name = (
            get_user_property(username, UserKeys.CurrentView)
        )
        uri = self.request.uri
        method = self.request.method
        try:
            app_stats = (
                get_all_app_stats_by_view(view_name)
            )
            results = (
                GenericResults(
                    username, uri, method
                ).information_retrieved(app_stats)
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


class BarChartByAppIdByStatusHandler(BaseHandler):
    def get(self):
        username = self.get_current_user().encode('utf-8')
        view_name = (
            get_user_property(username, UserKeys.CurrentView)
        )
        appid = self.get_argument('id', None)
        result = bar_chart_for_appid_by_status(app_id=appid,
                                              view_name=view_name)
        self.set_header('Content-Type', 'application/json')
        self.write(json.dumps(result, indent=4))


class OsAppsOverTimeHandler(BaseHandler):
    @authenticated_request
    def get(self):
        username = self.get_current_user().encode('utf-8')
        view_name = (
            get_user_property(username, UserKeys.CurrentView)
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
                get_os_apps_history(
                    view_name, status, start_date, end_date,
                    username, uri, method
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


class AgentOsAppsOverTimeHandler(BaseHandler):
    @authenticated_request
    def get(self, agent_id):
        username = self.get_current_user().encode('utf-8')
        view_name = (
            get_user_property(username, UserKeys.CurrentView)
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
                get_os_apps_history_for_agent(
                    agent_id, status, start_date, end_date,
                    username, uri, method
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


class TagOsAppsOverTimeHandler(BaseHandler):
    @authenticated_request
    def get(self, tag_id):
        username = self.get_current_user().encode('utf-8')
        view_name = (
            get_user_property(username, UserKeys.CurrentView)
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
                get_os_apps_history_for_tag(
                    tag_id, status, start_date, end_date,
                    username, uri, method
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


class TopAppsNeededHandler(BaseHandler):
    @authenticated_request
    def get(self):
        username = self.get_current_user().encode('utf-8')
        view_name = (
            get_user_property(username, UserKeys.CurrentView)
        )
        count = int(self.get_argument('count', '5'))
        uri = self.request.uri
        method = self.request.method
        try:
            results = (
                top_packages_needed(
                    view_name, count,
                    username, uri, method
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


class RecentlyReleasedHandler(BaseHandler):
    @authenticated_request
    def get(self):
        username = self.get_current_user().encode('utf-8')
        view_name = (
            get_user_property(username, UserKeys.CurrentView)
        )
        uri = self.request.uri
        method = self.request.method
        try:
            count = int(self.get_argument('count', 5))
            results = (
                recently_released_packages(
                    view_name, count,
                    username, uri, method
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


class ViewSeverityHandler(BaseHandler):
    @authenticated_request
    def get(self):
        username = self.get_current_user().encode('utf-8')
        view_name = (
            get_user_property(username, UserKeys.CurrentView)
        )
        uri = self.request.uri
        method = self.request.method
        try:
            results = (
                get_severity_bar_chart_stats_for_view(
                    view_name, username, uri, method
                )
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


class AgentSeverityHandler(BaseHandler):
    @authenticated_request
    def get(self, agent_id):
        username = self.get_current_user().encode('utf-8')
        view_name = (
            get_user_property(username, UserKeys.CurrentView)
        )
        uri = self.request.uri
        method = self.request.method
        try:
            results = (
                get_severity_bar_chart_stats_for_agent(
                    agent_id, username, uri, method
                )
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


class TagSeverityHandler(BaseHandler):
    @authenticated_request
    def get(self, tag_id):
        username = self.get_current_user().encode('utf-8')
        view_name = (
            get_user_property(username, UserKeys.CurrentView)
        )
        uri = self.request.uri
        method = self.request.method
        try:
            results = (
                get_severity_bar_chart_stats_for_tag(
                    tag_id, username,
                    uri, method
                )
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

