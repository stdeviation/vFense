import logging
import logging.config
from datetime import datetime
import simplejson as json

from vFense.core.api.base import BaseHandler
from vFense import VFENSE_LOGGING_CONFIG

#from vFense.scheduler.jobManager import schedule_once
from vFense.plugins.patching.api.base import AppsBaseHandler
from vFense.plugins.patching.scheduler.manager import (
    AgentAppsJobManager, TagAppsJobManager
)
from vFense.plugins.patching.operations._constants import InstallKeys
from vFense.plugins.patching.operations import Install

from vFense.plugins.patching.search.search_by_tagid import (
    RetrieveAppsByTagId
)

from vFense.plugins.patching.search.search_by_agentid import (
    RetrieveAppsByAgentId
)

from vFense.plugins.patching.search.search_by_appid import (
    RetrieveAgentsByAppId
)

from vFense.plugins.patching.search.search import (
    RetrieveApps
)

from vFense.core.agent._db_model import AgentKeys
from vFense.plugins.patching._db_model import AppsKey
from vFense.core._constants import CommonKeys
from vFense.core.permissions._constants import Permissions
from vFense.core.permissions.decorators import check_permissions
from vFense.core.results import Results, ApiResultKeys

from vFense.plugins.patching._db import update_app_data_by_app_id
from vFense.plugins.patching.operations.store_operations import StorePatchingOperation
from vFense.plugins.patching.patching import toggle_hidden_status
from vFense.core.decorators import (
    authenticated_request, convert_json_to_arguments, results_message
)

from vFense.core.user import UserKeys
from vFense.core.user.manager import UserManager
from vFense.core.api._constants import (
    ApiArguments
)
from vFense.core._constants import DefaultQueryValues, SortValues
from vFense.core.operations._constants import AgentOperations
from vFense.plugins.patching.api._constants import (
    AppApiArguments, AppFilterValues
)
from vFense.plugins.patching._constants import (
    AppStatuses, CommonSeverityKeys
)

logging.config.fileConfig(VFENSE_LOGGING_CONFIG)
logger = logging.getLogger('rvapi')


class AgentIdOsAppsHandler(AppsBaseHandler):
    @authenticated_request
    def get(self, agent_id):
        active_user = self.get_current_user().encode('utf-8')
        self.get_and_set_search_arguments()
        search = (
            RetrieveAppsByAgentId(
                agent_id, self.count, self.offset,
                self.sort, self.sort_by, show_hidden=self.hidden
            )
        )

        results = self.app_search_results(search, active_user)
        self.set_status(results['http_status'])
        self.modified_output(results, self.output, 'apps')


    @authenticated_request
    @convert_json_to_arguments
    def put(self, agent_id):
        active_user = self.get_current_user().encode('utf-8')
        active_view = (
            UserManager(active_user).get_attribute(UserKeys.CurrentView)
        )
        self.get_and_set_install_arguments()
        self.app_ids = self.arguments.get('app_ids')
        install = (
            Install(
                self.app_ids, [agent_id], user_name=active_user,
                view_name=active_view, restart=self.restart,
                net_throttle=self.net_throttle, cpu_throttle=self.cpu_throttle
            )
        )
        operation = (
            StorePatchingOperation(active_user, active_view)
        )

        sched = self.application.scheduler
        job = AgentAppsJobManager(sched, active_view)
        results = (
            self.get_install_results(
                operation, install, active_user, job,
                AgentOperations.INSTALL_OS_APPS
            )
        )
        self.set_status(results['http_status'])
        self.set_header('Content-Type', 'application/json')
        self.write(json.dumps(results, indent=4))


    @authenticated_request
    @convert_json_to_arguments
    @check_permissions(Permissions.UNINSTALL)
    def delete(self, agent_id):
        active_user = self.get_current_user().encode('utf-8')
        active_view = (
            UserManager(active_user).get_attribute(UserKeys.CurrentView)
        )
        self.get_and_set_install_arguments()
        self.app_ids = self.arguments.get('app_ids')
        install = (
            Install(
                self.app_ids, [agent_id], user_name=active_user,
                view_name=active_view, restart=self.restart,
                net_throttle=self.net_throttle, cpu_throttle=self.cpu_throttle
            )
        )
        operation = (
            StorePatchingOperation(active_user, active_view)
        )

        sched = self.application.scheduler
        job = AgentAppsJobManager(sched, install.view_name)
        results = (
            self.get_uninstall_results(
                operation, install, active_user, job
            )
        )
        self.set_status(results['http_status'])
        self.set_header('Content-Type', 'application/json')
        self.write(json.dumps(results, indent=4))


