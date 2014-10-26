#!/usr/bin/env python

from vFense import logging
from vFense.core.operations import (
    AgentOperation, OperPerAgent
)
from vFense.core.operations._constants import OperationErrors
from vFense.core._constants import Time
from vFense.core.operations._db_agent import fetch_agent_operation, \
    operation_with_agentid_exists, operation_with_agentid_and_appid_exists, \
    insert_into_agent_operations, update_agent_operation_expire_time, \
    update_operation_per_agent, update_agent_operation, \
    fetch_operation_with_agentid, update_failed_and_pending_count, \
    update_completed_and_pending_count, update_agent_operation_pickup_time, \
    insert_agent_into_agent_operations

from vFense.core.operations.status_codes import (
    AgentOperationCodes, OperationPerAgentCodes
)
from vFense.core.status_codes import (
    DbCodes
)


logger = logging.getLogger('rvapi')


def get_agent_operation(operation_id):
    """Get an operation by id and all of it's information
    Args:
        operation_id (str): 36 character UUID

    Basic Usage:
        >>> from vFense.core.operations.agent_operations import get_agent_operation
        >>> operation_id = '8fed3dc7-33d4-4278-9bd4-398a68bf7f22'
        >>> get_agent_operation(operation_id)

    Results:
        Dictionary
        {
            "agents_expired_count": 0,
            "cpu_throttle": "normal",
            "agents_total_count": 1,
            "plugin": "rv",
            "tag_id": null,
            "agents_completed_with_errors_count": 0,
            "created_by": "admin",
            "agents_pending_pickup_count": 0,
            "completed_time": 1397246851,
            "operation_status": 6006,
            "agents_completed_count": 1,
            "operation_id": "8fed3dc7-33d4-4278-9bd4-398a68bf7f22",
            "created_time": 1397246674,
            "agents_pending_results_count": 0,
            "operation": "install_os_apps",
            "updated_time": 1397246851,
            "net_throttle": 0,
            "agents_failed_count": 0,
            "restart": "none",
            "view_name": "default"
        }
    """
    return AgentOperation(**fetch_agent_operation(operation_id))

def operation_for_agent_exist(operation_id, agent_id):
    """Verify if the operation exists by operation id and agent id.
    Args:
        operation_id (str): 36 character UUID
        agent_id (str): 36 character UUID

    Basic Usage:
        >>> from vFense.core.operations.agent_operations import operation_for_agent_exist
        >>> operation_id = '8fed3dc7-33d4-4278-9bd4-398a68bf7f22'
        >>> agent_id = 'db6bf07-c5da-4494-93bb-109db205ca64'
        >>> operation_with_agentid_exists(operation_id, agent_id)

    Results:
        Boolean True or False
    """

    data = (
        operation_with_agentid_exists(operation_id, agent_id)
    )
    return data


def operation_for_agent_and_app_exist(operation_id, agent_id, app_id):
    """Verify if the operation exists by operation id, agent id and app id.
    Args:
        operation_id (str): 36 character UUID
        agent_id (str): 36 character UUID
        app_id (str): 36 character UUID

    Basic Usage:
        >>> from vFense.core.operations._db import operation_for_agent_and_app_exist
        >>> operation_id = '8fed3dc7-33d4-4278-9bd4-398a68bf7f22'
        >>> agent_id = 'db6bf07-c5da-4494-93bb-109db205ca64'
        >>> app_id = '70d462913faad1ecaa85eda4c448a607164fe39414c8be44405e7ab4f7f8467c'
        >>> operation_for_agent_and_app_exist(operation_id, agent_id, app_id)

    Results:
        Boolean True or False
    """
    data = (
        operation_with_agentid_and_appid_exists(
            operation_id, agent_id, app_id
        )
    )
    return data


