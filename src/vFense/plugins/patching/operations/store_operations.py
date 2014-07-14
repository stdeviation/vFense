import logging
import logging.config
from vFense import VFENSE_LOGGING_CONFIG
from vFense.plugins.patching.operations.patching_operations import \
    PatchingOperation
from vFense.core.operations._constants import AgentOperations, vFensePlugins, \
    vFenseObjects
from vFense.core.operations.store_agent_operation import StoreAgentOperation
from vFense.core.operations._db_model import AgentOperationKey, OperationPerAgentKey
from vFense.core._constants import CPUThrottleValues, RebootValues
from vFense.plugins.patching._db_model import AppCollections, DbCommonAppKeys, \
        DbCommonAppPerAgentKeys
from vFense.plugins.patching._db import fetch_app_data_to_send_to_agent, \
    return_valid_appids_for_agent

from vFense.plugins.patching._constants import CommonAppKeys, CommonFileKeys
from vFense.plugins.patching.patching import get_download_urls, \
    update_app_status_by_agentid_and_appid

from vFense.core.tag._db import fetch_agent_ids_in_tag
from vFense.result._constants import ApiResultKeys
from vFense.core.status_codes import GenericCodes, GenericFailureCodes
from vFense.core.operations.status_codes import (
    AgentOperationCodes, AgentOperationFailureCodes
)

logging.config.fileConfig(VFENSE_LOGGING_CONFIG)
logger = logging.getLogger('rvapi')