class TagIdOsAppsHandler(AppsBaseHandler):
    @authenticated_request
    def get(self, tag_id):
        active_user = self.get_current_user().encode('utf-8')
        self.get_and_set_search_arguments()
        search = (
            RetrieveAppsByTagId(
                tag_id, self.count, self.offset,
                self.sort, self.sort_by, show_hidden=self.hidden
            )
        )
        results = self.app_search_results(search, active_user)
        self.set_status(results['http_status'])
        self.modified_output(results, self.output, 'apps')

    @authenticated_request
    @convert_json_to_arguments
    def put(self, tag_id):
        active_user = self.get_current_user().encode('utf-8')
        active_view = (
            UserManager(active_user).get_attribute(UserKeys.CurrentView)
        )
        self.get_and_set_install_arguments()
        self.app_ids = self.arguments.get('app_ids')
        install = (
            Install(
                self.app_ids, [], tag_id=tag_id, user_name=active_user,
                view_name=active_view, restart=self.restart,
                net_throttle=self.net_throttle, cpu_throttle=self.cpu_throttle
            )
        )
        operation = (
            StorePatchingOperation(active_user, active_view)
        )

        sched = self.application.scheduler
        job = TagAppsJobManager(sched, active_view)
        results = (
            self.get_install_results(
                operation, install, active_user, job,
                AgentOperations.INSTALL_OS_APPS
            )
        )
        self.set_status(results['http_status'])
        self.set_header('Content-Type', 'application/json')
        self.write(json.dumps(results, indent=4))
        return results


    @authenticated_request
    @convert_json_to_arguments
    def delete(self, tag_id):
        active_user = self.get_current_user().encode('utf-8')
        active_view = (
            UserManager(active_user).get_attribute(UserKeys.CurrentView)
        )
        self.get_and_set_install_arguments()
        self.app_ids = self.arguments.get('app_ids')
        install = (
            Install(
                self.app_ids, [], tag_id=tag_id, user_name=active_user,
                view_name=active_view, restart=self.restart,
                net_throttle=self.net_throttle, cpu_throttle=self.cpu_throttle
            )
        )
        operation = (
            StorePatchingOperation(active_user, active_view)
        )

        sched = self.application.scheduler
        job = TagAppsJobManager(sched, install.view_name)
        results = (
            self.get_uninstall_results(
                operation, install, active_user, job
            )
        )
        self.set_status(results['http_status'])
        self.set_header('Content-Type', 'application/json')
        self.write(json.dumps(results, indent=4))