class AgentOperationManager(object):
    """This is what creates operations for an agent or multiple agents.

    """
    def __init__(self, username=None, view_name=None):
        """
        Kwrgs:
            username (str): the name of the user who created the operation.
            view_name (str): the name of the view this user is part of.
                default=None

        Basic Usage:
            >>> from vFense.core.operations.agent_operations import AgentOperationManager
            >>> username = 'admin'
            >>> view_name = 'default'
            >>> oper = AgentOperationManager(username, view_name)
        """
        self.username = username
        self.view_name = view_name
        self.now = Time.now()
        self.INIT_COUNT = 0

    def create_operation(self, operation):
        """Create the base operation. Here is where the
            operation_id is generated.
        Args:
            operation (str): The operation (install_os_apps, reboot, etc..).
            plugin (str): The plugin this operation is from (rv, core, ra, erc..).
            agent_ids (list): List of agent ids, this operation is being performed on.
            tag_id (str): The tag id, that this operation is being performed on.

        Kwargs:
            cpu_throttle (str): The default is normal, do not throttle.
            net_throttle (int): The default is 0, do not throttle.
            restart (str): The default is none, do not restart.
            performed_on (str): The default is agent.

        Basic Usage:
            >>> from vFense.core.operations.agent_operations import AgentOperationManager
            >>> username = 'admin'
            >>> view_name = 'default'
            >>> oper = AgentOperationManager(username, view_name)
            >>> operation = 'reboot'
            >>> plugin = 'core'
            >>> agent_ids = ['38c1c67e-436f-4652-8cae-f1a2ac2dd4a2']
            >>> tag_id = None
            >>> performed_on = 'agent'
            >>> oper.create_operation(operation, plugin, agent_ids, tag_id)

        Returns:
            String The 36 character UUID of the operation that was created.
            6c0209d5-b350-48b7-808a-158ddacb6940
        """
        operation_id = None
        if isinstance(operation, AgentOperation):
            operation.fill_in_defaults()
            operation.agents_total_count = len(operation.agent_ids)
            operation.agents_pending_pickup_count = len(operation.agent_ids)
            operation.view_name = self.view_name
            operation.created_by = self.username
            status_code, count, errors, generated_ids = (
                insert_into_agent_operations(operation.to_dict_db())
            )
            if status_code == DbCodes.Inserted:
                operation_id = generated_ids[0]

        return operation_id


    def add_agent_to_operation(self, agent_id, operation_id):
        """Add an operation for an agent
        Args:
            agent_id (str): the agent id.
            operation_id (str): the operation id.

        Basic Usage:
            >>> from vFense.core.operations.agent_operations import AgentOperationManager
            >>> username = 'admin'
            >>> view_name = 'default'
            >>> oper = AgentOperationManager(username, view_name)
            >>> operation_id = '5dc03727-de89-460d-b2a7-7f766c83d2f1'
            >>> agent_id = '38c1c67e-436f-4652-8cae-f1a2ac2dd4a2'
            >>> oper.add_agent_to_operation(
                    agent_id, operation_id
                )

        Returns:
            36 character UUID of the operation that was created for the agent.
        """
        agent_operation_id = None
        operation = OperPerAgent()
        operation.fill_in_defaults()
        operation.agent_id = agent_id
        operation.operation_id = operation_id
        operation.view_name = self.view_name
        status_code, count, errors, generated_ids = (
            insert_agent_into_agent_operations(operation.to_dict_db())
        )

        if status_code == DbCodes.Inserted:
            agent_operation_id = generated_ids[0]

        return agent_operation_id


    def update_operation_expire_time(self, operation_id, agent_id):
        """Expire the operation for agent id
        Args:
            operation_id (str): the operation id.
            agent_id (str): the agent id.

        Basic Usage:
            >>> from vFense.core.operations.agent_operations import AgentOperationManager
            >>> username = 'admin'
            >>> view_name = 'default'
            >>> oper = AgentOperationManager(username, view_name)
            >>> operation_id = '5dc03727-de89-460d-b2a7-7f766c83d2f1'
            >>> agent_id = '38c1c67e-436f-4652-8cae-f1a2ac2dd4a2'
            >>> oper.update_operation_expire_time(operation_id, agent_id)

        Returns:
            Boolean
        """
        completed = False
        operation = OperPerAgent()
        operation.status = OperationPerAgentCodes.OperationExpired
        operation.expired_time = self.now
        operation.completed_time = self.now
        operation.errors = OperationErrors.EXPIRED

        status_code, count, errors, generated_ids = (
            update_operation_per_agent(
                operation_id, agent_id, operation.to_dict_db()
            )
        )
        if status_code == DbCodes.Replaced or status_code == DbCodes.Unchanged:
            status_code, count, errors, generated_ids = (
                update_agent_operation_expire_time(operation_id, self.now)
            )
            completed = True

        return completed

    def update_operation_pickup_time(self, operation_id, agent_id):
        """Update the pickup time for operation_id and agent id.
        Args:
            operation_id (str): the operation id.
            agent_id (str): the agent id.

        Basic Usage:
            >>> from vFense.core.operations.agent_operations import AgentOperationManager
            >>> username = 'admin'
            >>> view_name = 'default'
            >>> oper = AgentOperationManager(username, view_name)
            >>> operation_id = '5dc03727-de89-460d-b2a7-7f766c83d2f1'
            >>> agent_id = '38c1c67e-436f-4652-8cae-f1a2ac2dd4a2'
            >>> oper.update_operation_pickup_time(operation_id, agent_id)

        Returns:
            Boolean
        """
        completed = False
        operation = OperPerAgent()
        operation.status = OperationPerAgentCodes.PickedUp
        operation.picked_up_time = self.now
        status_code, count, errors, generated_ids = (
            update_operation_per_agent(
                operation_id, agent_id, operation.to_dict_db()
            )
        )
        if status_code == DbCodes.Replaced or status_code == DbCodes.Unchanged:
            status_code, count, errors, generated_ids = (
                update_agent_operation_pickup_time(operation_id, self.now)
            )
            completed = True

        return completed

    def update_operation_results(
            self, operation_id, agent_id,
            status, operation, errors=None,
        ):
        """Update the results for an operation.
        Args:
            operation_id (str): The operation id.
            agent_id (str): The agent id.
            status (int): The operation status code.
            operation (str): The operation type.

        Kwargs:
            errors (str): The error message, default is None.

        Basic Usage:
            >>> from vFense.core.operations.agent_operations import AgentOperationManager
            >>> username = 'admin'
            >>> view_name = 'default'
            >>> oper = AgentOperationManager(username, view_name)
            >>> operation_id = '5dc03727-de89-460d-b2a7-7f766c83d2f1'
            >>> agent_id = '38c1c67e-436f-4652-8cae-f1a2ac2dd4a2'
            >>> status_code = 6006
            >>> operation = 'install_os_apps'
            >>> oper.update_operation_results(
                    operation_id, agent_id, status_code, operation
                )

        Returns:
            Boolean
        """
        completed = False
        operation = OperPerAgent()
        operation.status = status
        operation.completed_time = self.now
        operation.errors = errors

        status_code, count, errors, generated_ids = (
            update_operation_per_agent(
                operation_id, agent_id, operation.to_dict_db()
            )
        )
        if status_code == DbCodes.Replaced or status_code == DbCodes.Unchanged:
            self._update_agent_stats(operation_id, agent_id)
            self._update_operation_status_code(operation_id)
            completed = True

        return completed

    def _update_agent_stats(self, operation_id, agent_id):
        """Update the total counts based on the status code.
        Args:
            operation_id (str): the operation id.
            agent_id (str): the agent id.

        Basic Usage:
            >>> from vFense.core.operations.agent_operations import AgentOperationManager
            >>> username = 'admin'
            >>> view_name = 'default'
            >>> oper = AgentOperationManager(username, view_name)
            >>> operation_id = '5dc03727-de89-460d-b2a7-7f766c83d2f1'
            >>> agent_id = '38c1c67e-436f-4652-8cae-f1a2ac2dd4a2'
            >>> oper._update_agent_stats(operation_id, agent_id)

        Returns:
            Boolean
        """
        completed = False
        agent_operation_exist = (
            operation_with_agentid_exists(operation_id, agent_id)
        )

        if agent_operation_exist:
            operation = (
                OperPerAgent(
                    **fetch_operation_with_agentid(operation_id, agent_id)
                )
            )
            if operation.status == AgentOperationCodes.ResultsReceived:
                status_code, count, errors, generated_ids = (
                    update_completed_and_pending_count(
                        operation_id, self.now
                    )
                )
                if (
                        status_code == DbCodes.Replaced or
                        status_code == DbCodes.Unchanged
                    ):

                    completed = True

            elif (
                    operation.status ==
                    AgentOperationCodes.ResultsReceivedWithErrors
                ):

                status_code, count, errors, generated_ids = (
                    update_failed_and_pending_count(
                        operation_id, self.now
                    )
                )
                if (
                        status_code == DbCodes.Replaced or
                        status_code == DbCodes.Unchanged
                    ):

                    completed = True

        return completed

    def _update_completed_time_on_agents(self, operation_id, agent_id):
        """Update the completed time for the agent operation.
        Args:
            operation_id (str): the operation id.
            agent_id (str): the agent id.

        Basic Usage:
            >>> from vFense.core.operations.agent_operations import AgentOperationManager
            >>> username = 'admin'
            >>> view_name = 'default'
            >>> oper = AgentOperationManager(username, view_name)
            >>> operation_id = '5dc03727-de89-460d-b2a7-7f766c83d2f1'
            >>> agent_id = '38c1c67e-436f-4652-8cae-f1a2ac2dd4a2'
            >>> oper._update_completed_time_on_agents(operation_id, agent_id)

        Returns:
            Boolean
        """
        completed = False
        data = OperPerAgent()
        data.completed_time = self.now
        status_code, count, errors, generated_ids = (
            update_operation_per_agent(
                operation_id, agent_id, data.to_dict_db()
            )
        )

        if status_code == DbCodes.Replaced or status_code == DbCodes.Unchanged:
            completed = True

        return completed


    def _update_operation_status_code(self, operation_id):
        """Update the status code based on the following counts:
            total_completed_count, total_failed_count,
            and total_expired_count.
        Args:
            operation_id (str): the operation id.

        Basic Usage:
            >>> from vFense.core.operations.agent_operations import AgentOperationManager
            >>> username = 'admin'
            >>> view_name = 'default'
            >>> oper = AgentOperationManager(username, view_name)
            >>> operation_id = '5dc03727-de89-460d-b2a7-7f766c83d2f1'
            >>> oper._update_operation_status_code(operation_id)

        Returns:
            Boolean
        """
        operation = get_agent_operation(operation_id)
        updated_oper = AgentOperation()
        completed = False

        if operation.agents_total_count == operation.agents.completed_count:
            updated_oper.operation_status = (
                AgentOperationCodes.ResultsCompleted
            )
            updated_oper.completed_time = self.now

        elif operation.agents_total_count == operation.agents.failed_count:
            updated_oper.operation_status = (
                AgentOperationCodes.ResultsCompletedFailed
            )
            updated_oper.completed_time = self.now

        elif operation.agents_total_count == operation.agents_expired_count:
            updated_oper.operation_status = (
                AgentOperationCodes.ResultsCompletedFailed
            )
            updated_oper.completed_time = self.now

        elif (
                operation.agents_total_count ==
                (
                    operation.agents.failed_count +
                    operation.agents_expired_count
                )
            ):
            updated_oper.operation_status = (
                AgentOperationCodes.ResultsCompletedFailed
            )
            updated_oper.completed_time = self.now

        elif (
                operation.agents_total_count ==
                (
                    operation.agents.failed_count +
                    operation.agents_completed_with_errors_count
                )
            ):
            updated_oper.operation_status = (
                AgentOperationCodes.ResultsCompletedWithErrors
            )
            updated_oper.completed_time = self.now

        elif (
                operation.agents_total_count ==
                (
                    operation.agents_completed_with_errors_count +
                    operation.agents.agents_expired_count
                )
            ):
            updated_oper.operation_status = (
                AgentOperationCodes.ResultsCompletedWithErrors
            )
            updated_oper.completed_time = self.now

        elif (
                operation.agents_total_count ==
                (
                    operation.agents_completed_with_errors_count +
                    operation.agents.agents_expired_count +
                    operation.agents.agents_failed_count
                )
            ):
            updated_oper.operation_status = (
                AgentOperationCodes.ResultsCompletedWithErrors
            )
            updated_oper.completed_time = self.now

        else:
            updated_oper.operation_status = (
                AgentOperationCodes.ResultsIncomplete
            )

        if updated_oper.operation_status:
            status_code, count, errors, generated_ids = (
                update_agent_operation(
                    operation_id, updated_oper.to_dict_db()
                )
            )
            if (
                    status_code == DbCodes.Replaced or
                    status_code == DbCodes.Unchanged):

                completed = True

        return completed
