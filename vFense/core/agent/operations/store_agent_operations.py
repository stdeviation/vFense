import logging
import logging.config
from vFense import VFENSE_LOGGING_CONFIG
from vFense.core.operations._constants import AgentOperations, vFensePlugins
from vFense.core.operations.store_agent_operation import (
    StoreAgentOperationManager
)

logging.config.fileConfig(VFENSE_LOGGING_CONFIG)
logger = logging.getLogger('rvapi')

class StoreAgentOperations(StoreAgentOperationManager):

    def uninstall_agent(self, agent_operation):
        agent_operation.operation = AgentOperations.UNINSTALL_AGENT
        agent_operation.plugin = vFensePlugins.CORE_PLUGIN
        agent_operation.fill_in_defaults()
        results = self.generic_operation(agent_operation)
        return results

    def reboot(self, agent_operation):
        agent_operation.operation = AgentOperations.REBOOT
        agent_operation.plugin = vFensePlugins.CORE_PLUGIN
        agent_operation.fill_in_defaults()
        results = self.generic_operation(agent_operation)
        return results

    def shutdown(self, agent_operation):
        agent_operation.operation = AgentOperations.SHUTDOWN
        agent_operation.plugin = vFensePlugins.CORE_PLUGIN
        agent_operation.fill_in_defaults()
        results = self.generic_operation(agent_operation)
        return results

    def new_token(self, agent_operation):
        agent_operation.operation = AgentOperations.NEW_TOKEN
        agent_operation.plugin = vFensePlugins.CORE_PLUGIN
        agent_operation.fill_in_defaults()
        results = self.generic_operation(agent_operation)
        return results
