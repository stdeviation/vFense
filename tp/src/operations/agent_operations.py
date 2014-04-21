#!/usr/bin/env python

import logging
import logging.config
from datetime import datetime
from time import mktime
from vFense.operations import AgentOperationKey, OperationPerAgentKey
from vFense.operations._constants import vFenseObjects, OperationErrors
from vFense.operations._db_constants import DbTime
from vFense.operations._db_agent import fetch_agent_operation, \
    operation_with_agentid_exists, operation_with_agentid_and_appid_exists, \
    insert_into_agent_operations, update_agent_operation_expire_time, \
    update_operation_per_agent, update_agent_operation, \
    fetch_operation_with_agentid, update_failed_and_pending_count, \
    update_completed_and_pending_count, update_agent_operation_pickup_time, \
    insert_agent_into_agent_operations

from vFense.errorz.status_codes import DbCodes, AgentOperationCodes, \
    OperationPerAgentCodes


logging.config.fileConfig('/opt/TopPatch/conf/logging.config')
logger = logging.getLogger('rvapi')


def get_agent_operation(operation_id):
    """Get an operation by id and all of it's information
    Args:
        operation_id (str): 36 character UUID

    Basic Usage:
        >>> from vFense.operations.agent_operations import get_agent_operation
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
            "customer_name": "default"
        }
    """
    return(fetch_agent_operation(operation_id))


def operation_for_agent_exist(operation_id, agent_id):
    """Verify if the operation exists by operation id and agent id.
    Args:
        operation_id (str): 36 character UUID
        agent_id (str): 36 character UUID

    Basic Usage:
        >>> from vFense.operations.agent_operations import operation_for_agent_exist
        >>> operation_id = '8fed3dc7-33d4-4278-9bd4-398a68bf7f22'
        >>> agent_id = 'db6bf07-c5da-4494-93bb-109db205ca64'
        >>> operation_with_agentid_exists(operation_id, agent_id)

    Results:
        Boolean True or False
    """

    return(operation_with_agentid_exists(operation_id, agent_id))


def operation_for_agent_and_app_exist(operation_id, agent_id, app_id):
    """Verify if the operation exists by operation id, agent id and app id.
    Args:
        operation_id (str): 36 character UUID
        agent_id (str): 36 character UUID
        app_id (str): 36 character UUID

    Basic Usage:
        >>> from vFense.operations._db import operation_for_agent_and_app_exist
        >>> operation_id = '8fed3dc7-33d4-4278-9bd4-398a68bf7f22'
        >>> agent_id = 'db6bf07-c5da-4494-93bb-109db205ca64'
        >>> app_id = '70d462913faad1ecaa85eda4c448a607164fe39414c8be44405e7ab4f7f8467c'
        >>> operation_for_agent_and_app_exist(operation_id, agent_id, app_id)

    Results:
        Boolean True or False
    """
    return(
        operation_with_agentid_and_appid_exists(
            operation_id, agent_id, app_id
        )
    )


