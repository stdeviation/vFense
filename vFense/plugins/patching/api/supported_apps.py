import simplejson as json
import logging
import logging.config
from vFense import VFENSE_LOGGING_CONFIG

from datetime import datetime

from vFense.core._constants import CommonKeys
from vFense.core.api.base import BaseHandler
from vFense.core.permissions._constants import Permissions
from vFense.core.permissions.decorators import check_permissions
from vFense.core.decorators import (
    authenticated_request, convert_json_to_arguments, results_message
)

from vFense.core.results import Results, PackageResults

#from vFense.scheduler.jobManager import schedule_once

from vFense.plugins.patching.operations.store_operations import (
    StorePatchingOperation
)
from vFense.core.agent._db_model import AgentKeys
from vFense.plugins.patching._db_model import AppsKey
from vFense.plugins.patching._db import update_app_data_by_app_id
from vFense.plugins.patching.patching import toggle_hidden_status

from vFense.plugins.patching.search.search import (
    RetrieveSupportedApps
)
from vFense.plugins.patching.search.search_by_agentid import (
    RetrieveSupportedAppsByAgentId
)
from vFense.plugins.patching.search.search_by_tagid import (
    RetrieveSupportedAppsByTagId
)
from vFense.plugins.patching.search.search_by_appid import (
    RetrieveAgentsBySupportedAppId
)

from vFense.core.user import UserKeys
from vFense.core.user.manager import UserManager

from vFense.core.api._constants import ApiArguments
from vFense.core._constants import DefaultQueryValues, SortValues
from vFense.plugins.patching.api._constants import (
    AppApiArguments, AppFilterValues
)
from vFense.plugins.patching._constants import (
    AppStatuses, CommonSeverityKeys
)

logging.config.fileConfig(VFENSE_LOGGING_CONFIG)
logger = logging.getLogger('rvapi')


