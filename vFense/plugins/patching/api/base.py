import logging
import logging.config

from vFense._constants import VFENSE_LOGGING_CONFIG
from vFense.core.api.base import BaseHandler
from vFense.core.decorators import results_message, api_catch_it
from vFense.core.api._constants import ApiArguments
from vFense.plugins.patching.api._constants import AppApiArguments
from vFense.core._constants import DefaultQueryValues, SortValues
from vFense.core.operations._constants import AgentOperations
from vFense.core.results import ApiResults, ExternalApiResults
from vFense.core.status_codes import GenericCodes
from vFense.core._constants import CommonKeys
from vFense.core.permissions._constants import Permissions
from vFense.core.permissions.decorators import check_permissions
from vFense.plugins.patching._db_model import AppsKey, AppCollections
from vFense.plugins.patching.api._constants import vFenseAppTypes
from vFense.plugins.patching.scheduler.manager import (
    AgentAppsJobManager, TagAppsJobManager
)
from vFense.plugins.patching._constants import AppStatuses
from vFense.plugins.patching.search.search_by_agentid import (
    RetrieveAppsByAgentId, RetrieveCustomAppsByAgentId,
    RetrieveSupportedAppsByAgentId, RetrieveAgentAppsByAgentId
)

from vFense.plugins.patching.search.search_by_tagid import (
    RetrieveAppsByTagId, RetrieveCustomAppsByTagId,
    RetrieveSupportedAppsByTagId, RetrieveAgentAppsByTagId
)
from vFense.plugins.patching.search.search import (
    RetrieveApps, RetrieveCustomApps, RetrieveSupportedApps,
    RetrieveAgentApps
)
from vFense.plugins.patching.patching import toggle_hidden_status

logging.config.fileConfig(VFENSE_LOGGING_CONFIG)
logger = logging.getLogger('vfense_api')