class AgentOperation(object):
    """This is what creates operations for an agent or multiple agents.

    """
    def __init__(self, username, customer_name):
        """
        Args:
            username (str): the name of the user who created the operation.
            customer_name (str): the name of the customer this user is part of.

        Basic Usage:
            >>> from vFense.operations.agent_operations import AgentOperation
            >>> username = 'admin'
            >>> customer_name = 'default'
            >>> oper = AgentOperation(username, customer_name)
        """
        self.username = username
        self.customer_name = customer_name
        self.now = mktime(datetime.now().timetuple())
        self.db_time = DbTime.time_now()
        self.INIT_COUNT = 0

    def create_operation(
        self, operation, plugin, agent_ids,
        tag_id, cpu_throttle=None, net_throttle=None,
        restart=None, performed_on=vFenseObjects.AGENT,
        ):
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
            >>> from vFense.operations.agent_operations import AgentOperation
            >>> username = 'admin'
            >>> customer_name = 'default'
            >>> oper = AgentOperation(username, customer_name)
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

        number_of_agents = len(agent_ids)
        keys_to_insert = (
            {
                AgentOperationKey.Plugin: plugin,
                AgentOperationKey.Operation: operation,
                AgentOperationKey.OperationStatus: AgentOperationCodes.ResultsIncomplete,
                AgentOperationKey.CustomerName: self.customer_name,
                AgentOperationKey.CreatedBy: self.username,
                AgentOperationKey.ActionPerformedOn: performed_on,
                AgentOperationKey.TagId: tag_id,
                AgentOperationKey.AgentIds: agent_ids,
                AgentOperationKey.AgentsTotalCount: number_of_agents,
                AgentOperationKey.AgentsExpiredCount: self.INIT_COUNT,
                AgentOperationKey.AgentsPendingResultsCount: self.INIT_COUNT,
                AgentOperationKey.AgentsPendingPickUpCount: number_of_agents,
                AgentOperationKey.AgentsFailedCount: self.INIT_COUNT,
                AgentOperationKey.AgentsCompletedCount: self.INIT_COUNT,
                AgentOperationKey.AgentsCompletedWithErrorsCount: self.INIT_COUNT,
                AgentOperationKey.CreatedTime: self.db_time,
                AgentOperationKey.UpdatedTime: self.db_time,
                AgentOperationKey.CompletedTime: DbTime.begining_of_time(),
                AgentOperationKey.Restart: restart,
                AgentOperationKey.CpuThrottle: cpu_throttle,
                AgentOperationKey.NetThrottle: net_throttle,
            }
        )
        status_code, count, errors, generated_ids = (
            insert_into_agent_operations(keys_to_insert)
        )
        if status_code == DbCodes.Inserted:
            operation_id = generated_ids[0]

        else:
            operation_id = None

        return(operation_id)


    def add_agent_to_operation(self, agent_id, operation_id):
        """Add an operation for an agent
        Args:
            agent_id (str): the agent id.
            operation_id (str): the operation id.

        Basic Usage:
            >>> from vFense.operations.agent_operations import AgentOperation
            >>> username = 'admin'
            >>> customer_name = 'default'
            >>> oper = AgentOperation(username, customer_name)
            >>> operation_id = '5dc03727-de89-460d-b2a7-7f766c83d2f1'
            >>> agent_id = '38c1c67e-436f-4652-8cae-f1a2ac2dd4a2'
            >>> oper.add_agent_to_operation(
                    agent_id, operation_id
                )

        Returns:
            36 character UUID of the operation that was created for the agent.
        """
        data_to_insert = {
            OperationPerAgentKey.AgentId: agent_id,
            OperationPerAgentKey.OperationId: operation_id,
            OperationPerAgentKey.CustomerName: self.customer_name,
            OperationPerAgentKey.Status: OperationPerAgentCodes.PendingPickUp,
            OperationPerAgentKey.PickedUpTime: DbTime.begining_of_time(),
            OperationPerAgentKey.ExpiredTime: DbTime.begining_of_time(),
            OperationPerAgentKey.CompletedTime: DbTime.begining_of_time(),
            OperationPerAgentKey.Errors: None
        }

        status_code, count, errors, generated_ids = (
            insert_agent_into_agent_operations(data_to_insert)
        )

        if status_code == DbCodes.Inserted:
            operation_id = generated_ids[0]

        else:
            operation_id = None

        return(operation_id)


    def update_operation_expire_time(self, operation_id, agent_id):
        """Expire the operation for agent id
        Args:
            operation_id (str): the operation id.
            agent_id (str): the agent id.

        Basic Usage:
            >>> from vFense.operations.agent_operations import AgentOperation
            >>> username = 'admin'
            >>> customer_name = 'default'
            >>> oper = AgentOperation(username, customer_name)
            >>> operation_id = '5dc03727-de89-460d-b2a7-7f766c83d2f1'
            >>> agent_id = '38c1c67e-436f-4652-8cae-f1a2ac2dd4a2'
            >>> oper.update_operation_expire_time(operation_id, agent_id)

        Returns:
            Boolean
        """
        completed = False
        operation_data = (
            {
                OperationPerAgentKey.Status: OperationPerAgentCodes.OperationExpired,
                OperationPerAgentKey.ExpiredTime: self.db_time,
                OperationPerAgentKey.CompletedTime: self.db_time,
                OperationPerAgentKey.Errors: OperationErrors.EXPIRED,
            }
        )

        status_code, count, errors, generated_ids = (
            update_operation_per_agent(operation_id, agent_id, operation_data)
        )
        if status_code == DbCodes.Replaced or status_code == DbCodes.Unchanged:
            status_code, count, errors, generated_ids = (
                update_agent_operation_expire_time(
                    operation_id, agent_id, self.db_time
                )
            )
            completed = True

        return(completed)

    def update_operation_pickup_time(self, operation_id, agent_id):
        """Update the pickup time for operation_id and agent id.
        Args:
            operation_id (str): the operation id.
            agent_id (str): the agent id.

        Basic Usage:
            >>> from vFense.operations.agent_operations import AgentOperation
            >>> username = 'admin'
            >>> customer_name = 'default'
            >>> oper = AgentOperation(username, customer_name)
            >>> operation_id = '5dc03727-de89-460d-b2a7-7f766c83d2f1'
            >>> agent_id = '38c1c67e-436f-4652-8cae-f1a2ac2dd4a2'
            >>> oper.update_operation_pickup_time(operation_id, agent_id)

        Returns:
            Boolean
        """
        completed = False
        operation_data = (
            {
                OperationPerAgentKey.Status: OperationPerAgentCodes.PickedUp,
                OperationPerAgentKey.PickedUpTime: self.db_time,
            }
        )

        status_code, count, errors, generated_ids = (
            update_operation_per_agent(operation_id, agent_id, operation_data)
        )
        if status_code == DbCodes.Replaced or status_code == DbCodes.Unchanged:
            status_code, count, errors, generated_ids = (
                update_agent_operation_pickup_time(
                    operation_id, agent_id, self.db_time
                )
            )
            completed = True

        return(completed)

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
            >>> from vFense.operations.agent_operations import AgentOperation
            >>> username = 'admin'
            >>> customer_name = 'default'
            >>> oper = AgentOperation(username, customer_name)
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
        operation_data = (
            {
                OperationPerAgentKey.Status: status,
                OperationPerAgentKey.CompletedTime: self.db_time,
                OperationPerAgentKey.Errors: errors
            }
        )

        status_code, count, errors, generated_ids = (
            update_operation_per_agent(operation_id, agent_id, operation_data)
        )
        if status_code == DbCodes.Replaced or status_code == DbCodes.Unchanged:
            self._update_agent_stats(operation_id, agent_id)
            self._update_operation_status_code(operation_id)
            completed = True

        return(completed)


    def _update_agent_stats(self, operation_id, agent_id):
        """Update the total counts based on the status code.
        Args:
            operation_id (str): the operation id.
            agent_id (str): the agent id.

        Basic Usage:
            >>> from vFense.operations.agent_operations import AgentOperation
            >>> username = 'admin'
            >>> customer_name = 'default'
            >>> oper = AgentOperation(username, customer_name)
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
            operation = fetch_operation_with_agentid(operation_id, agent_id)
            if (operation[OperationPerAgentKey.Status] ==
                    AgentOperationCodes.ResultsReceived):

                status_code, count, errors, generated_ids = (
                    update_completed_and_pending_count(
                        operation_id, self.db_time
                    )
                )
                if (status_code == DbCodes.Replaced or
                        status_code == DbCodes.Unchanged):

                    completed = True

            elif (operation[OperationPerAgentKey.Status] ==
                    AgentOperationCodes.ResultsReceivedWithErrors):


                status_code, count, errors, generated_ids = (
                    update_failed_and_pending_count(
                        operation_id, self.db_time
                    )
                )
                if (status_code == DbCodes.Replaced or
                        status_code == DbCodes.Unchanged):

                    completed = True

        return(completed)

    def _update_completed_time_on_agents(self, operation_id, agent_id):
        """Update the completed time for the agent operation.
        Args:
            operation_id (str): the operation id.
            agent_id (str): the agent id.

        Basic Usage:
            >>> from vFense.operations.agent_operations import AgentOperation
            >>> username = 'admin'
            >>> customer_name = 'default'
            >>> oper = AgentOperation(username, customer_name)
            >>> operation_id = '5dc03727-de89-460d-b2a7-7f766c83d2f1'
            >>> agent_id = '38c1c67e-436f-4652-8cae-f1a2ac2dd4a2'
            >>> oper._update_completed_time_on_agents(operation_id, agent_id)

        Returns:
            Boolean
        """
        completed = False
        data = {OperationPerAgentKey.CompletedTime: self.db_time}
        status_code, count, errors, generated_ids = (
            update_operation_per_agent(operation_id, agent_id, data)
        )

        if status_code == DbCodes.Replaced or status_code == DbCodes.Unchanged:
            completed = True

        return(completed)


    def _update_operation_status_code(self, operation_id):
        """Update the status code based on the following counts:
            total_completed_count, total_failed_count,
            and total_expired_count.
        Args:
            operation_id (str): the operation id.

        Basic Usage:
            >>> from vFense.operations.agent_operations import AgentOperation
            >>> username = 'admin'
            >>> customer_name = 'default'
            >>> oper = AgentOperation(username, customer_name)
            >>> operation_id = '5dc03727-de89-460d-b2a7-7f766c83d2f1'
            >>> oper._update_operation_status_code(operation_id)

        Returns:
            Boolean
        """
        operation = get_agent_operation(operation_id)
        operation_data = {}
        completed = False

        if (operation[AgentOperationKey.AgentsTotalCount] == 
            operation[AgentOperationKey.AgentsCompletedCount]):

            operation_data = {
                AgentOperationKey.OperationStatus: AgentOperationCodes.ResultsCompleted,
                AgentOperationKey.CompletedTime: self.db_time
            }

        elif (operation[AgentOperationKey.AgentsTotalCount] == 
            operation[AgentOperationKey.AgentsFailedCount]):

            operation_data = {
                AgentOperationKey.OperationStatus: AgentOperationCodes.ResultsCompletedFailed,
                AgentOperationKey.CompletedTime: self.db_time
            }

        elif (operation[AgentOperationKey.AgentsTotalCount] == 
            (
               operation[AgentOperationKey.AgentsFailedCount] +
               operation[AgentOperationKey.AgentsExpiredCount]
            )):

            operation_data = {
                AgentOperationKey.OperationStatus: AgentOperationCodes.ResultsCompletedFailed,
                AgentOperationKey.CompletedTime: self.db_time
            }

        elif (operation[AgentOperationKey.AgentsTotalCount] == 
            operation[AgentOperationKey.AgentsExpiredCount]):

            operation_data = {
                AgentOperationKey.OperationStatus: AgentOperationCodes.ResultsCompletedFailed,
                AgentOperationKey.CompletedTime: self.db_time
            }

        elif (operation[AgentOperationKey.AgentsTotalCount] == 
            (
                operation[AgentOperationKey.AgentsFailedCount] +
                operation[AgentOperationKey.AgentsCompletedWithErrorsCount]
            )):

            operation_data = {
                AgentOperationKey.OperationStatus: AgentOperationCodes.ResultsCompletedWithErrors,
                AgentOperationKey.CompletedTime: self.db_time
            }

        elif (operation[AgentOperationKey.AgentsTotalCount] == 
            (
                operation[AgentOperationKey.AgentsCompletedWithErrorsCount] +
                operation[AgentOperationKey.AgentsExpiredCount]
            )):

            operation_data = {
                AgentOperationKey.OperationStatus: AgentOperationCodes.ResultsCompletedWithErrors,
                AgentOperationKey.CompletedTime: self.db_time
            }

        elif (operation[AgentOperationKey.AgentsTotalCount] == 
            (
                operation[AgentOperationKey.AgentsFailedCount] +
                operation[AgentOperationKey.AgentsCompletedWithErrorsCount] +
                operation[AgentOperationKey.AgentsExpiredCount]
            )):

            operation_data = {
                AgentOperationKey.OperationStatus: AgentOperationCodes.ResultsCompletedWithErrors,
                AgentOperationKey.CompletedTime: self.db_time
            }

        else:
            operation_data = {
                AgentOperationKey.OperationStatus: AgentOperationCodes.ResultsIncomplete
            }

        if operation_data:
            status_code, count, errors, generated_ids = (
                update_agent_operation(operation_id, operation_data)
            )
            if (status_code == DbCodes.Replaced or
                    status_code == DbCodes.Unchanged):

                completed = True

        return(completed)
