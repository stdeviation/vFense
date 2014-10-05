import logging
import logging.config
from vFense import VFENSE_LOGGING_CONFIG
from copy import deepcopy
from vFense.core.operations._constants import vFenseObjects
from vFense.core.operations.agent_operations import AgentOperation
from vFense.core.operations._db_model import (
    OperationPerAgentKey, AgentOperationKey
)
from vFense.core.decorators import results_message
from vFense.core.queue.manager import AgentQueueManager
from vFense.core.tag._db import fetch_agent_ids_in_tag
from vFense.core.results import ApiResults
from vFense.core.status_codes import GenericCodes, GenericFailureCodes
from vFense.core.operations.status_codes import (
    AgentOperationCodes, AgentOperationFailureCodes
)

logging.config.fileConfig(VFENSE_LOGGING_CONFIG)
logger = logging.getLogger('rvapi')


class StoreAgentOperation(object):
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
            >>> store = StoreAgentOperation(username, view_name)
        """
        self.view_name = view_name
        self.username = username
        self.server_queue_ttl = server_queue_ttl
        self.agent_queue_ttl = agent_queue_ttl

    def _store_in_agent_queue(self, operation):
        """Add the operation inside of the agent queue collection
        Args:
            operation (AgentQueueOperation): The dictionary of the operation.
        """
        agent_queue = AgentQueueManager(operation.agent_id)
        agent_queue.add(
            operation, self.view_name, self.server_queue_ttl,
            self.agent_queue_ttl
        )

    def generic_operation(
            self, action, plugin, agentids=None,
            tag_id=None, custom_key=None, custom_value=None
        ):
        """This will do all the necessary work, to add the operation
            into the agent_queue. This method is to be used for operations
            that do not need any extra manipulation, in order to be added into
            the queue.
        Args:
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
            >>> from vFense.core.operations.store_agent_operation import StoreAgentOperation
            >>> username = 'admin'
            >>> view_name = 'default'
            >>> store = StoreAgentOperation(username, view_name)
            >>> store.generic_operation(
                    'reboot', 'core',
                    agentids=['33ba8521-b2e5-47dc-9bdc-0f1e3384049d']
                )

        Returns:
            Dictionary
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
        performed_on = vFenseObjects.AGENT
        if tag_id:
            performed_on = vFenseObjects.TAG
            if not agentids:
                agentids = fetch_agent_ids_in_tag(tag_id)

            elif agentids:
                agentids += fetch_agent_ids_in_tag(tag_id)

        results = ApiResults()
        results.fill_in_defaults()

        operation = (
            AgentOperation(
                self.username, self.view_name,
            )
        )

        operation_id = (
            operation.create_operation(
                action, plugin, agentids, tag_id,
                performed_on=performed_on
            )
        )
        if operation_id:
            msg = 'operation created'
            status_code = GenericCodes.ObjectCreated
            vfense_status_code = AgentOperationCodes.Created
            results.generated_ids = [operation_id]
            results.generic_status_code = status_code
            results.vfense_status_code = vfense_status_code
            results.message = msg

            for agent_id in agentids:
                operation_data = {
                    AgentOperationKey.Operation: action,
                    AgentOperationKey.OperationId: operation_id,
                    AgentOperationKey.Plugin: plugin,
                    OperationPerAgentKey.AgentId: agent_id,
                }
                if custom_key and custom_value:
                    operation_data[custom_key] = custom_value

                agent_data = deepcopy(operation_data)
                data.append(agent_data)
                self._store_in_agent_queue(operation_data)
                operation.add_agent_to_operation(agent_id, operation_id)

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