class AgentIdSupportedAppsHandler(BaseHandler):
    @authenticated_request
    def get(self, agent_id):
        uri = self.request.uri
        http_method = self.request.method
        username = self.get_current_user().encode('utf-8')
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
        sort_by = self.get_argument(ApiArguments.SORT_BY, AppsKey.Name)
        status = (
            self.get_argument(
                AppApiArguments.STATUS, AppStatuses.AVAILABLE
            )
        )
        severity = self.get_argument(AppApiArguments.SEVERITY, None)
        vuln = self.get_argument(AppApiArguments.VULN, None)
        hidden = self.get_argument(AppApiArguments.HIDDEN, 'false')

        if hidden == 'false':
            hidden = CommonKeys.NO
        else:
            hidden = CommonKeys.YES
        search = (
            RetrieveSupportedAppsByAgentId(
                agent_id, count, offset,
                sort, sort_by, show_hidden=hidden
            )
        )
        if not query and not severity and not vuln and status:
            results = self.by_status(search, status)

        elif not query and not vuln and status and severity:
            results = self.by_status_and_sev(search, status, severity)

        elif not query and not severity and status and vuln:
            results = self.by_status_and_vuln(search, status)

        elif not query and not status and not vuln and severity:
            results = self.by_severity(search, severity)

        elif not vuln and severity and status and query:
            results = (
                self.by_status_and_name_and_sev(
                    search, query, status, severity
                )
            )

        elif vuln and severity and status and query:
            results = (
                self.by_status_and_name_and_sev_and_vuln(
                    search, query, status, severity
                )
            )

        elif not vuln and not severity and status and query:
            results = (
                self.by_status_and_name(search, query, status)
            )

        elif not severity and status and query and vuln:
            results = (
                self.by_status_and_name_and_vuln(search, query, status)
            )

        elif severity and query and not status and not vuln:
            results = (
                self.by_sev_and_name(
                    search, query, severity
                )
            )

        elif not vuln and not severity and not status and query:
            results = self.by_name(search, query)

        else:
            results = (
                Results(
                    username, uri, http_method
                ).incorrect_arguments()
            )

        self.set_status(results['http_status'])
        self.set_header('Content-Type', 'application/json')
        self.write(json.dumps(results, indent=4))

    @results_message
    def by_name(self, search, name):
        results = search.by_name(name)
        return results

    @results_message
    def by_status(self, search, status):
        results = search.by_status(status)
        return results

    @results_message
    def by_status_and_sev(self, search, status, sev):
        results = search.by_status_and_sev(status, sev)
        return results

    @results_message
    def by_sev_and_name(self, search, sev, name):
        results = search.by_sev_and_name(sev, name)
        return results

    @results_message
    def by_status_and_vuln(self, search, status):
        results = search.by_status_and_vuln(status)
        return results

    @results_message
    def by_severity(self, search, sev):
        results = search.by_severity(sev)
        return results

    @results_message
    def by_status_and_name_and_sev(self, search, status, name, sev):
        results = search.by_status_and_name_and_sev(status, name, sev)
        return results

    @results_message
    def by_status_and_name_and_sev_and_vuln(self, search, status, name, sev):
        results = (
            search.by_status_and_name_and_sev_and_vuln(status, name, sev)
        )
        return results

    @results_message
    def by_status_and_name(self, search, status, name):
        results = search.by_status_and_name(status, name)
        return results

    @results_message
    def by_status_and_name_and_vuln(self, search, status, name):
        results = search.by_status_and_name_and_vuln(status, name)
        return results

    @authenticated_request
    @convert_json_to_arguments
    @check_permissions(Permissions.INSTALL)
    def put(self, agent_id):
        username = self.get_current_user().encode('utf-8')
        view_name = (
            UserManager(username).get_attribute(UserKeys.CurrentView)
        )
        uri = self.request.uri
        method = self.request.method
        try:
            app_ids = self.arguments.get('app_ids')
            epoch_time = self.arguments.get('time', None)
            label = self.arguments.get('label', None)
            restart = self.arguments.get('restart', 'none')
            cpu_throttle = self.arguments.get('cpu_throttle', 'normal')
            net_throttle = self.arguments.get('net_throttle', 0)
            if not epoch_time and not label and app_ids:
                operation = (
                    StorePatchingOperation(
                        username, view_name
                    )
                )
                results = (
                    operation.install_supported_apps(
                        app_ids, cpu_throttle,
                        net_throttle, restart,
                        agentids=[agent_id]
                    )
                )
                self.set_status(results['http_status'])
                self.set_header('Content-Type', 'application/json')
                self.write(json.dumps(results, indent=4))

            elif epoch_time and label and app_ids:
                date_time = datetime.fromtimestamp(int(epoch_time))
                sched = self.application.scheduler
                job = (
                    {
                        'cpu_throttle': cpu_throttle,
                        'net_throttle': net_throttle,
                        'pkg_type': 'supported_apps',
                        'restart': restart,
                        'app_ids': app_ids
                    }
                )
                add_install_job = (
                    schedule_once(
                        sched, view_name, username,
                        [agent_id], operation='install',
                        name=label, date=date_time, uri=uri,
                        method=method, job_extra=job
                    )
                )
                result = add_install_job
                self.set_header('Content-Type', 'application/json')
                self.write(json.dumps(result))

        except Exception as e:
            results = (
                Results(
                    username, uri, method
                ).something_broke(agent_id, 'install_supported_apps', e)
            )
            logger.exception(e)
            self.set_status(results['http_status'])
            self.set_header('Content-Type', 'application/json')
            self.write(json.dumps(results, indent=4))


    @authenticated_request
    @convert_json_to_arguments
    @check_permissions(Permissions.UNINSTALL)
    def delete(self, agent_id):
        username = self.get_current_user().encode('utf-8')
        view_name = (
            UserManager(username).get_attribute(UserKeys.CurrentView)
        )
        uri = self.request.uri
        method = self.request.method
        try:
            app_ids = self.arguments.get('app_ids')
            epoch_time = self.arguments.get('time', None)
            label = self.arguments.get('label', None)
            restart = self.arguments.get('restart', 'none')
            cpu_throttle = self.arguments.get('cpu_throttle', 'normal')
            net_throttle = self.arguments.get('net_throttle', 0)
            if not epoch_time and not label and app_ids:
                operation = (
                    StorePatchingOperation(
                        username, view_name
                    )
                )
                results = (
                    operation.uninstall_apps(
                        app_ids, cpu_throttle,
                        net_throttle, restart,
                        agentids=[agent_id]
                    )
                )
                self.set_status(results['http_status'])
                self.set_header('Content-Type', 'application/json')
                self.write(json.dumps(results, indent=4))

            elif epoch_time and label and app_ids:
                date_time = datetime.fromtimestamp(int(epoch_time))
                sched = self.application.scheduler
                job = (
                    {
                        'restart': restart,
                        'pkg_type': 'supported_apps',
                        'app_ids': app_ids
                    }
                )
                add_uninstall_job = (
                    schedule_once(
                        sched, view_name, username,
                        [agent_id], operation='uninstall',
                        name=label, date=date_time, uri=uri,
                        method=method, job_extra=job
                    )
                )
                result = add_uninstall_job
                self.set_header('Content-Type', 'application/json')
                self.write(json.dumps(result))

        except Exception as e:
            results = (
                Results(
                    username, uri, method
                ).something_broke(agent_id, 'install_supported_apps', e)
            )
            logger.exception(e)
            self.set_status(results['http_status'])
            self.set_header('Content-Type', 'application/json')
            self.write(json.dumps(results, indent=4))


