#!/usr/bin/env python

import logging
import logging.config
from datetime import datetime
from time import mktime
from vFense.db.client import r
from vFense.operations import *
from vFense.operations._constants import vFenseObjects
from vFense.operations._db_constants import DbTime
from vFense.operations._db_agent import fetch_agent_operation, \
    operation_with_agentid_exists, operation_with_agentid_and_appid_exists, \
    insert_into_agent_operations, update_agent_operation_expire_time, \
    update_operation_per_agent, group_operations_per_app_by_results, \
    update_operation_per_app

from vFense.errorz.status_codes import DbCodes,AgentOperationCodes


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


def operation_for_agent_and_app_exist(oper_id, agent_id, app_id):
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
        """
        self.username = username
        self.customer_name = customer_name
        self.now = mktime(datetime.now().timetuple())
        self.db_time = DbTime.time_now
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

        Returns:
            String The 36 character UUID of the operation that was created.
        """

        number_of_agents = len(agent_ids)
        keys_to_insert = (
            {
                OperationKey.Plugin: plugin,
                OperationKey.Operation: operation,
                OperationKey.OperationStatus: AgentOperationCodes.ResultsIncomplete,
                OperationKey.CustomerName: self.customer_name,
                OperationKey.CreatedBy: self.username,
                OperationKey.ActionPerformedOn: performed_on,
                OperationKey.TagId: tag_id,
                OperationKey.AgentsTotalCount: number_of_agents,
                OperationKey.AgentsExpiredCount: self.INIT_COUNT,
                OperationKey.AgentsPendingResultsCount: self.INIT_COUNT,
                OperationKey.AgentsPendingPickUpCount: number_of_agents,
                OperationKey.AgentsFailedCount: self.INIT_COUNT,
                OperationKey.AgentsCompletedCount: self.INIT_COUNT,
                OperationKey.AgentsCompletedWithErrorsCount: self.INIT_COUNT,
                OperationKey.CreatedTime: self.db_time,
                OperationKey.UpdatedTime: self.db_time,
                OperationKey.CompletedTime: DbTime.begining_of_time,
                OperationKey.Restart: restart,
                OperationKey.CpuThrottle: cpu_throttle,
                OperationKey.NetThrottle: net_throttle,
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
            Boolean
        """
        data_to_insert = {
            OperationPerAgentKey.AgentId: agent_id,
            OperationPerAgentKey.OperationId: operation_id,
            OperationPerAgentKey.CustomerName: self.customer_name,
            OperationPerAgentKey.Status: PENDINGPICKUP,
            OperationPerAgentKey.PickedUpTime: DbTime.begining_of_time,
            OperationPerAgentKey.ExpiredTime: DbTime.begining_of_time,
            OperationPerAgentKey.CompletedTime: DbTime.begining_of_time,
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


    def add_agent_to_install_operation(
        self, agent_id, operation_id, applications
        ):
        """Add an install operation for an agent
        Args:
            agent_id (str): the agent id.
            operation_id (str): the operation id.
            applications (list): List of application dictionairies.

        Basic Usage:
            >>> from vFense.operations.agent_operations import AgentOperation
            >>> username = 'admin'
            >>> customer_name = 'default'
            >>> oper = AgentOperation(username, customer_name)
            >>> operation_id = '5dc03727-de89-460d-b2a7-7f766c83d2f1'
            >>> agent_id = '38c1c67e-436f-4652-8cae-f1a2ac2dd4a2'
            >>> applications = [
                    {
                        'app_id': '70d462913faad1ecaa85eda4c448a607164fe39414c8be44405e7ab4f7f8467c',
                        'app_name': 'linux-firmware'
                    }
                ]
            >>> oper.add_agent_to_install_operation(
                    agent_id, operation_id, applications
                )

        Returns:
            Boolean
        """
        completed = False
        operation_data = {
            OperationPerAgentKey.AgentId: agent_id,
            OperationPerAgentKey.OperationId: operation_id,
            OperationPerAgentKey.CustomerName: self.customer_name,
            OperationPerAgentKey.Status: PENDINGPICKUP,
            OperationPerAgentKey.PickedUpTime: DbTime.begining_of_time,
            OperationPerAgentKey.ExpiredTime: DbTime.begining_of_time,
            OperationPerAgentKey.CompletedTime: DbTime.begining_of_time,
            OperationPerAgentKey.AppsTotalCount: len(applications),
            OperationPerAgentKey.AppsPendingCount: len(applications),
            OperationPerAgentKey.AppsFailedCount: self.INIT_COUNT,
            OperationPerAgentKey.AppsCompletedCount: self.INIT_COUNT,
            OperationPerAgentKey.Errors: None
        }

        status_code, count, errors, generated_ids = (
            insert_agent_into_agent_operations(operation_data)
        )
        if status_code == DbCodes.Inserted:
            apps = []
            for app in applications:
                apps.append(
                    {
                        OperationPerAppKey.AgentId: agent_id,
                        OperationPerAppKey.OperationId: operation_id,
                        OperationPerAppKey.CustomerName: self.customer_name,
                        OperationPerAppKey.Results: AgentOperationCodes.ResultsPending,
                        OperationPerAppKey.ResultsReceivedTime: DbTime.begining_of_time,
                        OperationPerAppKey.AppId: app[OperationPerAppKey.AppId],
                        OperationPerAppKey.AppName: app[OperationPerAppKey.AppName],
                        OperationPerAppKey.Errors: None
                    }
                )

            status_code, count, errors, generated_ids = (
                insert_app_into_agent_operations(apps)
            )
            if status_code == DbCodes.Inserted:
                completed = True

        return(completed)


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
                OperationPerAgentKey.Status: OPERATION_EXPIRED,
                OperationPerAgentKey.ExpiredTime: self.db_time,
                OperationPerAgentKey.CompletedTime: self.db_time,
                OperationPerAgentKey.Errors: OPERATION_EXPIRED,
            }
        )

        status_code, count, errors, generated_ids = (
            update_operation_per_agent(operation_id, operation_data)
        )
        if status_code == DbCodes.Replaced:
            status_code, count, errors, generated_ids = (
                update_agent_operation_expire_time(
                    operation_id, operation_data, self.db_time
                )
            )
            if status_code == DbCodes.Replaced:
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
                OperationPerAgentKey.Status: PICKEDUP,
                OperationPerAgentKey.PickedUpTime: self.db_time,
            }
        )

        status_code, count, errors, generated_ids = (
            update_operation_per_agent(operation_id, operation_data)
        )
        if status_code == DbCodes.Replaced:
            status_code, count, errors, generated_ids = (
                update_agent_operation_pickup_time(
                    operation_id, operation_data, self.db_time
                )
            )
            if status_code == DbCodes.Replaced:
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
            update_operation_per_agent(operation_id, operation_data)
        )

        if status_code == DbCodes.Replaced:
            self._update_agent_stats(operation_id, agent_id)
            self._update_operation_status_code(operation_id)
            completed = True

        return(completed)


    def update_app_results(
        self, operation_id, agent_id, app_id,
        status=AgentOperationCodes.ResultsReceived,
        errors=None
        ):
        """Update the results for an application.
        Args:
            operation_id (str): The operation id.
            agent_id (str): The agent id.
            app_id (str): The application id.
            status (int): The operation status code.
        
        Kwargs:
            errors (str): The error message, default is None.

        Basic Usage:
            >>> from vFense.operations.agent_operations import AgentOperation
            >>> username = 'admin'
            >>> customer_name = 'default'
            >>> oper = AgentOperation(username, customer_name)
            >>> operation_id = '5dc03727-de89-460d-b2a7-7f766c83d2f1'
            >>> agent_id = '38c1c67e-436f-4652-8cae-f1a2ac2dd4a2'
            >>> app_id = '70d462913faad1ecaa85eda4c448a607164fe39414c8be44405e7ab4f7f8467c'
            >>> status_code = 6006
            >>> oper.update_operation_results(
                    operation_id, agent_id, app_id, status_code
                )

        Returns:
            Boolean
        """
        completed = False
        operation_data = (
            {
                OperationPerAppKey.Results: results,
                OperationPerAppKey.ResultsReceivedTime: self.db_time,
                OperationPerAppKey.Errors: errors
            }
        )

        status_code, count, errors, generated_ids = (
            update_operation_per_app(operation_id, operation_data)
        )
        
        if status_code == DbCodes.Replaced:
            self._update_app_stats(operation_id, agent_id, app_id, results)
            completed = True

        return(completed)


    def _update_app_stats(
        self, operation_id, agent_id,
        app_id, results
        ):

        completed = False
        pending_count, completed_count, failed_count = (
            group_operations_per_app_by_results(
                operation_id, agent_id
            )
        )

        operation_data = {
            OperationPerAgentKey.AppsCompletedCount: completed_count,
            OperationPerAgentKey.AppsFailedCount: failed_count,
            OperationPerAgentKey.AppsPendingCount: pending_count,
        }

        status_code, count, errors, generated_ids = (
            update_agent_operation(operation_id, operation_data)
        )

        if status_code == DbCodes.Replaced:
            self._update_agent_stats_by_app_stats(
                operation_id, agent_id, completed_count,
                failed_count, pending_count
            )
            completed = True

        return(completed)

    def _update_agent_stats_by_app_stats(
        self, operation_id, agent_id,
        completed_count, failed_count,
        pending_count
        ):
        """Update the total counts based on the status code.
        Args:
            operation_id (str): the operation id.
            agent_id (str): the agent id.
            completed_count (int): the completed count.
            failed_count (int): the failed count.
            pending_count (int): the pending count.

        Basic Usage:
            >>> from vFense.operations.agent_operations import AgentOperation
            >>> username = 'admin'
            >>> customer_name = 'default'
            >>> oper = AgentOperation(username, customer_name)
            >>> operation_id = '5dc03727-de89-460d-b2a7-7f766c83d2f1'
            >>> agent_id = '38c1c67e-436f-4652-8cae-f1a2ac2dd4a2'
            >>> completed_count = 1
            >>> pending_count = 0
            >>> failed_count = 0
            >>> oper._update_agent_stats_by_app_stats(
                    operation_id, agent_id, completed_count,
                    failed_count, pending_count
                )

        Returns:
            Boolean
        """
        completed = False
        total_count = completed_count + failed_count + pending_count
        if total_count == completed_count:
            status_code, count, errors, generated_ids = (
                update_completed_and_pending_count(operation_id, self.db_time)
            )

            if status_code == DbCodes.Replaced:
                self._update_completed_time_on_agents(operation_id, agent_id)
                self._update_operation_status_code(operation_id)
                completed = True

        elif total_count == failed_count:
            status_code, count, errors, generated_ids = (
                update_failed_and_pending_count(operation_id, self.db_time)
            )

            if status_code == DbCodes.Replaced:
                self._update_completed_time_on_agents(operation_id, agent_id)
                self._update_operation_status_code(operation_id)
                completed = True

        elif total_count == (failed_count + completed_count):
            status_code, count, errors, generated_ids = (
                update_errors_and_pending_count(operation_id, self.db_time)
            )

            if status_code == DbCodes.Replaced:
                self._update_completed_time_on_agents(operation_id, agent_id)
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
                if status_code == DbCodes.Replaced:
                    completed = True

            elif (oper[OperationPerAgentKey.Status] ==
                    AgentOperationCodes.ResultsReceivedWithErrors):


                status_code, count, errors, generated_ids = (
                    update_failed_and_pending_count(
                        operation_id, self.db_time
                    )
                )
                if status_code == DbCodes.Replaced:
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

        if status_code == DbCodes.Replaced:
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

        if (operation[OperationKey.AgentsTotalCount] == 
            operation[OperationKey.AgentsCompletedCount]):

            operation_data = {
                OperationKey.OperationStatus: AgentOperationCodes.ResultsCompleted,
                OperationKey.CompletedTime: self.db_time
            }

        elif (operation[OperationKey.AgentsTotalCount] == 
            operation[OperationKey.AgentsFailedCount]):

            operation_data = {
                OperationKey.OperationStatus: AgentOperationCodes.ResultsCompletedFailed,
                OperationKey.CompletedTime: self.db_time
            }

        elif (operation[OperationKey.AgentsTotalCount] == 
            (
               operation[OperationKey.AgentsFailedCount] +
               operation[OperationKey.AgentsExpiredCount]
            )):

            operation_data = {
                OperationKey.OperationStatus: AgentOperationCodes.ResultsCompletedFailed,
                OperationKey.CompletedTime: self.db_time
            }

        elif (operation[OperationKey.AgentsTotalCount] == 
            operation[OperationKey.AgentsExpiredCount]):

            operation_data = {
                OperationKey.OperationStatus: AgentOperationCodes.ResultsCompletedFailed,
                OperationKey.CompletedTime: self.db_time
            }

        elif (operation[OperationKey.AgentsTotalCount] == 
            (
                operation[OperationKey.AgentsFailedCount] +
                operation[OperationKey.AgentsCompletedWithErrorsCount]
            )):

            operation_data = {
                OperationKey.OperationStatus: AgentOperationCodes.ResultsCompletedWithErrors,
                OperationKey.CompletedTime: self.db_time
            }

        elif (operation[OperationKey.AgentsTotalCount] == 
            (
                operation[OperationKey.AgentsCompletedWithErrorsCount] +
                operation[OperationKey.AgentsExpiredCount]
            )):

            operation_data = {
                OperationKey.OperationStatus: AgentOperationCodes.ResultsCompletedWithErrors,
                OperationKey.CompletedTime: self.db_time
            }

        elif (operation[OperationKey.AgentsTotalCount] == 
            (
                operation[OperationKey.AgentsFailedCount] +
                operation[OperationKey.AgentsCompletedWithErrorsCount] +
                operation[OperationKey.AgentsExpiredCount]
            )):

            operation_data = {
                OperationKey.OperationStatus: AgentOperationCodes.ResultsCompletedWithErrors,
                OperationKey.CompletedTime: self.db_time
            }

        else:
            operation_data = {
                OperationKey.OperationStatus: AgentOperationCodes.ResultsIncomplete
            }

        if operation_data:
            status_code, count, errors, generated_ids = (
                update_agent_operation(operation_id, operation_data)
            )
            if status_code == DbCodes.Replaced:
                completed = True

        retuen(completed)
