import logging
import logging.config
from vFense.operations._constants import AgentOperations, vFensePlugins
from vFense.operations.store_agent_operation import StoreAgentOperation

logging.config.fileConfig('/opt/TopPatch/conf/logging.config')
logger = logging.getLogger('rvapi')

class StoreAgentOperations(StoreAgentOperation):
    def reboot(self, agentids=None, tag_id=None):
        results = (
            self.generic_operation(
                AgentOperations.REBOOT,
                vFensePlugins.CORE_PLUGIN,
                agentids, tag_id
            )
        )

        return(results)

    def shutdown(self, agentids=None, tag_id=None):
        results = (
            self.generic_operation(
                AgentOperations.SHUTDOWN,
                vFensePlugins.CORE_PLUGIN,
                agentids, tag_id
            )
        )

        return(results)
