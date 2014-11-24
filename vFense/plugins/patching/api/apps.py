import logging
import logging.config
import simplejson as json

from vFense._constants import VFENSE_LOGGING_CONFIG

from vFense.core.api.base import BaseHandler
from vFense.core.agent._db_model import AgentKeys
from vFense.core._constants import (
    DefaultQueryValues, SortValues
)
from vFense.core.results import ApiResults, ExternalApiResults
from vFense.core.permissions._constants import Permissions
from vFense.core.permissions.decorators import check_permissions
from vFense.core.decorators import (
    authenticated_request, convert_json_to_arguments, results_message,
    api_catch_it
)
from vFense.core.user import UserKeys
from vFense.core.user.manager import UserManager
from vFense.core.api._constants import ApiArguments

from vFense.plugins.patching import Apps, Files
from vFense.plugins.patching.api.base import AppsBaseHandler
from vFense.plugins.patching.scheduler.manager import (
    AgentAppsJobManager, TagAppsJobManager
)
from vFense.plugins.patching.operations import Install
from vFense.plugins.patching.search.search_by_appid import (
    RetrieveAgentsByAppId
)
from vFense.plugins.patching.search.search import RetrieveApps
from vFense.plugins.patching._db import update_app_data_by_app_id
from vFense.plugins.patching._db_model import AppsKey
from vFense.plugins.patching.operations.store_operations import (
    StorePatchingOperation
)
from vFense.plugins.patching.api._constants import (
    AppApiArguments, AppFilterValues
)
from vFense.plugins.patching._constants import (
    AppStatuses, CommonSeverityKeys
)
from vFense.plugins.patching.uploader.manager import (
    move_app_from_tmp
)

logging.config.fileConfig(VFENSE_LOGGING_CONFIG)
logger = logging.getLogger('vfense_api')

class UploadHandler(BaseHandler):
    @api_catch_it
    @authenticated_request
    @check_permissions(Permissions.ADMINISTRATOR)
    def post(self):
        file_name = self.request.headers.get('x-Filename')
        tmp_path = self.request.headers.get('x-File')
        uuid = self.request.headers.get('x-Fileuuid')
        results = self.return_uploaded_data(file_name, tmp_path, uuid)
        self.set_status(results.http_status_code)
        self.set_header('Content-Type', 'application/json')
        self.write(json.dumps(results.to_dict_non_null(), indent=4))

    @results_message
    def return_uploaded_data(self, file_name, tmp_path, uuid):
        results = move_app_from_tmp(file_name, tmp_path, uuid)
        return results

    @api_catch_it
    @authenticated_request
    @convert_json_to_arguments
    @check_permissions(Permissions.ADMINISTRATOR)
    def put(self):
        active_user = self.get_current_user()
        active_view = UserManager(active_user).properties.current_view
        name = self.arguments.get('name')
        version = self.arguments.get('version')
        md5 = self.arguments.get('md5')
        arch = self.arguments.get('arch')
        uuid = self.arguments.get('uuid')
        size = self.arguments.get('size', None)
        kb = self.arguments.get('kb', '')
        support_url = self.arguments.get('support_url', '')
        severity = self.arguments.get('severity', 'Optional')
        operating_system = self.arguments.get('operating_system')
        platform = self.arguments.get('platform')
        vendor_name = self.arguments.get('vendor_name', None)
        description = self.arguments.get('description', None)
        cli_options = self.arguments.get('cli_options', None)
        release_date = self.arguments.get('release_date', None)
        reboot_required = self.arguments.get('reboot_required', None)
        vulnerability_id = self.arguments.get('vulnerability_id', None)
        vulnerability_categories = (
            self.arguments.get('vulnerability_categories', None)
        )
        cve_ids = self.arguments.get('cve_ids', None)
        app = (
            Apps(
                name, version, arch, uuid, kb, support_url, severity,
                operating_system, platform, vendor_name, description,
                cli_options, release_date,
                reboot_required=reboot_required,
                vulnerability_id=vulnerability_id,
                vulnerability_categories=vulnerability_categories,
                cve_ids=cve_ids
            )
        )
        file_data = Files(name, md5, size)
        results = self.finalize_upload(app, file_data, active_view)
        self.set_header('Content-Type', 'application/json')
        self.write(json.dumps(results.to_dict_non_null(), indent=4))

    @results_message
    def finalize_upload(self, app, file_data, active_view):
        pass


