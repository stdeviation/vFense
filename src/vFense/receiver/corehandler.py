import logging

from vFense import VFENSE_LOGGING_CONFIG
from vFense.core.operations.agent_operations import AgentOperation
from vFense.core.operations._db_model import AgentOperationKey
from vFense.core.operations._constants import AgentOperations
from vFense.core.queue.queue import AgentQueue

logging.config.fileConfig(VFENSE_LOGGING_CONFIG)
logger = logging.getLogger('rvapi')

#process that data!!


def process_queue_data(agent_id, username, view_name, uri, method):
    agent_queue = AgentQueue(agent_id, view_name).pop_agent_queue()
    for operation in agent_queue:
        if operation.get(AgentOperationKey.OperationId):
            oper = (
                AgentOperation(
                    username, view_name
                )
            )
            oper.update_operation_pickup_time(
                operation[AgentOperationKey.OperationId], agent_id
            )

    return agent_queue