class StorePatchingOperation(StoreAgentOperation):
    """Create operations for the patching plugin"""
    def refresh_apps(self, agent_ids=None, tag_id=None):
        """Send the apps_refresh operation to the agent,
            Send all installed applications and updates needed
            to the server.
        Kwargs:
            agent_ids (str): List of agent ids.
                default = None
            tag_id (str): 36 character UUID of the agent.
                default = None

        Basic Usage:
            >>> from vFense.plugins.patching.operations.store_operations import StorePatchingOperation
            >>> agent_ids = ['e9a8871a-5ae8-40fb-9316-b0918947f736']
            >>> username = 'admin'
            >>> view_name = 'default'
            >>> uri = '/api/v1/agent/e9a8871a-5ae8-40fb-9316-b0918947f736/apps/os'
            >>> method = 'PUT'
            >>> operation = StorePatchingOperation(username, view_name, uri, method)
            >>> operation.refresh_apps(agent_ids=agent_ids)

        Returns:
        """
        results = (
            self.generic_operation(
                AgentOperations.REFRESH_APPS,
                vFensePlugins.RV_PLUGIN,
                agent_ids, tag_id
            )
        )

        return results

    def uninstall_agent(self, agent_id):
        operation_data = {
            AgentOperationKey.Operation: AgentOperations.UNINSTALL_AGENT,
            AgentOperationKey.Plugin: vFensePlugins.RV_PLUGIN,
            OperationPerAgentKey.AgentId: agent_id,
        }
        self._store_in_agent_queue(operation_data)

    def install_os_apps(
            self, app_ids, cpu_throttle=CPUThrottleValues.NORMAL,
            net_throttle=0, restart=RebootValues.NONE,
            agent_ids=None, tag_id=None
        ):
        """Send the install_os_apps operation to the agent,
            This will install a list of applications on n
            number of agents or tag id.
        Args:
            app_ids (list): List of the application ids,
                that you want to install.

        Kwargs:
            cpu_throttle (str): Throttle how much cpu to use while installing
                the applications.
                default = normal
            net_throttle (int): Throttle how much bandwidth is being used,
                while the agent is downloading the applications.
                default = 0 (unlimited)
            restart (str): Choose if you want to restart the system after
                the application is installed. Examples (none, needed, forced)
                default = 'none' (do not reboot)
            agent_ids (str): List of agent ids.
                default = None
            tag_id (str): 36 character UUID of the agent.
                default = None

        Basic Usage:
            >>> from vFense.plugins.patching.operations.store_operations import StorePatchingOperation
            >>> username = 'admin'
            >>> view_name = 'default'
            >>> uri = '/api/v1/agent/e9a8871a-5ae8-40fb-9316-b0918947f736/apps/os'
            >>> method = 'PUT'
            >>> app_ids = ['000bd2abd0f5197612dad031eb5d04abc082aba1b904b801c7b2d7925ac248a3']
            >>> reboot = 'needed'
            >>> cpu = 'high'
            >>> net = 100
            >>> agent_ids = ['e9a8871a-5ae8-40fb-9316-b0918947f736']
            >>> operation = StorePatchingOperation(username, view_name, uri, method)
            >>> operation.install_os_apps(
                    app_ids, cpu_throttle=cpu, net_throttle=net,
                    restart=reboot, agent_ids=agent_ids
                )

        Returns:
        """
        oper_type = AgentOperations.INSTALL_OS_APPS

        self.CurrentAppsCollection = AppCollections.UniqueApplications
        self.CurrentAppsKey = DbCommonAppKeys
        self.CurrentAppsPerAgentCollection = AppCollections.AppsPerAgent
        self.CurrentAppsPerAgentKey = DbCommonAppPerAgentKeys

        return(
            self.install_apps(
                oper_type, app_ids,
                cpu_throttle, net_throttle,
                restart, agent_ids, tag_id
            )
        )

    def install_custom_apps(
            self, app_ids, cpu_throttle=CPUThrottleValues.NORMAL,
            net_throttle=0, restart=RebootValues.NONE,
            agent_ids=None, tag_id=None
        ):
        """Send the install_custom_apps operation to the agent,
            This will install a list of applications on n
            number of agents or tag id.
        Args:
            app_ids (list): List of the application ids,
                that you want to install.

        Kwargs:
            cpu_throttle (str): Throttle how much cpu to use while installing
                the applications.
                default = normal
            net_throttle (int): Throttle how much bandwidth is being used,
                while the agent is downloading the applications.
                default = 0 (unlimited)
            restart (str): Choose if you want to restart the system after
                the application is installed. Examples (none, needed, forced)
                default = 'none' (do not reboot)
            agent_ids (str): List of agent ids.
                default = None
            tag_id (str): 36 character UUID of the agent.
                default = None

        Basic Usage:
            >>> from vFense.plugins.patching.operations.store_operations import StorePatchingOperation
            >>> username = 'admin'
            >>> view_name = 'default'
            >>> uri = '/api/v1/agent/e9a8871a-5ae8-40fb-9316-b0918947f736/apps/custom'
            >>> method = 'PUT'
            >>> app_ids = ['000bd2abd0f5197612dad031eb5d04abc082aba1b904b801c7b2d7925ac248a3']
            >>> reboot = 'needed'
            >>> cpu = 'high'
            >>> net = 100
            >>> agent_ids = ['e9a8871a-5ae8-40fb-9316-b0918947f736']
            >>> operation = StorePatchingOperation(username, view_name, uri, method)
            >>> operation.install_custom_apps(
                    app_ids, cpu_throttle=cpu, net_throttle=net,
                    restart=reboot, agent_ids=agent_ids
                )
        """

        oper_type = AgentOperations.INSTALL_CUSTOM_APPS

        self.CurrentAppsCollection = AppCollections.CustomApps
        self.CurrentAppsKey = DbCommonAppKeys
        self.CurrentAppsPerAgentCollection = AppCollections.CustomAppsPerAgent
        self.CurrentAppsPerAgentKey = DbCommonAppPerAgentKeys

        return(
            self.install_apps(
                oper_type, app_ids,
                cpu_throttle, net_throttle,
                restart, agent_ids, tag_id
            )
        )

    def install_supported_apps(
            self, app_ids, cpu_throttle=CPUThrottleValues.NORMAL,
            net_throttle=0, restart=RebootValues.NONE,
            agent_ids=None, tag_id=None
        ):
        """Send the install_supported_apps operation to the agent,
            This will install a list of supported applications on n
            number of agents or tag id.
        Args:
            app_ids (list): List of the application ids,
                that you want to install.

        Kwargs:
            cpu_throttle (str): Throttle how much cpu to use while installing
                the applications.
                default = normal
            net_throttle (int): Throttle how much bandwidth is being used,
                while the agent is downloading the applications.
                default = 0 (unlimited)
            restart (str): Choose if you want to restart the system after
                the application is installed. Examples (none, needed, forced)
                default = 'none' (do not reboot)
            agent_ids (str): List of agent ids.
                default = None
            tag_id (str): 36 character UUID of the agent.
                default = None

        Basic Usage:
            >>> from vFense.plugins.patching.operations.store_operations import StorePatchingOperation
            >>> username = 'admin'
            >>> view_name = 'default'
            >>> uri = '/api/v1/agent/e9a8871a-5ae8-40fb-9316-b0918947f736/apps/supported'
            >>> method = 'PUT'
            >>> app_ids = ['000bd2abd0f5197612dad031eb5d04abc082aba1b904b801c7b2d7925ac248a3']
            >>> reboot = 'needed'
            >>> cpu = 'high'
            >>> net = 100
            >>> agent_ids = ['e9a8871a-5ae8-40fb-9316-b0918947f736']
            >>> operation = StorePatchingOperation(username, view_name, uri, method)
            >>> operation.install_supported_apps(
                    app_ids, cpu_throttle=cpu, net_throttle=net,
                    restart=reboot, agent_ids=agent_ids
                )
        """

        oper_type = AgentOperations.INSTALL_SUPPORTED_APPS

        self.CurrentAppsCollection = AppCollections.SupportedApps
        self.CurrentAppsKey = DbCommonAppKeys
        self.CurrentAppsPerAgentCollection = AppCollections.SupportedAppsPerAgent
        self.CurrentAppsPerAgentKey = DbCommonAppPerAgentKeys

        return(
            self.install_apps(
                oper_type, app_ids,
                cpu_throttle, net_throttle,
                restart, agent_ids, tag_id
            )
        )

    def install_agent_update(
            self, app_ids, cpu_throttle=CPUThrottleValues.NORMAL,
            net_throttle=0, restart=RebootValues.NONE,
            agent_ids=None, tag_id=None
        ):
        """Send the install_agent_update operation to the agent,
            This will install the agent update on n
            number of agents or tag id.
        Args:
            app_ids (list): List of the application ids,
                that you want to install.

        Kwargs:
            cpu_throttle (str): Throttle how much cpu to use while installing
                the applications.
                default = normal
            net_throttle (int): Throttle how much bandwidth is being used,
                while the agent is downloading the applications.
                default = 0 (unlimited)
            restart (str): Choose if you want to restart the system after
                the application is installed. Examples (none, needed, forced)
                default = 'none' (do not reboot)
            agent_ids (str): List of agent ids.
                default = None
            tag_id (str): 36 character UUID of the agent.
                default = None

        Basic Usage:
            >>> from vFense.plugins.patching.operations.store_operations import StorePatchingOperation
            >>> username = 'admin'
            >>> view_name = 'default'
            >>> uri = '/api/v1/agent/e9a8871a-5ae8-40fb-9316-b0918947f736/apps/agent'
            >>> method = 'PUT'
            >>> app_ids = ['000bd2abd0f5197612dad031eb5d04abc082aba1b904b801c7b2d7925ac248a3']
            >>> reboot = 'needed'
            >>> cpu = 'high'
            >>> net = 100
            >>> agent_ids = ['e9a8871a-5ae8-40fb-9316-b0918947f736']
            >>> operation = StorePatchingOperation(username, view_name, uri, method)
            >>> operation.install_agent_update(
                    app_ids, cpu_throttle=cpu, net_throttle=net,
                    restart=reboot, agent_ids=agent_ids
                )
        """

        oper_type = AgentOperations.INSTALL_AGENT_UPDATE

        self.CurrentAppsCollection = AppCollections.vFenseApps
        self.CurrentAppsKey = DbCommonAppKeys
        self.CurrentAppsPerAgentCollection = AppCollections.vFenseAppsPerAgent
        self.CurrentAppsPerAgentKey = DbCommonAppPerAgentKeys

        return self.install_apps(
            oper_type,
            app_ids,
            cpu_throttle,
            net_throttle,
            restart,
            agent_ids,
            tag_id
        )

    def uninstall_apps(
            self, app_ids, cpu_throttle=CPUThrottleValues.NORMAL,
            net_throttle=0, restart=RebootValues.NONE,
            agent_ids=None, tag_id=None
        ):
        """Send the uninstall_apps operation to the agent,
            This will uninstall the applications from n
            number of agents or tag id.
        Args:
            app_ids (list): List of the application ids,
                that you want to install.

        Kwargs:
            cpu_throttle (str): Throttle how much cpu to use while installing
                the applications.
                default = normal
            net_throttle (int): Throttle how much bandwidth is being used,
                while the agent is downloading the applications.
                default = 0 (unlimited)
            restart (str): Choose if you want to restart the system after
                the application is installed. Examples (none, needed, forced)
                default = 'none' (do not reboot)
            agent_ids (str): List of agent ids.
                default = None
            tag_id (str): 36 character UUID of the agent.
                default = None

        Basic Usage:
            >>> from vFense.plugins.patching.operations.store_operations import StorePatchingOperation
            >>> username = 'admin'
            >>> view_name = 'default'
            >>> uri = '/api/v1/agent/e9a8871a-5ae8-40fb-9316-b0918947f736/apps/agent'
            >>> method = 'PUT'
            >>> app_ids = ['000bd2abd0f5197612dad031eb5d04abc082aba1b904b801c7b2d7925ac248a3']
            >>> reboot = 'needed'
            >>> cpu = 'high'
            >>> net = 100
            >>> agent_ids = ['e9a8871a-5ae8-40fb-9316-b0918947f736']
            >>> operation = StorePatchingOperation(username, view_name, uri, method)
            >>> operation.uninstall_apps(
                    app_ids, cpu_throttle=cpu, net_throttle=net,
                    restart=reboot, agent_ids=agent_ids
                )
        """

        oper_type = AgentOperations.UNINSTALL

        self.CurrentAppsCollection = AppCollections.UniqueApplications
        self.CurrentAppsKey = DbCommonAppKeys
        self.CurrentAppsPerAgentCollection = AppCollections.AppsPerAgent
        self.CurrentAppsPerAgentKey = DbCommonAppPerAgentKeys

        return(
            self.install_apps(
                oper_type, app_ids,
                cpu_throttle, net_throttle,
                restart, agent_ids, tag_id
            )
        )

    def install_apps(
            self, oper_type, app_ids,
            cpu_throttle=CPUThrottleValues.NORMAL,
            net_throttle=0, restart=RebootValues.NONE,
            agent_ids=None, tag_id=None
        ):
        """This method creates the operation and stores it into the agent queue.
        Args:
            oper_type (str): The operation type,
                etc.. install_os_apps, uninstall
            app_ids (list): List of the application ids,
                that you want to install.

        Kwargs:
            cpu_throttle (str): Throttle how much cpu to use while installing
                the applications.
                default = normal
            net_throttle (int): Throttle how much bandwidth is being used,
                while the agent is downloading the applications.
                default = 0 (unlimited)
            restart (str): Choose if you want to restart the system after
                the application is installed. Examples (none, needed, forced)
                default = 'none' (do not reboot)
            agent_ids (str): List of agent ids.
                default = None
            tag_id (str): 36 character UUID of the agent.
                default = None

        """

        oper_plugin = vFensePlugins.RV_PLUGIN
        results = {
            ApiResultKeys.DATA: [],
            ApiResultKeys.USERNAME: self.username,
        }

        performed_on = vFenseObjects.AGENT
        if tag_id:
            performed_on = vFenseObjects.TAG
            if not agent_ids:
                agent_ids = fetch_agent_ids_in_tag(tag_id)
            else:
                agent_ids += fetch_agent_ids_in_tag(tag_id)

        operation = (
            PatchingOperation(
                self.username, self.view_name,
            )
        )

        operation_id = (
            operation.create_operation(
                oper_type, oper_plugin, agent_ids,
                tag_id, cpu_throttle,
                net_throttle, restart,
                performed_on=performed_on
            )
        )
        if operation_id:
            msg = 'operation created'
            status_code = GenericCodes.ObjectCreated
            vfense_status_code = AgentOperationCodes.Created
            results[ApiResultKeys.GENERATED_IDS] = [operation_id]
            results[ApiResultKeys.GENERIC_STATUS_CODE] = status_code
            results[ApiResultKeys.VFENSE_STATUS_CODE] = vfense_status_code
            results[ApiResultKeys.MESSAGE] = msg

            for agent_id in agent_ids:
                valid_app_ids = (
                    return_valid_app_ids_for_agent(
                        app_ids, agent_id,
                        collection=self.CurrentAppsPerAgentCollection
                    )
                )

                pkg_data = []
                for app_id in valid_app_ids:
                    update_app_status_by_agentid_and_appid(
                        agent_id,
                        app_id,
                        CommonAppKeys.PENDING,
                        self.CurrentAppsPerAgentCollection
                    )

                    pkg_data.append(
                        self._get_apps_data(app_id, agent_id)
                    )

                operation_data = {
                    AgentOperationKey.Operation: oper_type,
                    AgentOperationKey.OperationId: operation_id,
                    AgentOperationKey.Plugin: oper_plugin,
                    AgentOperationKey.Restart: restart,
                    CommonFileKeys.PKG_FILEDATA: pkg_data,
                    OperationPerAgentKey.AgentId: agent_id,
                    AgentOperationKey.CpuThrottle: cpu_throttle,
                    AgentOperationKey.NetThrottle: net_throttle,
                }
                self._store_in_agent_queue(operation_data)
                operation.add_agent_to_install_operation(
                    agent_id, operation_id, pkg_data
                )

        else:
            msg = 'operation failed to create'
            status_code = GenericFailureCodes.FailedToCreateObject
            vfense_status_code = (
                AgentOperationFailureCodes.FailedToCreateOperation
            )
            results[ApiResultKeys.GENERATED_IDS] = [operation_id],
            results[ApiResultKeys.GENERIC_STATUS_CODE] = status_code
            results[ApiResultKeys.VFENSE_STATUS_CODE] = vfense_status_code
            results[ApiResultKeys.MESSAGE] = msg

        return results

    def _get_apps_data(self, app_id, agent_id):

        collection = self.CurrentAppsCollection
        pkg = (
            fetch_app_data_to_send_to_agent(
                app_id, agent_id, collection,
            )
        )
        uris = (
            get_download_urls(
                self.view_name, app_id, pkg[CommonFileKeys.PKG_FILEDATA]
            )
        )

        pkg_data = {
            CommonAppKeys.APP_NAME: pkg[DbCommonAppKeys.Name],
            CommonAppKeys.APP_VERSION: pkg[DbCommonAppKeys.Version],
            CommonAppKeys.APP_URIS: uris,
            CommonAppKeys.APP_ID: app_id,
            CommonFileKeys.PKG_CLI_OPTIONS: pkg[CommonFileKeys.PKG_CLI_OPTIONS]
        }

        return pkg_data