class AppsBaseHandler(BaseHandler):

    def get_and_set_search_arguments(self):
        self.query = (
            self.get_argument(ApiArguments.QUERY, None)
        )
        self.count = (
            int(
                self.get_argument(
                    ApiArguments.COUNT, DefaultQueryValues.COUNT
                )
            )
        )
        self.offset = (
            int(
                self.get_argument(
                    ApiArguments.OFFSET, DefaultQueryValues.OFFSET
                )
            )
        )
        self.sort = (
            self.get_argument(ApiArguments.SORT, SortValues.ASC)
        )
        self.sort_by = self.get_argument(ApiArguments.SORT_BY, AppsKey.Name)
        self.status = (
            self.get_argument(
                AppApiArguments.STATUS, AppStatuses.AVAILABLE
            )
        )
        self.severity = self.get_argument(AppApiArguments.SEVERITY, None)
        self.vuln = self.get_argument(AppApiArguments.VULN, None)
        self.hidden = self.get_argument(AppApiArguments.HIDDEN, 'false')
        self.output = self.get_argument(AppApiArguments.OUTPUT, 'json')

        if self.hidden == 'false':
            self.hidden = CommonKeys.NO
        else:
            self.hidden = CommonKeys.YES

    def app_search_results(self, search, active_user):
        if (not self.query and not self.severity and not self.vuln
                and self.status):
            results = self.by_status(search)

        elif (not self.query and not self.vuln and self.status
              and self.severity):
            results = self.by_status_and_sev(search)

        elif (not self.query and not self.severity and self.status
              and self.vuln):
            results = self.by_status_and_vuln(search)

        elif (not self.query and not self.status and not self.vuln
              and self.severity):
            results = self.by_severity(search)

        elif not self.vuln and self.severity and self.status and self.query:
            results = self.by_status_and_name_and_sev(search)

        elif self.vuln and self.severity and self.status and self.query:
            results = (
                self.by_status_and_name_and_sev_and_vuln(search)
            )

        elif (not self.vuln and not self.severity and self.status
              and self.query):
            results = self.by_status_and_name(search)

        elif not self.severity and self.status and self.query and self.vuln:
            results = self.by_status_and_name_and_vuln(search)

        elif (self.severity and self.query and not self.status
              and not self.vuln):
            results = self.by_sev_and_name(search)

        elif (not self.vuln and not self.severity and not self.status
              and self.query):
            results = self.by_name(search)

        else:
            results = ExternalApiResults()
            results.fill_in_defaults()
            results.message = (
                'Incorrect arguments while searching for applications'
            )
            results.username = active_user
            results.uri = self.request.uri
            results.http_method = self.request.method
            results.http_status_code = 400
            results.generic_status_code = GenericCodes.IncorrectArguments
            results.vfense_status_code = GenericCodes.IncorrectArguments

        return results

    @results_message
    def by_name(self, search):
        print 'by_name'
        results = search.by_name(self.query)
        return results

    @results_message
    def by_status(self, search):
        print 'by_status', search
        results = search.by_status(self.status)
        return results

    @results_message
    def by_status_and_sev(self, search):
        print 'by_status_and_sev'
        results = search.by_status_and_sev(self.status, self.sev)
        return results

    @results_message
    def by_sev_and_name(self, search):
        print 'by_status_and_name'
        results = search.by_sev_and_name(self.sev, self.query)
        return results

    @results_message
    def by_status_and_vuln(self, search):
        print 'by_status_and_vuln'
        results = search.by_status_and_vuln(self.status)
        return results

    @results_message
    def by_severity(self, search):
        print 'by_severity'
        results = search.by_severity(self.sev)
        return results

    @results_message
    def by_status_and_name_and_sev(self, search):
        print 'by_status_and_name_and_sev'
        results = search.by_status_and_name_and_sev(
            self.status, self.query, self.sev
        )
        return results

    @results_message
    def by_status_and_name_and_sev_and_vuln(self, search):
        print 'by_status_and_name_and_sev_and_vuln'
        results = (
            search.by_status_and_name_and_sev_and_vuln(
                self.status, self.query, self.sev
            )
        )
        return results

    @results_message
    def by_status_and_name(self, search):
        print 'by_status_and_name'
        results = search.by_status_and_name(self.status, self.query)
        return results

    @results_message
    def by_status_and_name_and_vuln(self, search):
        print 'by_status_and_name_and_vuln'
        results = search.by_status_and_name_and_vuln(self.status, self.query)
        return results

    def get_and_set_install_arguments(self):
        self.run_date = self.arguments.get('run_date', None)
        self.job_name = self.arguments.get('job_name', None)
        self.restart = self.arguments.get('restart', 'none')
        self.cpu_throttle = self.arguments.get('cpu_throttle', 'normal')
        self.net_throttle = self.arguments.get('net_throttle', 0)
        self.time_zone = self.arguments.get('time_zone', None)


    @results_message
    @check_permissions(Permissions.INSTALL)
    def get_install_results(self, operation, install, active_user,
                            job, oper=AgentOperations.INSTALL_OS_APPS):
        return self.get_install_or_uninstall_results(
            operation, install, active_user, job, oper
        )

    @results_message
    @check_permissions(Permissions.INSTALL)
    def get_uninstall_results(self, operation, install, active_user,
                              job, oper=AgentOperations.UNINSTALL):
        return self.get_install_or_uninstall_results(
            operation, install, active_user, job, oper
        )

    def install_or_uninstall(self, operation, install,
                             oper=AgentOperations.INSTALL_OS_APPS):

        results = ApiResults()

        if oper == AgentOperations.INSTALL_OS_APPS:
            results = operation.install_os_apps(install)

        elif oper == AgentOperations.INSTALL_CUSTOM_APPS:
            results = operation.install_custom_apps(install)

        elif oper == AgentOperations.INSTALL_SUPPORTED_APPS:
            results = operation.install_supported_apps(install)

        elif oper == AgentOperations.INSTALL_AGENT_UPDATE:
            results = operation.install_supported_apps(install)

        elif oper == AgentOperations.UNINSTALL:
            results = operation.uninstall_apps(install)

        return results


    def schedule_install_or_uninstall(self, job, install,
                                      oper=AgentOperations.INSTALL_OS_APPS):

        results = job.once(
            install, self.run_date, self.job_name, self.time_zone, oper
        )
        return results


    def get_install_or_uninstall_results(self, operation, install,
                                         active_user, job, oper):

        if not self.run_date and not self.job_name:
            results = self.install_or_uninstall(operation, install, oper)

        elif self.run_date and self.job_name:
            if not isinstance(self.run_date, float):
                run_date = float(self.run_date)

            results = (
                self.schedule_install_or_uninstall(
                    job, install, run_date, self.job_name,
                    self.time_zone, oper
                )
            )

        else:
            results = ExternalApiResults()
            results.fill_in_defaults()
            results.message = (
                'Incorrect arguments while searching for applications'
            )
            results.username = active_user
            results.uri = self.request.uri
            results.http_method = self.request.method
            results.http_status_code = 400
            results.generic_status_code = GenericCodes.IncorrectArguments
            results.vfense_status_code = GenericCodes.IncorrectArguments

        return results

    def set_search_for_agent(self, oper, agent_id):
        if oper == AgentOperations.INSTALL_OS_APPS:
            search = (
                RetrieveAppsByAgentId(
                    agent_id=agent_id, count=self.count, offset=self.offset,
                    sort=self.sort, sort_key=self.sort_by,
                    show_hidden=self.hidden
                )
            )

        elif oper == AgentOperations.INSTALL_CUSTOM_APPS:
            search = (
                RetrieveCustomAppsByAgentId(
                    agent_id=agent_id, count=self.count, offset=self.offset,
                    sort=self.sort, sort_key=self.sort_by,
                    show_hidden=self.hidden
                )
            )

        elif oper == AgentOperations.INSTALL_SUPPORTED_APPS:
            search = (
                RetrieveSupportedAppsByAgentId(
                    agent_id=agent_id, count=self.count, offset=self.offset,
                    sort=self.sort, sort_key=self.sort_by,
                    show_hidden=self.hidden
                )
            )

        elif oper == AgentOperations.INSTALL_AGENT_UPDATE:
            search = (
                RetrieveAgentAppsByAgentId(
                    agent_id=agent_id, count=self.count, offset=self.offset,
                    sort=self.sort, sort_key=self.sort_by,
                    show_hidden=self.hidden
                )
            )

        return search

    def set_search_for_tag(self, oper, tag_id):
        if oper == AgentOperations.INSTALL_OS_APPS:
            search = (
                RetrieveAppsByTagId(
                    tag_id=tag_id, count=self.count, offset=self.offset,
                    sort=self.sort, sort_key=self.sort_by,
                    show_hidden=self.hidden
                )
            )

        elif oper == AgentOperations.INSTALL_CUSTOM_APPS:
            search = (
                RetrieveCustomAppsByTagId(
                    tag_id=tag_id, count=self.count, offset=self.offset,
                    sort=self.sort, sort_key=self.sort_by,
                    show_hidden=self.hidden
                )
            )

        elif oper == AgentOperations.INSTALL_SUPPORTED_APPS:
            search = (
                RetrieveSupportedAppsByTagId(
                    tag_id=tag_id, count=self.count, offset=self.offset,
                    sort=self.sort, sort_key=self.sort_by,
                    show_hidden=self.hidden
                )
            )

        elif oper == AgentOperations.INSTALL_AGENT_UPDATE:
            search = (
                RetrieveAgentAppsByTagId(
                    tag_id=tag_id, count=self.count, offset=self.offset,
                    sort=self.sort, sort_key=self.sort_by,
                    show_hidden=self.hidden
                )
            )

        return search

    def set_base_search(self, oper, view_name):
        if oper == AgentOperations.INSTALL_OS_APPS:
            search = (
                RetrieveApps(
                    view_name=view_name, count=self.count, offset=self.offset,
                    sort=self.sort, sort_key=self.sort_by,
                    show_hidden=self.hidden
                )
            )

        elif oper == AgentOperations.INSTALL_CUSTOM_APPS:
            search = (
                RetrieveCustomApps(
                    view_name=view_name, count=self.count, offset=self.offset,
                    sort=self.sort, sort_key=self.sort_by,
                    show_hidden=self.hidden
                )
            )

        elif oper == AgentOperations.INSTALL_SUPPORTED_APPS:
            search = (
                RetrieveSupportedApps(
                    view_name=view_name, count=self.count, offset=self.offset,
                    sort=self.sort, sort_key=self.sort_by,
                    show_hidden=self.hidden
                )
            )

        elif oper == AgentOperations.INSTALL_AGENT_UPDATE:
            search = (
                RetrieveAgentApps(
                    view_name=view_name, count=self.count, offset=self.offset,
                    sort=self.sort, sort_key=self.sort_by,
                    show_hidden=self.hidden
                )
            )

        return search

    def return_operation_type(self, oper):
        return vFenseAppTypes.return_app_operation(oper)

    @results_message
    def set_toggle_status(self, oper):
        if oper == AgentOperations.INSTALL_OS_APPS:
            results = toggle_hidden_status(self.app_ids, self.toggle)

        elif oper == AgentOperations.INSTALL_CUSTOM_APPS:
            results = (
                toggle_hidden_status(
                    self.app_ids, self.toggle,
                    collection=AppCollections.CustomApps
                )
            )

        elif oper == AgentOperations.INSTALL_SUPPORTED_APPS:
            results = (
                toggle_hidden_status(
                    self.app_ids, self.toggle,
                    collection=AppCollections.SupportedApps
                )
            )

        elif oper == AgentOperations.INSTALL_AGENT_UPDATE:
            results = (
                toggle_hidden_status(
                    self.app_ids, self.toggle,
                    collection=AppCollections.vFenseApps
                )
            )

        return results
