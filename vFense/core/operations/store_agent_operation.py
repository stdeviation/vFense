import logging
import logging.config
from copy import deepcopy
from vFense import VFENSE_LOGGING_CONFIG
from vFense.core.operations import (
    AgentOperation, OperPerAgent, OperPerApp
)
from vFense.core.operations._constants import vFenseObjects
from vFense.core.operations.agent_operations import AgentOperationManager
from vFense.core.operations._db_model import (
    OperationPerAgentKey, AgentOperationKey
)
from vFense.core.queue import AgentQueueOperation
from vFense.core.queue.manager import AgentQueueManager
from vFense.core.tag._db import fetch_agent_ids_in_tag
from vFense.core.results import ApiResults
from vFense.core.status_codes import GenericCodes, GenericFailureCodes
from vFense.core.operations.status_codes import (
    AgentOperationCodes, AgentOperationFailureCodes
)

logging.config.fileConfig(VFENSE_LOGGING_CONFIG)
logger = logging.getLogger('rvapi')


class StoreAgentOperationManager(object):
    """This is the base class for storing operations in an agent"""
    def __init__(
            self, username, view_name, server_queue_ttl=None,
            agent_queue_ttl=None
        ):
        """
        Args:
            username (str): The name of the user who called this class
            view_name (str): The current logged in customer

        Kwargs:
            server_queue_ttl (int): The number of minutes,
                until the operation expires in the server queue.
            agent_queue_ttl (int): The number of minutes,
                until the operation expires in the agent queue.

        Attributes:
            view_name
            username
            server_queue_ttl
            agent_queue_ttl

        Basic Usage:
            >>> from vFense.core.operations.store_agent_operation import StoreAgentOperation
            >>> username = 'admin'
            >>> view_name = 'default'
            >>> store = StoreAgentOperationManager(username, view_name)
        """
        self.view_name = view_name
        self.username = username
        self.server_queue_ttl = server_queue_ttl
        self.agent_queue_ttl = agent_queue_ttl

    def _store_in_agent_queue(self, queue):
        """Add the operation inside of the agent queue collection
        Args:
            queue (AgentQueueOperation): An instance of AgentQueueOperation

        Basic Usage:
            >>> queue_data = AgentQueueOperation()
            >>> queue_data.agent_id = '7eb61902-fb4d-4892-b4db-4913552ec92d'
            >>> queue_data.operation =-'reboot'
            >>> queue_data.operation_id = '6c24e95c-da37-4ba8-b207-cb8e39a5d30e'
            >>> queue_data.plugin = 'core'
            >>> username = 'admin'
            >>> view = 'global'
            >>> operation = StoreAgentOperationManager(username, view)
            >>> operation._store_in_agent_queue(queue_data)

        Returns:
            Boolean (True|False)
        """
        agent_queue = AgentQueueManager(queue.agent_id)
        added = agent_queue.add(
            queue, self.view_name, self.server_queue_ttl,
            self.agent_queue_ttl
        )

        return added

    def generic_operation(self, operation):
        """This will do all the necessary work, to add the operation
            into the agent_queue. This method is to be used for operations
            that do not need any extra manipulation, in order to be added into
            the queue.
        Args:
            operation (Agentperation): An instance of AgentOperation
            action (str): This is the action that will be performed,
                on the agent.
                Examples.... reboot, shutdown, install_os_apps, etc..
            plugin (str): The plugin that this operation is for.
                Examples... core, rv, ra, vuln
        Kwargs:
            agentids (list): List of agent ids, this operation will
                be performed on.
            tag_id (str): The tag id that this operation will be performed on.
            custom_key (str): This is a custom key that you want to add
                to this operation.
                default=None
            custom_val (str|int|dict|list): The data you want to send back
                to the agent. This must be sent with custom_key.
                default=None

        Basic Usage:
            >>> from vFense.core.operations.store_agent_operation import StoreAgentOperationManager
            >>> username = 'admin'
            >>> view_name = 'default'
            >>> store = StoreAgentOperationManager(username, view_name)
            >>> operation = AgentOperation()
            >>> operation.agent_ids = [ '6c24e95c-da37-4ba8-b207-cb8e39a5d30e']
            >>> operation.operation = 'reboot'
            >>> operation.plugin = 'core'
            >>> operation.fill_in_defaults()
            >>> results = store.generic_operation(operation)

        Returns:
            Instance of ApiResults
            {
                "rv_status_code": 6000,
                "unchanged_ids": [],
                "generated_ids": [
                    "d5fb023c-82a0-4552-adc1-b3f83de7ae8a"
                ],
                "message": "operation created",
                "data": [
                    {
                        "operation_id": "d5fb023c-82a0-4552-adc1-b3f83de7ae8a",
                        "operation": "reboot",
                        "agent_id": "456404f1-b185-4f4f-8fb7-bfb21b3a5d53",
                        "plugin": "core"
                    }
                ],

            }
        """
        data = []
        operation.action_performed_on= vFenseObjects.AGENT
        if operation.tag_id:
            operation.action_performed_on = vFenseObjects.TAG
            if not operation.agent_ids:
                agentids = fetch_agent_ids_in_tag(operation.tag_id)

            elif agentids:
                agentids += fetch_agent_ids_in_tag(operation.tag_id)

        operation.agent_ids = agentids
        results = ApiResults()
        results.fill_in_defaults()

        manager = (
            AgentOperationManager(
                self.username, self.view_name,
            )
        )

        operation_id = operation.create_operation(operation)
        if operation_id:
            msg = 'operation created'
            status_code = GenericCodes.ObjectCreated
            vfense_status_code = AgentOperationCodes.Created
            results.generated_ids = [operation_id]
            results.generic_status_code = status_code
            results.vfense_status_code = vfense_status_code
            results.message = msg

            for agent_id in agentids:
                queue_data = AgentQueueOperation()
                queue_data.operation =-operation.operation
                queue_data.operation_id = operation_id
                queue_data.plugin = operation.plugin
                queue_data.agent_id = agent_id
                data.append(queue_data.to_dict_non_null())
                self._store_in_agent_queue(queue_data)
                manager.add_agent_to_operation(agent_id, operation_id)

            results.data = data

        else:
            msg = 'operation failed to create'
            status_code = GenericFailureCodes.FailedToCreateObject
            vfense_status_code = (
                AgentOperationFailureCodes.FailedToCreateOperation
            )
            results.generated_ids = [operation_id]
            results.generic_status_code = status_code
            results.vfense_status_code = vfense_status_code
            results.message = msg
            results.data = data

        return results
