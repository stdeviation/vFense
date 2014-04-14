#!/usr/bin/env python
from json import loads
import logging
import logging.config
from datetime import datetime
from time import mktime

from vFense.db.client import r
from vFense.db.notificationhandler import *
from vFense.errorz.error_messages import GenericResults, AgentOperationCodes
from vFense.utils.common import *
from vFense.core.agent import *
from vFense.core.agent.agents import get_agent_info, update_agent_field
from vFense.core.tag import *
from vFense.plugins.patching import *
from vFense.plugins.patching.rv_db_calls import *
from vFense.plugins.patching.os_apps.incoming_updates import \
    incoming_packages_from_agent
from vFense.operations import *
from vFense.operations.agent_operations import AgentOperation, \
    operation_for_agent_and_app_exist, operation_for_agent_exist, \
    get_agent_operation


logging.config.fileConfig('/opt/TopPatch/conf/logging.config')
logger = logging.getLogger('rvapi')


class AddResults(object):
    def __init__(self, username, uri, method, agent_id,
                 operation_id, success, error=None):

        self.agent_id = agent_id
        self.operation_id = operation_id
        self.username = username
        self.uri = uri
        self.method = method
        self.agent_data = get_agent_info(self.agent_id)
        self.customer_name = self.agent_data['customer_name']
        self.date_now = mktime(datetime.now().timetuple())
        self.error = error
        self.success = success
        self.operation = (
            AgentOperation(
                self.username, self.customer_name,
                self.uri, self.method
            )
        )

    def reboot(self):
        oper_type = REBOOT
        results = self._update_operation(oper_type)

        if self.success == "true":
            update_agent_field(
                self.agent_id,
                AgentKey.NeedsReboot,
                'no', self.username,
                self.uri, self.method
            )

        return(results)

    def shutdown(self):
        oper_type = SHUTDOWN
        results = self._update_operation(oper_type)
        return(results)

    def ra(self, operation_type):
        oper_type = operation_type
        results = self._update_operation(oper_type)
        return(results)

    def apps_refresh(self):
        oper_type = UPDATES_APPLICATIONS
        results = self._update_operation(oper_type)
        return(results)

    def _update_operation(self, oper_type):
        try:
            oper_exists = (
                operation_for_agent_exist(
                    self.operation_id, self.agent_id
                )
            )

            if oper_exists:
                if self.success == "true":
                    results = (
                        self.operation.update_operation_results(
                            self.operation_id, self.agent_id,
                            AgentOperationCodes.ResultsReceived,
                            oper_type, self.error
                        )
                    )

                else:
                    results = (
                        self.operation.update_operation_results(
                            self.operation_id, self.agent_id,
                            AgentOperationCodes.ResultsReceivedWithErrors,
                            oper_type, self.error
                        )
                    )

            else:
                results = (
                    GenericResults(
                        self.username, self.uri, self.method
                    ).invalid_id(self.operation_id, oper_type)
                )

        except Exception as e:
            results = (
                GenericResults(
                    self.username, self.uri, self.method
                ).something_broke(self.operation_id, oper_type, e)
            )
            logger.exception(results)

        return(results)


