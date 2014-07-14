import logging
from json import dumps

from vFense import VFENSE_LOGGING_CONFIG
from vFense.core.api.base import BaseHandler
from vFense.receiver.api.decorators import authenticate_agent
from vFense.core.decorators import (
    convert_json_to_arguments, results_message
)
from vFense.core._constants import CommonKeys

from vFense.plugins.patching.operations.patching_results import (
    PatchingOperationResults
)
from vFense.core.results import Results



logging.config.fileConfig(VFENSE_LOGGING_CONFIG)
logger = logging.getLogger('rvlistener')


class AppsResultsV2(BaseHandler):
    @authenticate_agent
    @convert_json_to_arguments
    def put(self, agent_id):
        uri = self.request.uri
        method = self.request.method
        try:
            logger.info(self.request.body)
            operation_id = self.arguments.get('operation_id')
            apps_to_delete = self.arguments.get('apps_to_delete', [])
            apps_to_add = self.arguments.get('apps_to_add', [])
            error = self.arguments.get('error', None)
            reboot_required = self.arguments.get('reboot_required')
            app_id = self.arguments.get('app_id')
            success = self.arguments.get('success')
            status_code = self.arguments.get('status_code', None)

            if not isinstance(reboot_required, bool):
                if reboot_required == CommonKeys.TRUE:
                    reboot_required = True
                else:
                    reboot_required = False

            update_results = (
                PatchingOperationResults(
                    agent_id, operation_id, success, error, status_code
                )
            )
            results = (
                self.update_app_results(
                    update_results, app_id, reboot_required,
                    apps_to_delete, apps_to_add
                )
            )
            self.set_status(results['http_status'])
            self.set_header('Content-Type', 'application/json')
            self.write(dumps(results, indent=4))

        except Exception as e:
            results = (
                Results(
                    'agent', uri, method
                ).something_broke(agent_id, 'install_os_apps results', e)
            )
            logger.exception(results)

            self.set_status(results['http_status'])
            self.set_header('Content-Type', 'application/json')
            self.write(dumps(results, indent=4))

    @results_message
    def update_app_results(self, update_results, app_id,
                           reboot_required, apps_to_delete, apps_to_add):
        results = (
            update_results.install_os_apps(
                app_id, reboot_required, apps_to_delete, apps_to_add
            )
        )
        return results


class CustomAppsResultsV2(BaseHandler):
    @authenticate_agent
    @convert_json_to_arguments
    def put(self, agent_id):
        uri = self.request.uri
        method = self.request.method
        try:
            logger.info(self.request.body)
            operation_id = self.arguments.get('operation_id')
            apps_to_delete = self.arguments.get('apps_to_delete', [])
            apps_to_add = self.arguments.get('apps_to_add', [])
            error = self.arguments.get('error', None)
            reboot_required = self.arguments.get('reboot_required')
            app_id = self.arguments.get('app_id')
            success = self.arguments.get('success')
            status_code = self.arguments.get('status_code', None)
            logger.info("self.arguments: {0}".format(self.arguments))

            if not isinstance(reboot_required, bool):
                if reboot_required == CommonKeys.TRUE:
                    reboot_required = True
                else:
                    reboot_required = False

            update_results = (
                PatchingOperationResults(
                    agent_id, operation_id, success, error, status_code
                )
            )
            results = (
                self.update_custom_app_results(
                    update_results, app_id, reboot_required,
                    apps_to_delete, apps_to_add
                )
            )
            self.set_status(results['http_status'])
            self.set_header('Content-Type', 'application/json')
            self.write(dumps(results, indent=4))

        except Exception as e:
            results = (
                Results(
                    'agent', uri, method
                ).something_broke(agent_id, 'install_custom_apps results', e)
            )
            logger.exception(results)

            self.set_status(results['http_status'])
            self.set_header('Content-Type', 'application/json')
            self.write(dumps(results, indent=4))

    @results_message
    def update_custom_app_results(self, update_results, app_id,
                                  reboot_required, apps_to_delete,
                                  apps_to_add):
        results = (
            update_results.install_custom_apps(
                app_id, reboot_required, apps_to_delete, apps_to_add
            )
        )
        return results


