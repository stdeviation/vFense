import logging
import logging.config
from vFense.utils.common import *
from vFense.operations.agent_operations import AgentOperation
from vFense.operations import *
from vFense.operations._constants import AdminActions, vFenseObjects
from vFense.core.agent import *
from vFense.core.queue.queue import AgentQueue
from vFense.core.tag.tagManager import *

logging.config.fileConfig('/opt/TopPatch/conf/logging.config')
logger = logging.getLogger('rvapi')


class StoreAgentOperation(object):
    def __init__(self, agent_ids=None, tag_id=None,
                 username=None, customer_name=None,
                 uri=None, method=None, server_queue_ttl=None,
                 agent_queue_ttl=None):

        self.customer_name = customer_name
        self.username = username
        self.uri = uri
        self.method = method
        self.server_queue_ttl = server_queue_ttl
        self.agent_queue_ttl = agent_queue_ttl
        if tag_id:
            self.action_performed_on = vFenseObjects.TAG
            if not agentids:
                agent_ids = get_agent_ids_from_tag(tag_id)
            elif agent_ids:
                agent_ids += get_agent_ids_from_tag(tag_id)
        else:
            self.action_performed_on = vFenseObjects.AGENT

    def _store_in_agent_queue(self, operation):
        agent_queue = (
            AgentQueue(
                operation[OperationPerAgentKey.AgentId],
                self.customer_name
            )
        )
        agent_queue.add(
            operation,
            self.server_queue_ttl,
            self.agent_queue_ttl
        )

    def generic_operation(self, oper_type, oper_plugin):

        operation = (
            AgentOperation(
                self.username, self.customer_name,
                self.uri, self.method
            )
        )

        results = (
            operation.create_operation(
                oper_type, oper_plugin, agentids, tag_id
            )
        )

        operation_id = results['data'].get('operation_id', None)
        if operation_id:
            for agent_id in self.agent_ids:
                operation_data = {
                    OperationKey.Operation: oper_type,
                    OperationKey.OperationId: operation_id,
                    OperationKey.Plugin: oper_plugin,
                    OperationPerAgentKey.AgentId: agent_id,
                }
                self._store_in_agent_queue(operation_data)
                operation.add_agent_to_operation(agent_id, operation_id)

        return(results)

