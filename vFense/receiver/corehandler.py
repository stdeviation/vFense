import logging

from vFense._constants import VFENSE_LOGGING_CONFIG
from vFense.core.operations.agent_operations import AgentOperation
from vFense.core.operations._db_model import AgentOperationKey
from vFense.core.operations._constants import AgentOperations
from vFense.core.queue.manager import AgentQueueManager

logging.config.fileConfig(VFENSE_LOGGING_CONFIG)
logger = logging.getLogger('rvapi')

#process that data!!


def process_queue_data(agent_id):
    agent_queue = AgentQueueManager(agent_id).pop_agent_queue()
    for operation in agent_queue:
        if operation.get(AgentOperationKey.OperationId):
            oper = AgentOperation()
            oper.update_operation_pickup_time(
                operation[AgentOperationKey.OperationId], agent_id
            )

    return agent_queue