class AppIdOsAppsHandler(AppsBaseHandler):
    @authenticated_request
    def get(self, app_id):
        active_user = self.get_current_user().encode('utf-8')
        active_view = (
            UserManager(active_user).get_attribute(UserKeys.CurrentView)
        )
        output = self.get_argument(ApiArguments.OUTPUT, 'json')
        search = RetrieveApps(active_view)
        results = self.by_id(search, app_id)
        self.set_status(results['http_status'])
        self.modified_output(results, output, 'app')

    @results_message
    def by_id(self, search, app_id):
        results = search.by_id(app_id)
        return results

    @authenticated_request
    @convert_json_to_arguments
    @check_permissions(Permissions.ADMINISTRATOR)
    def post(self, app_id):
        active_user = self.get_current_user().encode('utf-8')
        uri = self.request.uri
        method = self.request.method
        try:
            severity = self.arguments.get('severity').capitalize()
            if severity in CommonSeverityKeys.ValidRvSeverities:
                sev_data = (
                    {
                        AppsKey.RvSeverity: severity
                    }
                )
                update_app_data_by_app_id(
                    app_id, sev_data
                )
                data = {
                    ApiResultKeys.MESSAGE: (
                        'Severity updated for app id: {0}'.format(app_id)
                    ),
                    ApiResultKeys.DATA: [sev_data],
                    ApiResultKeys.UPDATED_IDS: app_id
                }
                results = (
                    Results(
                        active_user, uri, method
                    ).object_updated(**data)
                )
                self.set_status(results['http_status'])
                self.set_header('Content-Type', 'application/json')
                self.write(json.dumps(results, indent=4))

            else:
                data = {
                    ApiResultKeys.MESSAGE: (
                        'Severity failed to update for app id: {0}'
                        .format(app_id)
                    ),
                    ApiResultKeys.DATA: [sev_data],
                    ApiResultKeys.UNCHANGED_IDS: app_id
                }
                results = (
                    Results(
                        active_user, uri, method
                    ).objects_failed_to_update(severity)
                )
                self.set_status(results['http_status'])
                self.set_header('Content-Type', 'application/json')
                self.write(json.dumps(results, indent=4))

        except Exception as e:
            data = {
                ApiResultKeys.MESSAGE: (
                    'Severity failed to update for app id {0}, error: {1}'
                    .format(app_id, e)
                ),
                ApiResultKeys.DATA: [sev_data],
                ApiResultKeys.UNCHANGED_IDS: app_id
            }
            results = (
                Results(
                    active_user, uri, method
                ).something_broke(**data)
            )
            logger.exception(e)
            self.set_status(results['http_status'])
            self.set_header('Content-Type', 'application/json')
            self.write(json.dumps(results, indent=4))

    @authenticated_request
    @convert_json_to_arguments
    @check_permissions(Permissions.INSTALL)
    def put(self, app_id):
        active_user = self.get_current_user().encode('utf-8')
        active_view = (
            UserManager(active_user).get_attribute(UserKeys.CurrentView)
        )
        self.get_and_set_install_arguments()
        self.app_ids = [app_id]
        self.agent_ids = self.arguments.get('agent_ids')
        install = (
            Install(
                self.app_ids, self.agent_ids, user_name=active_user,
                view_name=active_view, restart=self.restart,
                net_throttle=self.net_throttle, cpu_throttle=self.cpu_throttle
            )
        )
        operation = (
            StorePatchingOperation(active_user, active_view)
        )

        sched = self.application.scheduler
        job = AgentAppsJobManager(sched, active_view)
        results = (
            self.get_install_results(
                operation, install, active_user, job,
                AgentOperations.INSTALL_OS_APPS
            )
        )
        self.set_status(results['http_status'])
        self.set_header('Content-Type', 'application/json')
        self.write(json.dumps(results, indent=4))
        return results

    @authenticated_request
    @convert_json_to_arguments
    @check_permissions(Permissions.UNINSTALL)
    def delete(self, app_id):
        active_user = self.get_current_user().encode('utf-8')
        active_view = (
            UserManager(active_user).get_attribute(UserKeys.CurrentView)
        )
        self.get_and_set_install_arguments()
        self.app_ids = [app_id]
        self.agent_ids = self.arguments.get('agent_ids')
        install = (
            Install(
                self.app_ids, self.agent_ids, user_name=active_user,
                view_name=active_view, restart=self.restart,
                net_throttle=self.net_throttle, cpu_throttle=self.cpu_throttle
            )
        )
        operation = (
            StorePatchingOperation(active_user, active_view)
        )

        sched = self.application.scheduler
        job = AgentAppsJobManager(sched, active_view)
        results = (
            self.get_uninstall_results(
                operation, install, active_user, job
            )
        )
        self.set_status(results['http_status'])
        self.set_header('Content-Type', 'application/json')
        self.write(json.dumps(results, indent=4))
        return results