class TagIdSupportedAppsHandler(BaseHandler):
    @authenticated_request
    def get(self, tag_id):
        username = self.get_current_user().encode('utf-8')
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
        sort_by = self.get_argument(ApiArguments.SORT_BY, AppsKey.Name)
        status = (
            self.get_argument(
                AppApiArguments.STATUS, AppStatuses.AVAILABLE
            )
        )
        severity = self.get_argument(AppApiArguments.SEVERITY, None)
        vuln = self.get_argument(AppApiArguments.VULN, None)
        hidden = self.get_argument(AppApiArguments.HIDDEN, 'false')

        if hidden == 'false':
            hidden = CommonKeys.NO
        else:
            hidden = CommonKeys.YES

        search = (
            RetrieveSupportedAppsByTagId(
                tag_id, count, offset, sort, sort_by, show_hidden=hidden
            )
        )
        if not query and not severity and not vuln and status:
            results = self.by_status(search, status)

        elif not query and not vuln and status and severity:
            results = self.by_status_and_sev(search, status, severity)

        elif not query and not severity and status and vuln:
            results = self.by_status_and_vuln(search, status)

        elif not query and not status and not vuln and severity:
            results = self.by_severity(search, severity)

        elif not vuln and severity and status and query:
            results = (
                self.by_status_and_name_and_sev(
                    search, query, status, severity
                )
            )

        elif vuln and severity and status and query:
            results = (
                self.by_status_and_name_and_sev_and_vuln(
                    search, query, status, severity
                )
            )

        elif not vuln and not severity and status and query:
            results = (
                self.by_status_and_name(search, query, status)
            )

        elif not severity and status and query and vuln:
            results = (
                self.by_status_and_name_and_vuln(search, query, status)
            )

        elif severity and query and not status and not vuln:
            results = (
                self.by_sev_and_name(
                    search, query, severity
                )
            )

        elif not vuln and not severity and not status and query:
            results = self.by_name(search, query)

        else:
            results = (
                Results(
                    username, uri, http_method
                ).incorrect_arguments()
            )

        self.set_status(results['http_status'])
        self.set_header('Content-Type', 'application/json')
        self.write(json.dumps(results, indent=4))

    @results_message
    def by_name(self, search, name):
        results = search.by_name(name)
        return results

    @results_message
    def by_status(self, search, status):
        results = search.by_status(status)
        return results

    @results_message
    def by_status_and_sev(self, search, status, sev):
        results = search.by_status_and_sev(status, sev)
        return results

    @results_message
    def by_sev_and_name(self, search, sev, name):
        results = search.by_sev_and_name(sev, name)
        return results

    @results_message
    def by_status_and_vuln(self, search, status):
        results = search.by_status_and_vuln(status)
        return results

    @results_message
    def by_severity(self, search, sev):
        results = search.by_severity(sev)
        return results

    @results_message
    def by_status_and_name_and_sev(self, search, status, name, sev):
        results = search.by_status_and_name_and_sev(status, name, sev)
        return results

    @results_message
    def by_status_and_name_and_sev_and_vuln(self, search, status, name, sev):
        results = (
            search.by_status_and_name_and_sev_and_vuln(status, name, sev)
        )
        return results

    @results_message
    def by_status_and_name(self, search, status, name):
        results = search.by_status_and_name(status, name)
        return results

    @results_message
    def by_status_and_name_and_vuln(self, search, status, name):
        results = search.by_status_and_name_and_vuln(status, name)
        return results

    @authenticated_request
    @convert_json_to_arguments
    @check_permissions(Permissions.INSTALL)
    def put(self, tag_id):
        username = self.get_current_user().encode('utf-8')
        view_name = (
            UserManager(username).get_attribute(UserKeys.CurrentView)
        )
        uri = self.request.uri
        method = self.request.method
        try:
            app_ids = self.arguments.get('app_ids')
            epoch_time = self.arguments.get('time', None)
            label = self.arguments.get('label', None)
            restart = self.arguments.get('restart', 'none')
            cpu_throttle = self.arguments.get('cpu_throttle', 'normal')
            net_throttle = self.arguments.get('net_throttle', 0)
            if not epoch_time and not label and app_ids:
                operation = (
                    StorePatchingOperation(
                        username, view_name
                    )
                )
                results = (
                    operation.install_supported_apps(
                        app_ids, cpu_throttle,
                        net_throttle, restart,
                        tag_id=tag_id
                    )
                )
                self.set_status(results['http_status'])
                self.set_header('Content-Type', 'application/json')
                self.write(json.dumps(results, indent=4))

            elif epoch_time and label and app_ids:
                date_time = datetime.fromtimestamp(int(epoch_time))
                sched = self.application.scheduler
                job = (
                    {
                        'cpu_throttle': cpu_throttle,
                        'net_throttle': net_throttle,
                        'pkg_type': 'supported_apps',
                        'restart': restart,
                        'app_ids': app_ids
                    }
                )
                add_install_job = (
                    schedule_once(
                        sched, view_name, username,
                        tag_ids=[tag_id], operation='install',
                        name=label, date=date_time, uri=uri,
                        method=method, job_extra=job
                    )
                )
                result = add_install_job
                self.set_header('Content-Type', 'application/json')
                self.write(json.dumps(result))

        except Exception as e:
            results = (
                Results(
                    username, uri, method
                ).something_broke(tag_id, 'install_supported_apps', e)
            )
            logger.exception(e)
            self.set_status(results['http_status'])
            self.set_header('Content-Type', 'application/json')
            self.write(json.dumps(results, indent=4))

    @authenticated_request
    @convert_json_to_arguments
    @check_permissions(Permissions.UNINSTALL)
    def delete(self, tag_id):
        username = self.get_current_user().encode('utf-8')
        view_name = (
            UserManager(username).get_attribute(UserKeys.CurrentView)
        )
        uri = self.request.uri
        method = self.request.method
        try:
            app_ids = self.arguments.get('app_ids')
            epoch_time = self.arguments.get('time', None)
            label = self.arguments.get('label', None)
            restart = self.arguments.get('restart', 'none')
            cpu_throttle = self.arguments.get('cpu_throttle', 'normal')
            net_throttle = self.arguments.get('net_throttle', 0)
            if not epoch_time and not label and app_ids:
                operation = (
                    StorePatchingOperation(
                        username, view_name
                    )
                )
                results = (
                    operation.uninstall_apps(
                        app_ids, cpu_throttle,
                        net_throttle, restart,
                        tag_id=tag_id
                    )
                )
                self.set_status(results['http_status'])
                self.set_header('Content-Type', 'application/json')
                self.write(json.dumps(results, indent=4))

            elif epoch_time and label and app_ids:
                date_time = datetime.fromtimestamp(int(epoch_time))
                sched = self.application.scheduler
                job = (
                    {
                        'restart': restart,
                        'pkg_type': 'supported_apps',
                        'app_ids': app_ids
                    }
                )
                add_uninstall_job = (
                    schedule_once(
                        sched, view_name, username,
                        tag_ids=[tag_id], operation='uninstall',
                        name=label, date=date_time, uri=uri,
                        method=method, job_extra=job
                    )
                )
                result = add_uninstall_job
                self.set_header('Content-Type', 'application/json')
                self.write(json.dumps(result))

        except Exception as e:
            results = (
                Results(
                    username, uri, method
                ).something_broke(tag_id, 'install_supported_apps', e)
            )
            logger.exception(e)
            self.set_status(results['http_status'])
            self.set_header('Content-Type', 'application/json')
            self.write(json.dumps(results, indent=4))


