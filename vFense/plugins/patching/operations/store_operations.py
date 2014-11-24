import logging
import logging.config
from vFense._constants import VFENSE_LOGGING_CONFIG
from vFense.core.operations import AgentOperation
from vFense.core.operations._constants import (
    AgentOperations, vFensePlugins, vFenseObjects
)
from vFense.core.operations.store_agent_operation import (
    StoreAgentOperationManager
)
from vFense.core.tag._db import fetch_agent_ids_in_tag
from vFense.core.results import ApiResults
from vFense.core.operations.status_codes import (
    AgentOperationCodes, AgentOperationFailureCodes
)
from vFense.plugins.patching import AgentAppData
from vFense.plugins.patching.queue import InstallQueueOperation
from vFense.plugins.patching._constants import CommonAppKeys
from vFense.plugins.patching.operations.patching_operations import (
    PatchingOperation
)
from vFense.plugins.patching.operations import Install
from vFense.plugins.patching._db_model import (
    AppCollections, DbCommonAppKeys, DbCommonAppPerAgentKeys
)
from vFense.plugins.patching._db import (
    fetch_app_data_to_send_to_agent, return_valid_appids_for_agent
)
from vFense.plugins.patching.patching import (
    get_download_urls, update_app_status_by_agentid_and_appid
)

logging.config.fileConfig(VFENSE_LOGGING_CONFIG)
logger = logging.getLogger('vfense_api')