class GetAgentsByAppIdHandler(AppsBaseHandler):
    @authenticated_request
    def get(self, app_id):
        active_user = self.get_current_user().encode('utf-8')
        uri = self.request.uri
        http_method = self.request.method
        query = (
            self.get_argument(ApiArguments.QUERY, None)
        )
        count = (
            int(
                self.get_argument(
                    ApiArguments.COUNT, DefaultQueryValues.COUNT
                )
            )
        )
        offset = (
            int(
                self.get_argument(
                    ApiArguments.OFFSET, DefaultQueryValues.OFFSET
                )
            )
        )
        sort = (
            self.get_argument(
                ApiArguments.SORT, SortValues.ASC
            )
        )
        sort_by = (
            self.get_argument(ApiArguments.SORT_BY, AgentKeys.ComputerName)
        )
        status = (
            self.get_argument(
                AppApiArguments.STATUS, AppStatuses.AVAILABLE
            )
        )
        search = (
            RetrieveAgentsByAppId(app_id, count, offset, sort, sort_by)
        )
        output = self.get_argument(ApiArguments.OUTPUT, 'json')

        if status and not query:
            results = self.by_status(search, status)

        elif status and query:
            results = self.by_status_and_name(search, status, query)

        elif query and not status:
            results = self.by_name(search, query)

        else:
            results = (
                Results(
                    active_user, uri, http_method
                ).incorrect_arguments()
            )

        self.set_status(results['http_status'])
        self.modified_output(results, output, 'apps')

    @results_message
    def by_status(self, search, status):
        results = search.by_status(status)
        return results

    @results_message
    def by_name(self, search, name):
        results = search.by_name(name)
        return results

    @results_message
    def by_status_and_name(self, search, status, name):
        results = search.by_status_and_name(status, name)
        return results


    @authenticated_request
    @convert_json_to_arguments
    @check_permissions(Permissions.INSTALL)
    def put(self, app_id):
        active_user = self.get_current_user().encode('utf-8')
        active_view = (
            UserManager(active_user).get_attribute(UserKeys.CurrentView)
        )
        self.get_and_set_install_arguments()
        self.app_ids = [app_id]
        self.agent_ids = self.arguments.get('agent_ids')
        install = (
            Install(
                self.app_ids, self.agent_ids, user_name=active_user,
                view_name=active_view, restart=self.restart,
                net_throttle=self.net_throttle, cpu_throttle=self.cpu_throttle
            )
        )
        operation = (
            StorePatchingOperation(active_user, active_view)
        )

        sched = self.application.scheduler
        job = AgentAppsJobManager(sched, active_view)
        results = (
            self.get_install_results(
                operation, install, active_user, job,
                AgentOperations.INSTALL_OS_APPS
            )
        )
        self.set_status(results['http_status'])
        self.set_header('Content-Type', 'application/json')
        self.write(json.dumps(results, indent=4))
        return results


    @authenticated_request
    @convert_json_to_arguments
    @check_permissions(Permissions.UNINSTALL)
    def delete(self, app_id):
        active_user = self.get_current_user().encode('utf-8')
        active_view = (
            UserManager(active_user).get_attribute(UserKeys.CurrentView)
        )
        self.get_and_set_install_arguments()
        self.app_ids = [app_id]
        self.agent_ids = self.arguments.get('agent_ids')
        install = (
            Install(
                self.app_ids, self.agent_ids, user_name=active_user,
                view_name=active_view, restart=self.restart,
                net_throttle=self.net_throttle, cpu_throttle=self.cpu_throttle
            )
        )
        operation = (
            StorePatchingOperation(active_user, active_view)
        )

        sched = self.application.scheduler
        job = AgentAppsJobManager(sched, active_view)
        results = (
            self.get_uninstall_results(
                operation, install, active_user, job
            )
        )
        self.set_status(results['http_status'])
        self.set_header('Content-Type', 'application/json')
        self.write(json.dumps(results, indent=4))
        return results


class OsAppsHandler(AppsBaseHandler):
    @authenticated_request
    def get(self):
        active_user = self.get_current_user().encode('utf-8')
        active_view = (
            UserManager(active_user).get_attribute(UserKeys.CurrentView)
        )
        self.get_and_set_search_arguments()
        search = (
            RetrieveApps(
                active_view, self.count, self.offset,
                self.sort, self.sort_by, show_hidden=self.hidden
            )
        )
        if (not self.query and not self.severity and not self.vuln
                and not self.status):
            results = self.all(search)

        else:
            results = self.app_search_results(search, active_user)

        self.set_status(results['http_status'])
        self.modified_output(results, self.output, 'apps')

    @results_message
    def all(self, search):
        results = search.all()
        return results


    @authenticated_request
    @convert_json_to_arguments
    @check_permissions(Permissions.ADMINISTRATOR)
    def put(self):
        active_user = self.get_current_user().encode('utf-8')
        uri = self.request.uri
        method = self.request.method

        try:
            app_ids = self.arguments.get('app_ids')
            toggle = self.arguments.get('hide', 'toggle')
            results = (
                toggle_hidden_status(
                    app_ids, toggle,
                    active_user=active_user, uri=uri, method=method
                )
            )

            self.set_status(results['http_status'])
            self.set_header('Content-Type', 'application/json')
            self.write(json.dumps(results, indent=4))

        except Exception as e:
            logger.exception(e)
            results = (
                Results(
                    active_user, uri, method
                ).something_broke(app_ids, 'toggle hidden on os_apps', e)
            )

            self.set_status(results['http_status'])
            self.set_header('Content-Type', 'application/json')
            self.write(json.dumps(results, indent=4))
