import logging

from vFense._constants import VFENSE_LOGGING_CONFIG
from vFense.core.operations.agent_operations import AgentOperationManager
from vFense.core.queue import AgentQueue
from vFense.core.queue.manager import AgentQueueManager

logging.config.fileConfig(VFENSE_LOGGING_CONFIG)
logger = logging.getLogger('rvapi')


def process_queue_data(agent_id):
    agent_queue = AgentQueueManager(agent_id).pop_agent_queue()
    for operation in agent_queue:
        operation = AgentQueue(**operation)
        if operation.operation_id:
            oper = AgentOperationManager()
            oper.update_operation_pickup_time(
                operation.operation_id, agent_id
            )

    return agent_queue