class StorePatchingOperation(StoreAgentOperationManager):
    """Create operations for the patching plugin"""
    def refresh_apps(self, agent_operation):
        """Send the refresh_apps operation to the agent,
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
        agent_operation.operation = AgentOperations.REFRESH_APPS
        agent_operation.plugin = vFensePlugins.RV_PLUGIN
        agent_operation.fill_in_defaults()
        results = self.generic_operation(agent_operation)
        return results


    def install_os_apps(self, install):
        """Send the install_os_apps operation to the agent,
            This will install a list of applications on n
            number of agents or tag id.

        Args:
            install (Install): An instance of install.

        Basic Usage:
            >>> from vFense.plugins.patching.operations.store_operations import StorePatchingOperation
            >>> from vFense.plugins.patching.operations import Install
            >>> username = 'admin'
            >>> view_name = 'default'
            >>> app_ids = ['000bd2abd0f5197612dad031eb5d04abc082aba1b904b801c7b2d7925ac248a3']
            >>> reboot = 'needed'
            >>> cpu = 'high'
            >>> net = 100
            >>> agent_ids = ['e9a8871a-5ae8-40fb-9316-b0918947f736']
            >>> install = Install(app_ids, agent_ids, username, view_name, reboot, net, cpu)
            >>> operation = StorePatchingOperation(username, view_name)
            >>> operation.install_os_apps(install)

        Returns:
        """
        oper_type = AgentOperations.INSTALL_OS_APPS

        self.CurrentAppsCollection = AppCollections.UniqueApplications
        self.CurrentAppsKey = DbCommonAppKeys
        self.CurrentAppsPerAgentCollection = AppCollections.AppsPerAgent
        self.CurrentAppsPerAgentKey = DbCommonAppPerAgentKeys
        if isinstance(install, Install):
            results = self.install_apps(install, oper_type)

        else:
            results = ApiResults()
            results.fill_in_defaults()
            msg = (
                'Invalid instance {0}, please pass an instance of Install'
                .format(type(install))
            )
            status_code = AgentOperationFailureCodes.FailedToCreateObject
            vfense_status_code = (
                AgentOperationFailureCodes.FailedToCreateOperation
            )
            results.generated_ids = []
            results.generic_status_code = status_code
            results.vfense_status_code = vfense_status_code
            results.message = msg

        return results

    def install_custom_apps(self, install):
        """Send the install_custom_apps operation to the agent,
            This will install a list of applications on n
            number of agents or tag id.

        Args:
            install (Install): An instance of install.

        Basic Usage:
            >>> from vFense.plugins.patching.operations.store_operations import StorePatchingOperation
            >>> from vFense.plugins.patching.operations import Install
            >>> username = 'admin'
            >>> view_name = 'default'
            >>> app_ids = ['000bd2abd0f5197612dad031eb5d04abc082aba1b904b801c7b2d7925ac248a3']
            >>> reboot = 'needed'
            >>> cpu = 'high'
            >>> net = 100
            >>> agent_ids = ['e9a8871a-5ae8-40fb-9316-b0918947f736']
            >>> install = Install(app_ids, agent_ids, username, view_name, reboot, net, cpu)
            >>> operation = StorePatchingOperation(username, view_name)
            >>> operation.install_custom_apps(install)

        Returns:

        """
        oper_type = AgentOperations.INSTALL_CUSTOM_APPS

        self.CurrentAppsCollection = AppCollections.CustomApps
        self.CurrentAppsKey = DbCommonAppKeys
        self.CurrentAppsPerAgentCollection = AppCollections.CustomAppsPerAgent
        self.CurrentAppsPerAgentKey = DbCommonAppPerAgentKeys

        if isinstance(install, Install):
            results = self.install_apps(install, oper_type)

        else:
            results = ApiResults()
            results.fill_in_defaults()
            msg = (
                'Invalid instance {0}, please pass an instance of Install'
                .format(type(install))
            )
            status_code = AgentOperationFailureCodes.FailedToCreateObject
            vfense_status_code = (
                AgentOperationFailureCodes.FailedToCreateOperation
            )
            results.generated_ids = []
            results.generic_status_code = status_code
            results.vfense_status_code = vfense_status_code
            results.message = msg


    def install_supported_apps(self, install):
        """Send the install_supported_apps operation to the agent,
            This will install a list of supported applications on n
            number of agents or tag id.

        Args:
            install (Install): An instance of install.

        Basic Usage:
            >>> from vFense.plugins.patching.operations.store_operations import StorePatchingOperation
            >>> from vFense.plugins.patching.operations import Install
            >>> username = 'admin'
            >>> view_name = 'default'
            >>> app_ids = ['000bd2abd0f5197612dad031eb5d04abc082aba1b904b801c7b2d7925ac248a3']
            >>> reboot = 'needed'
            >>> cpu = 'high'
            >>> net = 100
            >>> agent_ids = ['e9a8871a-5ae8-40fb-9316-b0918947f736']
            >>> install = Install(app_ids, agent_ids, username, view_name, reboot, net, cpu)
            >>> operation = StorePatchingOperation(username, view_name)
            >>> operation.install_supported_apps(install)

        Returns:

        """

        oper_type = AgentOperations.INSTALL_SUPPORTED_APPS

        self.CurrentAppsCollection = AppCollections.SupportedApps
        self.CurrentAppsKey = DbCommonAppKeys
        self.CurrentAppsPerAgentCollection = AppCollections.SupportedAppsPerAgent
        self.CurrentAppsPerAgentKey = DbCommonAppPerAgentKeys

        if isinstance(install, Install):
            results = self.install_apps(install, oper_type)

        else:
            results = ApiResults()
            results.fill_in_defaults()
            msg = (
                'Invalid instance {0}, please pass an instance of Install'
                .format(type(install))
            )
            status_code = AgentOperationFailureCodes.FailedToCreateObject
            vfense_status_code = (
                AgentOperationFailureCodes.FailedToCreateOperation
            )
            results.generated_ids = []
            results.generic_status_code = status_code
            results.vfense_status_code = vfense_status_code
            results.message = msg


    def install_agent_update(self, install):
        """Send the install_agent_update operation to the agent,
            This will install the agent update on n
            number of agents or tag id.

        Args:
            install (Install): An instance of install.

        Basic Usage:
            >>> from vFense.plugins.patching.operations.store_operations import StorePatchingOperation
            >>> from vFense.plugins.patching.operations import Install
            >>> username = 'admin'
            >>> view_name = 'default'
            >>> app_ids = ['000bd2abd0f5197612dad031eb5d04abc082aba1b904b801c7b2d7925ac248a3']
            >>> reboot = 'needed'
            >>> cpu = 'high'
            >>> net = 100
            >>> agent_ids = ['e9a8871a-5ae8-40fb-9316-b0918947f736']
            >>> install = Install(app_ids, agent_ids, username, view_name, reboot, net, cpu)
            >>> operation = StorePatchingOperation(username, view_name)
            >>> operation.install_agent_update(install)

        Returns:

        """

        oper_type = AgentOperations.INSTALL_AGENT_UPDATE

        self.CurrentAppsCollection = AppCollections.vFenseApps
        self.CurrentAppsKey = DbCommonAppKeys
        self.CurrentAppsPerAgentCollection = AppCollections.vFenseAppsPerAgent
        self.CurrentAppsPerAgentKey = DbCommonAppPerAgentKeys

        if isinstance(install, Install):
            results = self.install_apps(install, oper_type)

        else:
            results = ApiResults()
            results.fill_in_defaults()
            msg = (
                'Invalid instance {0}, please pass an instance of Install'
                .format(type(install))
            )
            status_code = AgentOperationFailureCodes.FailedToCreateObject
            vfense_status_code = (
                AgentOperationFailureCodes.FailedToCreateOperation
            )
            results.generated_ids = []
            results.generic_status_code = status_code
            results.vfense_status_code = vfense_status_code
            results.message = msg


    def uninstall_apps(self, install):
        """Send the uninstall_apps operation to the agent,
            This will uninstall the applications from n
            number of agents or tag id.

        Args:
            install (Install): An instance of install.

        Basic Usage:
            >>> from vFense.plugins.patching.operations.store_operations import StorePatchingOperation
            >>> from vFense.plugins.patching.operations import Install
            >>> username = 'admin'
            >>> view_name = 'default'
            >>> app_ids = ['000bd2abd0f5197612dad031eb5d04abc082aba1b904b801c7b2d7925ac248a3']
            >>> reboot = 'needed'
            >>> cpu = 'high'
            >>> net = 100
            >>> agent_ids = ['e9a8871a-5ae8-40fb-9316-b0918947f736']
            >>> install = Install(app_ids, agent_ids, username, view_name, reboot, net, cpu)
            >>> operation = StorePatchingOperation(username, view_name)
            >>> results = operation.uninstall_apps(install)

        Returns:
            >>> results.message
            u'install_os_apps operation created: 3b6150ae-a143-4134-8338-a5aa65fa9e47'

        Returns:
            ApiResults instance
            Check vFense.core.results for all the attributes and methods
            for the instance.

        """

        oper_type = AgentOperations.UNINSTALL

        self.CurrentAppsCollection = AppCollections.UniqueApplications
        self.CurrentAppsKey = DbCommonAppKeys
        self.CurrentAppsPerAgentCollection = AppCollections.AppsPerAgent
        self.CurrentAppsPerAgentKey = DbCommonAppPerAgentKeys

        if isinstance(install, Install):
            results = self.install_apps(install, oper_type)

        else:
            results = ApiResults()
            results.fill_in_defaults()
            msg = (
                'Invalid instance {0}, please pass an instance of Install'
                .format(type(install))
            )
            status_code = AgentOperationFailureCodes.FailedToCreateObject
            vfense_status_code = (
                AgentOperationFailureCodes.FailedToCreateOperation
            )
            results.generated_ids = []
            results.generic_status_code = status_code
            results.vfense_status_code = vfense_status_code
            results.message = msg


    def install_apps(self, install, oper_type):
        """This method creates the operation and stores it into the agent queue.
        Args:
            install (Install): An instance of Install.
            oper_type (str): The operation type,
                etc.. install_os_apps, uninstall
        """

        oper_plugin = vFensePlugins.RV_PLUGIN
        results = ApiResults()
        results.fill_in_defaults()

        performed_on = vFenseObjects.AGENT
        if install.tag_id:
            performed_on = vFenseObjects.TAG
            if not install.agent_ids:
                install.agent_ids = fetch_agent_ids_in_tag(install.tag_id)
            else:
                install.agent_ids += fetch_agent_ids_in_tag(install.tag_id)

        manager = PatchingOperation(self.username, self.view_name)
        operation = AgentOperation()
        operation.fill_in_defaults()
        operation.tag_id = install.tag_id
        operation.operation = oper_type
        operation.agent_ids = install.agent_ids
        operation.cpu_throttle = install.cpu_throttle
        operation.net_throttle = install.net_throttle
        operation.plugin = oper_plugin
        operation.performed_on = performed_on
        operation_id = manager.create_operation(operation)
        if operation_id:
            msg = (
                '{0} operation created, operation_id: {1}'
                .format(oper_type, operation_id)
            )
            status_code = AgentOperationCodes.ObjectCreated
            vfense_status_code = AgentOperationCodes.Created
            results.generated_ids.append(operation_id)
            results.generic_status_code = status_code
            results.vfense_status_code = vfense_status_code
            results.message = msg

            for agent_id in install.agent_ids:
                valid_app_ids = (
                    return_valid_appids_for_agent(
                        install.app_ids, agent_id,
                        collection=self.CurrentAppsPerAgentCollection
                    )
                )

                pkg_data = []
                for app_id in valid_app_ids:
                    update_app_status_by_agentid_and_appid(
                        agent_id, app_id, CommonAppKeys.PENDING,
                        self.CurrentAppsPerAgentCollection
                    )

                    pkg_data.append(self._get_apps_data(app_id, agent_id))

                agent_queue = InstallQueueOperation()
                agent_queue.operation = oper_type
                agent_queue.operation_id = operation_id
                agent_queue.plugin = oper_plugin
                agent_queue.agent_id = agent_id
                agent_queue.restart = install.restart
                agent_queue.file_data = pkg_data
                agent_queue.cpu_throttle = install.cpu_throttle
                agent_queue.net_throttle = install.net_throttle

                self._store_in_agent_queue(agent_queue)
                manager.add_agent_to_install_operation(
                    agent_id, operation_id, pkg_data
                )

        else:
            msg = '{0} operation failed to create'.format(oper_type)
            status_code = AgentOperationFailureCodes.FailedToCreateObject
            vfense_status_code = (
                AgentOperationFailureCodes.FailedToCreateOperation
            )
            results.generated_ids.append(operation_id)
            results.generic_status_code = status_code
            results.vfense_status_code = vfense_status_code
            results.message = msg

        return results

    def _get_apps_data(self, app_id, agent_id):

        collection = self.CurrentAppsCollection
        data = (
            fetch_app_data_to_send_to_agent(
                app_id, agent_id, collection,
            )
        )
        uris = (
            get_download_urls(
                self.view_name, app_id, data.file_data
            )
        )
        app_data = AgentAppData()
        app_data.app_id = app_id
        app_data.app_name = data.name
        app_data.app_version = data.version
        app_data.app_uris = uris
        app_data.cli_options = data.cli_options

        return app_data