class AgentIdAppsHandler(AppsBaseHandler):
    @api_catch_it
    @authenticated_request
    def get(self, agent_id, oper_type):
        active_user = self.get_current_user().encode('utf-8')
        self.get_and_set_search_arguments()
        oper = self.return_operation_type(oper_type)
        search = self.set_search_for_agent(oper, agent_id)
        results = self.app_search_results(search, active_user)
        self.set_status(results.http_status_code)
        self.modified_output(results, self.output, 'apps')


    @authenticated_request
    @convert_json_to_arguments
    def put(self, agent_id, oper_type):
        active_user = self.get_current_user().encode('utf-8')
        active_view = UserManager(active_user).properties.current_view
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
        oper = self.return_operation_type(oper_type)
        results = (
            self.get_install_results(
                operation, install, active_user, job, oper
            )
        )
        self.set_status(results.http_status_code)
        self.set_header('Content-Type', 'application/json')
        self.write(json.dumps(results.to_dict_non_null(), indent=4))

    @api_catch_it
    @authenticated_request
    @convert_json_to_arguments
    @check_permissions(Permissions.UNINSTALL)
    def delete(self, agent_id, oper_type):
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
        self.set_status(results.http_status_code)
        self.set_header('Content-Type', 'application/json')
        self.write(json.dumps(results.to_dict_non_null(), indent=4))


class TagIdAppsHandler(AppsBaseHandler):
    @api_catch_it
    @authenticated_request
    def get(self, tag_id, oper_type):
        active_user = self.get_current_user().encode('utf-8')
        self.get_and_set_search_arguments()
        oper = self.return_operation_type(oper_type)
        search = self.set_search_for_tag(oper, tag_id)
        results = self.app_search_results(search, active_user)
        self.set_status(results.http_status_code)
        self.modified_output(results, self.output, 'apps')

    @api_catch_it
    @authenticated_request
    @convert_json_to_arguments
    def put(self, tag_id, oper_type):
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
        oper = self.return_operation_type(oper_type)
        results = (
            self.get_install_results(
                operation, install, active_user, job, oper
            )
        )
        self.set_status(results.http_status_code)
        self.set_header('Content-Type', 'application/json')
        self.write(json.dumps(results.to_dict_non_null(), indent=4))
        return results

    @api_catch_it
    @authenticated_request
    @convert_json_to_arguments
    def delete(self, tag_id, oper_type):
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
        self.set_status(results.http_status_code)
        self.set_header('Content-Type', 'application/json')
        self.write(json.dumps(results.to_dict_non_null(), indent=4))


