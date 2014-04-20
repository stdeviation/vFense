import logging
import logging.config
from vFense.operations.agent_operations import AgentOperation
from vFense.operations import OperationPerAgentKey
from vFense.core.decorators import results_message
from vFense.core.queue.queue import AgentQueue
from vFense.core.tag.tagManager import *
from vFense.errorz._constants import ApiResultKeys
from vFense.errorz.status_codes import GenericCodes, AgentOperationCodes, \
    GenericFailureCodes, AgentOperationFailureCodes

logging.config.fileConfig('/opt/TopPatch/conf/logging.config')
logger = logging.getLogger('rvapi')

class StoreAgentOperation(object):
    def __init__(self, username, customer_name,
                 uri, method, server_queue_ttl=None,
                 agent_queue_ttl=None):
        self.customer_name = customer_name
        self.username = username
        self.uri = uri
        self.method = method
        self.server_queue_ttl = server_queue_ttl
        self.agent_queue_ttl = agent_queue_ttl

    def _store_in_agent_queue(self, operation):
        agent_queue = (
            AgentQueue(
                operation[OperationPerAgentKey.AgentId],
                self.customer_name
            )
        )
        agent_queue.add(operation, self.server_queue_ttl, self.agent_queue_ttl)

    @results_message
    def generic_operation(self, oper_type, oper_plugin,
                          agentids=None, tag_id=None):
        if tag_id:
            if not agentids:
                agentids = get_agent_ids_from_tag(tag_id)

            elif agentids:
                agentids += get_agent_ids_from_tag(tag_id)

        results = {
            ApiResultKeys.DATA: [],
            ApiResultKeys.USERNAME: self.username,
            ApiResultKeys.URI: self.uri,
            ApiResultKeys.HTTP_METHOD: self.method
        }

        operation = (
            AgentOperation(
                self.username, self.customer_name,
            )
        )

        operation_id = (
            operation.create_operation(
                oper_type, oper_plugin, agentids, tag_id
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

            for agent_id in agentids:
                operation_data = {
                    AgentOperationKey.Operation: oper_type,
                    AgentOperationKey.OperationId: operation_id,
                    AgentOperationKey.Plugin: oper_plugin,
                    OperationPerAgentKey.AgentId: agent_id,
                }
                self._store_in_agent_queue(operation_data)
                operation.add_agent_to_operation(agent_id, operation_id)

        else:
            msg = 'operation failed to create'
            status_code = GenericFailureCodes.FailedToCreateObject
            vfense_status_code = AgentOperationFailureCodes.FailedToCreateOperation
            results[ApiResultKeys.GENERATED_IDS] = [operation_id],
            results[ApiResultKeys.GENERIC_STATUS_CODE] = status_code
            results[ApiResultKeys.VFENSE_STATUS_CODE] = vfense_status_code
            results[ApiResultKeys.MESSAGE] = msg

        return(results)