class AddAppResults(object):
    def __init__(self, username, uri, method, agent_id,
                 app_id, operation_id, reboot_required,
                 success, data, apps_to_delete,
                 apps_to_add, error=None):

        self.agent_id = agent_id
        self.operation_id = operation_id
        self.username = username
        self.uri = uri
        self.method = method
        self.agent_data = get_agent_info(self.agent_id)
        self.customer_name = self.agent_data['customer_name']
        self.date_now = mktime(datetime.now().timetuple())
        self.error = error
        self.reboot_required = reboot_required
        self.success = success
        self.data = data
        self.apps_to_delete = apps_to_delete
        self.apps_to_add = apps_to_add
        self.app_id = app_id
        self.oper_info=get_agent_operation(self.operation_id)
        self.operation = (
            Operation(
                self.username, self.customer_name,
                self.uri, self.method
            )
        )

    def install_os_apps(self, data):
        oper_type = self.oper_info[OperationKey.Operation]
        self.CurrentAppsCollection = AppsCollection
        self.CurrentAppsKey = AppsKey
        self.CurrentAppsPerAgentCollection = AppsPerAgentCollection
        self.CurrentAppsPerAgentKey = AppsPerAgentKey
        results = self._update_app_status(data, oper_type)
        return(results)

    def install_supported_apps(self, data):
        oper_type = INSTALL_SUPPORTED_APPS
        self.CurrentAppsCollection = SupportedAppsCollection
        self.CurrentAppsKey = SupportedAppsKey
        self.CurrentAppsPerAgentCollection = SupportedAppsPerAgentCollection
        self.CurrentAppsPerAgentKey = SupportedAppsPerAgentKey
        results = self._update_app_status(data, oper_type)
        return(results)

    def install_custom_apps(self, data):
        oper_type = INSTALL_CUSTOM_APPS
        self.CurrentAppsCollection = CustomAppsCollection
        self.CurrentAppsKey = CustomAppsKey
        self.CurrentAppsPerAgentCollection = CustomAppsPerAgentCollection
        self.CurrentAppsPerAgentKey = CustomAppsPerAgentKey
        results = self._update_app_status(data, oper_type)
        return(results)

    def install_agent_update(self, data):
        oper_type = INSTALL_AGENT_UPDATE
        self.CurrentAppsCollection = AgentAppsCollection
        self.CurrentAppsKey = AgentAppsKey
        self.CurrentAppsPerAgentCollection = AgentAppsPerAgentCollection
        self.CurrentAppsPerAgentKey = AgentAppsPerAgentKey
        data = loads(data)
        results = self._update_app_status(data, oper_type)
        return(results)

    def _update_app_status(self, data, oper_type):
        try:
            if self.reboot_required == 'true':
                update_agent_field(
                    self.agent_id, 'needs_reboot',
                    'yes', self.username
                )

            if self.success == 'true' and re.search(r'^install', oper_type):
                status = INSTALLED
                install_date = self.date_now

            elif self.success == 'true' and re.search(r'^uninstall', oper_type):
                status = AVAILABLE
                install_date = 0.0

            elif self.success == 'false' and re.search(r'^install', oper_type):
                status = AVAILABLE
                install_date = 0.0

            elif self.success == 'false' and re.search(r'^uninstall', oper_type):
                status = INSTALLED
                install_date = 0.0

            app_exist = get_app_data(self.app_id, table=self.CurrentAppsCollection)
            oper_app_exists = (
                operation_for_agent_and_app_exist(
                    self.operation_id, self.agent_id, self.app_id
                )
            )
            if app_exist:
                if oper_app_exists and self.success == 'true':
                    results = (
                        self.operation.update_app_results(
                            self.operation_id, self.agent_id,
                            self.app_id, AgentOperationCodes.ResultsReceived,
                            errors=self.error
                        )
                    )
                    if self.apps_to_delete:
                        try:
                            self.apps_to_delete = [loads(x) for x in self.apps_to_delete]
                        except Exception as e:
                            logger.exception(e)

                        for apps in self.apps_to_delete:
                            delete_app_from_agent(
                                apps[NAME],
                                apps[VERSION],
                                self.agent_id
                            )
                    if self.apps_to_add:
                        try:
                            self.apps_to_add = [loads(x) for x in self.apps_to_add]
                        except Exception as e:
                            logger.exception(e)

                        incoming_packages_from_agent(
                            self.username, self.agent_id,
                            self.customer_name,
                            self.agent_data[AgentKey.OsCode],
                            self.agent_data[AgentKey.OsString],
                            self.apps_to_add, delete_afterwards=False
                        )

                elif oper_app_exists and self.success == 'false':
                    results = (
                        self.operation.update_app_results(
                            self.operation_id, self.agent_id,
                            self.app_id, AgentOperationCodes.ResultsReceivedWithErrors,
                            errors=self.error
                        )
                    )
                else:
                    results = (
                        GenericResults(
                            self.username, self.uri, self.method
                        ).invalid_id(self.operation_id, oper_type)
                    )
                data_to_update = (
                    {
                        self.CurrentAppsPerAgentKey.Status: status,
                        self.CurrentAppsPerAgentKey.InstallDate: r.epoch_time(install_date)
                    }
                )
                if oper_type == INSTALL_OS_APPS or oper_type == UNINSTALL:
                    update_os_app_per_agent(self.agent_id, self.app_id, data_to_update)

                elif oper_type == INSTALL_CUSTOM_APPS:
                    update_custom_app_per_agent(self.agent_id, self.app_id, data_to_update)

                elif oper_type == INSTALL_SUPPORTED_APPS:
                    update_supported_app_per_agent(self.agent_id, self.app_id, data_to_update)

                elif oper_type == INSTALL_AGENT_UPDATE:
                    update_agent_app_per_agent(self.agent_id, self.app_id, data_to_update)

            else:
                results = (
                    GenericResults(
                        self.username, self.uri, self.method
                    ).invalid_id(self.operation_id, oper_type)
                )

        except Exception as e:
            results = (
                GenericResults(
                    self.username, self.uri, self.method
                ).something_broke(self.operation_id, oper_type, e)
            )
            logger.exception(results)

        return(results)