class AppIdAppsHandler(AppsBaseHandler):
    @api_catch_it
    @authenticated_request
    def get(self, oper_type, app_id):
        active_user = self.get_current_user().encode('utf-8')
        active_view = (
            UserManager(active_user).get_attribute(UserKeys.CurrentView)
        )
        output = self.get_argument(ApiArguments.OUTPUT, 'json')
        search = RetrieveApps(view_name=active_view)
        results = self.by_id(search, app_id)
        self.set_status(results.http_status_code)
        self.modified_output(results, output, 'app')

    @results_message
    def by_id(self, search, app_id):
        results = search.by_id(app_id)
        return results

    @api_catch_it
    @authenticated_request
    @convert_json_to_arguments
    @check_permissions(Permissions.ADMINISTRATOR)
    def post(self, oper_type, app_id):
        severity = self.arguments.get('severity').capitalize()
        results = self.update_severity(severity, app_id)
        self.set_status(results.http_status_code)
        self.set_header('Content-Type', 'application/json')
        self.write(json.dumps(results.to_dict_non_null(), indent=4))

    @results_message
    def update_severity(self, severity, app_id):
        results = ApiResults()
        results.fill_in_defaults()
        results.data = {AppsKey.vFenseSeverity: severity}
        if severity in CommonSeverityKeys.ValidRvSeverities:
            update_app_data_by_app_id(app_id, results.data)
            results.message = (
                'Severity updated for app id: {0}'.format(app_id)
            )
            results.updated_ids.append(app_id)
        else:
            results.message = (
                'Severity failed tp update for app id: {0}'.format(app_id)
            )
            results.unchanged_ids.append(app_id)

        return results


    @authenticated_request
    @convert_json_to_arguments
    @check_permissions(Permissions.INSTALL)
    def put(self, oper_type, app_id):
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
        oper = self.return_operation_type(oper_type)
        results = (
            self.get_install_results(
                operation, install, active_user, job, oper
            )
        )
        self.set_status(results.http_status_code)
        self.set_header('Content-Type', 'application/json')
        self.write(json.dumps(results.to_dict_non_null(), indent=4))
        return results

    @authenticated_request
    @convert_json_to_arguments
    @check_permissions(Permissions.UNINSTALL)
    def delete(self, oper_type, app_id):
        active_user = self.get_current_user().encode('utf-8')
        active_view = UserManager(active_user).properties.current_view
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
        self.set_status(results.http_status_code)
        self.set_header('Content-Type', 'application/json')
        self.write(json.dumps(results.to_dict_non_null(), indent=4))
        return results


class GetAgentsByAppIdHandler(AppsBaseHandler):
    @authenticated_request
    def get(self, oper_type, app_id):
        active_user = self.get_current_user().encode('utf-8')
        active_view = UserManager(active_user).properties.current_view
        self.get_and_set_search_arguments()
        oper = self.return_operation_type(oper_type)
        search = self.set_base_search(oper, active_view)
        if (not self.query and not self.severity and not self.vuln
                and not self.status):
            results = self.all(search)

        else:
            results = self.app_search_results(search, active_user)
        self.set_status(results.http_status_code)
        self.modified_output(results, self.output, 'apps')

    @results_message
    def all(self, search):
        results = search.all()
        return results


    @authenticated_request
    @convert_json_to_arguments
    @check_permissions(Permissions.INSTALL)
    def put(self, oper_type, app_id):
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
        oper = self.return_operation_type(oper_type)
        results = (
            self.get_install_results(
                operation, install, active_user, job, oper
            )
        )
        self.set_status(results.http_status_code)
        self.set_header('Content-Type', 'application/json')
        self.write(json.dumps(results.to_dict_non_null(), indent=4))
        return results


    @authenticated_request
    @convert_json_to_arguments
    @check_permissions(Permissions.UNINSTALL)
    def delete(self, oper_type, app_id):
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
        self.set_status(results.http_status_code)
        self.set_header('Content-Type', 'application/json')
        self.write(json.dumps(results.to_dict_non_null(), indent=4))
        return results


class AppsHandler(AppsBaseHandler):
    @authenticated_request
    def get(self, oper_type):
        active_user = self.get_current_user().encode('utf-8')
        active_view = UserManager(active_user).properties.current_view
        self.get_and_set_search_arguments()
        oper = self.return_operation_type(oper_type)
        search = self.set_base_search(oper, active_view)
        if (not self.query and not self.severity and not self.vuln
                and not self.status):
            results = self.all(search)

        else:
            results = self.app_search_results(search, active_user)

        self.set_status(results.http_status_code)
        self.modified_output(results, self.output, 'apps')

    @results_message
    def all(self, search):
        results = search.all()
        return results

    @authenticated_request
    @convert_json_to_arguments
    def put(self, oper_type):
        oper = self.return_operation_type(oper_type)
        self.app_ids = self.arguments.get('app_ids')
        self.toggle = self.arguments.get('hide', 'toggle')
        results = self.set_toggle_status(oper)
        self.set_status(results.http_status_code)
        self.set_header('Content-Type', 'application/json')
        self.write(json.dumps(results.to_dict_non_null(), indent=4))