class SupportedAppsResultsV2(BaseHandler):
    @authenticate_agent
    @convert_json_to_arguments
    def put(self, agent_id):
        uri = self.request.uri
        method = self.request.method
        try:
            operation_id = self.arguments.get('operation_id')
            apps_to_delete = self.arguments.get('apps_to_delete', [])
            apps_to_add = self.arguments.get('apps_to_add', [])
            error = self.arguments.get('error', None)
            reboot_required = self.arguments.get('reboot_required')
            app_id = self.arguments.get('app_id')
            success = self.arguments.get('success')
            status_code = self.arguments.get('status_code', None)
            logger.info("self.arguments: {0}".format(self.arguments))

            if not isinstance(reboot_required, bool):
                if reboot_required == CommonKeys.TRUE:
                    reboot_required = True
                else:
                    reboot_required = False

            update_results = (
                PatchingOperationResults(
                    agent_id, operation_id, success, error, status_code
                )
            )
            results = self.update_supported_app_results(
                update_results, app_id, reboot_required,
                apps_to_delete, apps_to_add
            )

            self.set_status(results['http_status'])
            self.set_header('Content-Type', 'application/json')
            self.write(dumps(results, indent=4))

        except Exception as e:
            results = (
                Results(
                    'agent', uri, method
                ).something_broke(agent_id, 'install_supported_apps results', e)
            )
            logger.exception(results)

            self.set_status(results['http_status'])
            self.set_header('Content-Type', 'application/json')
            self.write(dumps(results, indent=4))

    @results_message
    def update_supported_app_results(self, update_results, app_id,
                                     reboot_required, apps_to_delete,
                                     apps_to_add):
        results = (
            update_results.install_supported_apps(
                app_id, reboot_required, apps_to_delete, apps_to_add
            )
        )
        return results


class vFenseAppsResultsV2(BaseHandler):
    @authenticate_agent
    @convert_json_to_arguments
    def put(self, agent_id):
        uri = self.request.uri
        method = self.request.method
        try:
            logger.info(self.request.body)
            operation_id = self.arguments.get('operation_id')
            apps_to_delete = self.arguments.get('apps_to_delete', [])
            apps_to_add = self.arguments.get('apps_to_add', [])
            error = self.arguments.get('error', None)
            reboot_required = self.arguments.get('reboot_required')
            app_id = self.arguments.get('app_id')
            success = self.arguments.get('success')
            status_code = self.arguments.get('status_code', None)
            logger.info("self.arguments: {0}".format(self.arguments))

            if not isinstance(reboot_required, bool):
                if reboot_required == CommonKeys.TRUE:
                    reboot_required = True
                else:
                    reboot_required = False

            update_results = (
                PatchingOperationResults(
                    agent_id, operation_id, success, error, status_code
                )
            )
            results_data = (
                self.update_agent_app_results(
                    update_results, app_id, reboot_required,
                    apps_to_delete, apps_to_add
                )
            )

            self.set_status(results_data['http_status'])
            self.set_header('Content-Type', 'application/json')
            self.write(dumps(results_data, indent=4))

        except Exception as e:
            results = (
                Results(
                    'agent', uri, method
                ).something_broke(agent_id, 'install_agent_apps results', e)
            )
            logger.exception(results)

            self.set_status(results['http_status'])
            self.set_header('Content-Type', 'application/json')
            self.write(dumps(results, indent=4))

    @results_message
    def update_agent_app_results(self, update_results, app_id,
                                 reboot_required, apps_to_delete,
                                 apps_to_add):
        results = (
            update_results.install_agent_apps(
                app_id, reboot_required, apps_to_delete, apps_to_add
            )
        )
        return results


class UninstallResultsV2(BaseHandler):
    @authenticate_agent
    @convert_json_to_arguments
    def put(self, agent_id):
        uri = self.request.uri
        method = self.request.method
        try:
            logger.info(self.request.body)
            operation_id = self.arguments.get('operation_id')
            apps_to_delete = self.arguments.get('apps_to_delete', [])
            apps_to_add = self.arguments.get('apps_to_add', [])
            error = self.arguments.get('error', None)
            reboot_required = self.arguments.get('reboot_required')
            app_id = self.arguments.get('app_id')
            success = self.arguments.get('success')
            status_code = self.arguments.get('status_code', None)
            logger.info("self.arguments: {0}".format(self.arguments))

            if not isinstance(reboot_required, bool):
                if reboot_required == CommonKeys.TRUE:
                    reboot_required = True
                else:
                    reboot_required = False

            update_results = (
                PatchingOperationResults(
                    agent_id, operation_id, success, error, status_code
                )
            )
            results = (
                self.update_app_results(
                    update_results, app_id, reboot_required,
                    apps_to_delete, apps_to_add
                )
            )
            self.set_status(results['http_status'])
            self.set_header('Content-Type', 'application/json')
            self.write(dumps(results, indent=4))

        except Exception as e:
            results = (
                Results(
                    'agent', uri, method
                ).something_broke(agent_id, 'uninstall_os_apps results', e)
            )
            logger.exception(results)

            self.set_status(results['http_status'])
            self.set_header('Content-Type', 'application/json')
            self.write(dumps(results, indent=4))


    @results_message
    def update_app_results(self, update_results, app_id, reboot_required,
                           apps_to_delete, apps_to_add):
        results = (
            update_results.install_os_apps(
                app_id, reboot_required, apps_to_delete, apps_to_add
            )
        )
        return results