class AppIdSupportedAppsHandler(BaseHandler):
    @authenticated_request
    def get(self, app_id):
        username = self.get_current_user().encode('utf-8')
        active_view = (
            UserManager(username).get_attribute(UserKeys.CurrentView)
        )
        search = RetrieveSupportedApps(active_view)
        results = self.by_id(search, app_id)
        self.set_status(results['http_status'])
        self.set_header('Content-Type', 'application/json')
        self.write(json.dumps(results, indent=4))

    @results_message
    def by_id(self, search, app_id):
        results = search.by_id(app_id)
        return results

    @authenticated_request
    @convert_json_to_arguments
    @check_permissions(Permissions.ADMINISTRATOR)
    def post(self, app_id):
        username = self.get_current_user().encode('utf-8')
        view_name = (
            UserManager(username).get_attribute(UserKeys.CurrentView)
        )
        uri = self.request.uri
        method = self.request.method

        try:
            severity = self.arguments.get('severity').capitalize()

            if severity in CommonSeverityKeys.ValidRvSeverities:
                sev_data = {AppsKey.RvSeverity: severity}

                update_app_data_by_app_id(
                    app_id, sev_data, AppCollections.SupportedApps
                )

                results = Results(
                    username, uri, method
                ).object_updated(app_id, 'app severity', [sev_data])

                self.set_status(results['http_status'])
                self.set_header('Content-Type', 'application/json')
                self.write(json.dumps(results, indent=4))

            else:
                results = (
                    PackageResults(
                        username, uri, method
                    ).invalid_severity(severity)
                )
                self.set_status(results['http_status'])
                self.set_header('Content-Type', 'application/json')
                self.write(json.dumps(results, indent=4))

        except Exception as e:
            results = (
                Results(
                    username, uri, method
                ).something_broke(app_id, 'update_severity', e)
            )
            logger.exception(e)
            self.set_status(results['http_status'])
            self.set_header('Content-Type', 'application/json')
            self.write(json.dumps(results, indent=4))


    @authenticated_request
    @convert_json_to_arguments
    @check_permissions(Permissions.INSTALL)
    def put(self, app_id):
        username = self.get_current_user().encode('utf-8')
        view_name = (
            UserManager(username).get_attribute(UserKeys.CurrentView)
        )
        uri = self.request.uri
        method = self.request.method
        try:
            agent_ids = self.arguments.get('agent_ids')
            epoch_time = self.arguments.get('time', None)
            label = self.arguments.get('label', None)
            restart = self.arguments.get('restart', 'none')
            cpu_throttle = self.arguments.get('cpu_throttle', 'normal')
            net_throttle = self.arguments.get('net_throttle', 0)
            if not epoch_time and not label and app_id:
                operation = (
                    StorePatchingOperation(
                        username, view_name
                    )
                )
                results = (
                    operation.install_supported_apps(
                        [app_id], cpu_throttle,
                        net_throttle, restart,
                        agentids=agent_ids
                    )
                )
                self.set_status(results['http_status'])
                self.set_header('Content-Type', 'application/json')
                self.write(json.dumps(results, indent=4))

            elif epoch_time and label and agent_ids:
                date_time = datetime.fromtimestamp(int(epoch_time))
                sched = self.application.scheduler
                job = (
                    {
                        'operation': 'install',
                        'cpu_throttle': cpu_throttle,
                        'net_throttle': net_throttle,
                        'restart': restart,
                        'pkg_type': 'supported_apps',
                        'app_ids': [app_id]
                    }
                )
                add_install_job = (
                    schedule_once(
                        sched, view_name, username,
                        agent_ids=[agent_ids], operation='install',
                        name=label, date=date_time, uri=uri,
                        method=method, job_extra=job
                    )
                )
                result = add_install_job
                self.set_header('Content-Type', 'application/json')
                self.write(json.dumps(result))

        except Exception as e:
            results = (
                Results(
                    username, uri, method
                ).something_broke(app_id, 'install_supported_apps', e)
            )
            logger.exception(e)
            self.set_status(results['http_status'])
            self.set_header('Content-Type', 'application/json')
            self.write(json.dumps(results, indent=4))


    @authenticated_request
    @convert_json_to_arguments
    @check_permissions(Permissions.UNINSTALL)
    def delete(self, app_id):
        username = self.get_current_user().encode('utf-8')
        view_name = (
            UserManager(username).get_attribute(UserKeys.CurrentView)
        )
        uri = self.request.uri
        method = self.request.method
        try:
            agent_ids = self.arguments.get('agent_ids')
            epoch_time = self.arguments.get('time', None)
            label = self.arguments.get('label', None)
            restart = self.arguments.get('restart', 'none')
            cpu_throttle = self.arguments.get('cpu_throttle', 'normal')
            net_throttle = self.arguments.get('net_throttle', 0)
            if not epoch_time and not label and app_id:
                operation = (
                    StorePatchingOperation(
                        username, view_name
                    )
                )
                results = (
                    operation.uninstall_apps(
                        [app_id], cpu_throttle,
                        net_throttle, restart,
                        agentids=agent_ids
                    )
                )
                self.set_status(results['http_status'])
                self.set_header('Content-Type', 'application/json')
                self.write(json.dumps(results, indent=4))

            elif epoch_time and label and agent_ids:
                date_time = datetime.fromtimestamp(int(epoch_time))
                sched = self.application.scheduler
                job = (
                    {
                        'restart': restart,
                        'pkg_type': 'supported_apps',
                        'app_ids': [app_id]
                    }
                )
                add_install_job = (
                    schedule_once(
                        sched, view_name, username,
                        agent_ids=[agent_ids], operation='uninstall',
                        name=label, date=date_time, uri=uri,
                        method=method, job_extra=job
                    )
                )
                result = add_install_job
                self.set_header('Content-Type', 'application/json')
                self.write(json.dumps(result))

        except Exception as e:
            results = (
                Results(
                    username, uri, method
                ).something_broke(app_id, 'install_supported_apps', e)
            )
            logger.exception(e)
            self.set_status(results['http_status'])
            self.set_header('Content-Type', 'application/json')
            self.write(json.dumps(results, indent=4))


class GetAgentsBySupportedAppIdHandler(BaseHandler):
    @authenticated_request
    def get(self, app_id):
        username = self.get_current_user().encode('utf-8')
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
            RetrieveAgentsBySupportedAppId(
                app_id, count, offset, sort, sort_by
            )
        )

        if status and not query:
            results = self.by_status(search, status)

        elif status and query:
            results = self.by_status_and_name(search, status, query)

        elif query and not status:
            results = self.by_name(search, query)

        else:
            results = (
                Results(
                    username, uri, http_method
                ).incorrect_arguments()
            )

        self.set_status(results['http_status'])
        self.set_header('Content-Type', 'application/json')
        self.write(json.dumps(results, indent=4))

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
        username = self.get_current_user().encode('utf-8')
        view_name = (
            UserManager(username).get_attribute(UserKeys.CurrentView)
        )
        uri = self.request.uri
        method = self.request.method
        try:
            agent_ids = self.arguments.get('agent_ids')
            epoch_time = self.arguments.get('time', None)
            label = self.arguments.get('label', None)
            restart = self.arguments.get('restart', 'none')
            cpu_throttle = self.arguments.get('cpu_throttle', 'normal')
            net_throttle = self.arguments.get('net_throttle', 0)
            if not epoch_time and not label and app_id:
                operation = (
                    StorePatchingOperation(
                        username, view_name
                    )
                )
                results = (
                    operation.install_supported_apps(
                        [app_id], cpu_throttle,
                        net_throttle, restart,
                        agentids=agent_ids
                    )
                )
                self.set_status(results['http_status'])
                self.set_header('Content-Type', 'application/json')
                self.write(json.dumps(results, indent=4))

            elif epoch_time and label and agent_ids:
                date_time = datetime.fromtimestamp(int(epoch_time))
                sched = self.application.scheduler
                job = (
                    {
                        'cpu_throttle': cpu_throttle,
                        'net_throttle': net_throttle,
                        'pkg_type': 'supported_apps',
                        'restart': restart,
                        'app_ids': [app_id]
                    }
                )
                add_install_job = (
                    schedule_once(
                        sched, view_name, username,
                        agent_ids=agent_ids, operation='install',
                        name=label, date=date_time, uri=uri,
                        method=method, job_extra=job
                    )
                )
                result = add_install_job
                self.set_header('Content-Type', 'application/json')
                self.write(json.dumps(result))

        except Exception as e:
            results = (
                Results(
                    username, uri, method
                ).something_broke(app_id, 'install_supported_apps', e)
            )
            logger.exception(e)
            self.set_status(results['http_status'])
            self.set_header('Content-Type', 'application/json')
            self.write(json.dumps(results, indent=4))


    @authenticated_request
    @convert_json_to_arguments
    @check_permissions(Permissions.UNINSTALL)
    def delete(self, app_id):
        username = self.get_current_user().encode('utf-8')
        view_name = (
            UserManager(username).get_attribute(UserKeys.CurrentView)
        )
        uri = self.request.uri
        method = self.request.method
        try:
            agent_ids = self.arguments.get('agent_ids')
            epoch_time = self.arguments.get('time', None)
            label = self.arguments.get('label', None)
            restart = self.arguments.get('restart', 'none')
            cpu_throttle = self.arguments.get('cpu_throttle', 'normal')
            net_throttle = self.arguments.get('net_throttle', 0)
            if not epoch_time and not label and app_id:
                operation = (
                    StorePatchingOperation(
                        username, view_name
                    )
                )
                results = (
                    operation.uninstall_apps(
                        [app_id], cpu_throttle,
                        net_throttle, restart,
                        agentids=agent_ids
                    )
                )
                self.set_status(results['http_status'])
                self.set_header('Content-Type', 'application/json')
                self.write(json.dumps(results, indent=4))

            elif epoch_time and label and agent_ids:
                date_time = datetime.fromtimestamp(int(epoch_time))
                sched = self.application.scheduler
                job = (
                    {
                        'pkg_type': 'supported_apps',
                        'restart': restart,
                        'app_ids': [app_id]
                    }
                )
                add_uninstall_job = (
                    schedule_once(
                        sched, view_name, username,
                        agent_ids=agent_ids, operation='uninstall',
                        name=label, date=date_time, uri=uri,
                        method=method, job_extra=job
                    )
                )
                result = add_uninstall_job
                self.set_header('Content-Type', 'application/json')
                self.write(json.dumps(result))

        except Exception as e:
            results = (
                Results(
                    username, uri, method
                ).something_broke(app_id, 'install_supported_apps', e)
            )
            logger.exception(e)
            self.set_status(results['http_status'])
            self.set_header('Content-Type', 'application/json')
            self.write(json.dumps(results, indent=4))


class SupportedAppsHandler(BaseHandler):
    @authenticated_request
    def get(self):
        uri = self.request.uri
        http_method = self.request.method
        username = self.get_current_user().encode('utf-8')
        active_view = (
            UserManager(username).get_attribute(UserKeys.CurrentView)
        )
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
        sort_by = self.get_argument(ApiArguments.SORT_BY, AppsKey.Name)
        status = (
            self.get_argument(
                AppApiArguments.STATUS, AppStatuses.AVAILABLE
            )
        )
        severity = self.get_argument(AppApiArguments.SEVERITY, None)
        vuln = self.get_argument(AppApiArguments.VULN, None)
        hidden = self.get_argument(AppApiArguments.HIDDEN, 'false')

        if hidden == 'false':
            hidden = CommonKeys.NO
        else:
            hidden = CommonKeys.YES

        if sort_by == AppFilterValues.SEVERITY:
            sort_by = AppsKey.RvSeverity

        search = (
            RetrieveSupportedApps(
                active_view, count, offset,
                sort, sort_by, show_hidden=hidden
            )
        )
        if not query and not severity and not vuln and not status:
            results = self.all(search)

        if not query and not severity and not vuln and status:
            results = self.by_status(search, status)

        elif not query and not vuln and status and severity:
            results = self.by_status_and_sev(search, status, severity)

        elif not query and not severity and status and vuln:
            results = self.by_status_and_vuln(search, status)

        elif not query and not status and not vuln and severity:
            results = self.by_severity(search, severity)

        elif not vuln and severity and status and query:
            results = (
                self.by_status_and_name_and_sev(
                    search, query, status, severity
                )
            )

        elif vuln and severity and status and query:
            results = (
                self.by_status_and_name_and_sev_and_vuln(
                    search, query, status, severity
                )
            )

        elif not vuln and not severity and status and query:
            results = (
                self.by_status_and_name(search, query, status)
            )

        elif not severity and status and query and vuln:
            results = (
                self.by_status_and_name_and_vuln(search, query, status)
            )

        elif severity and query and not status and not vuln:
            results = (
                self.by_sev_and_name(
                    search, query, severity
                )
            )

        elif not vuln and not severity and not status and query:
            results = self.by_name(search, query)


        else:
            results = (
                Results(
                    username, uri, http_method
                ).incorrect_arguments()
            )

        self.set_status(results['http_status'])
        self.set_header('Content-Type', 'application/json')
        self.write(json.dumps(results, indent=4))

    @authenticated_request
    @convert_json_to_arguments
    @check_permissions(Permissions.ADMINISTRATOR)
    def put(self):
        username = self.get_current_user().encode('utf-8')
        uri = self.request.uri
        method = self.request.method
        try:
            app_ids = self.arguments.get('app_ids')
            toggle = self.arguments.get('hide', 'toggle')
            results = (
                toggle_hidden_status(
                    app_ids, toggle,
                    AppCollections.SupportedApps,
                    username, uri, method
                )
            )

            self.set_status(results['http_status'])
            self.set_header('Content-Type', 'application/json')
            self.write(json.dumps(results, indent=4))

        except Exception as e:
            logger.exception(e)
            results = (
                Results(
                    username, uri, method
                ).something_broke(app_ids, 'toggle hidden on supported_apps', e)
            )

            self.set_status(results['http_status'])
            self.set_header('Content-Type', 'application/json')
            self.write(json.dumps(results, indent=4))
