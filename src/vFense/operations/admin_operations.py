#!/usr/bin/env python

from vFense import logging
from datetime import datetime
from time import mktime
from vFense.operations._db_model import (
    AdminOperationKey
)
from vFense.operations._constants import vFenseObjects, OperationErrors
from vFense.core._db_constants import DbTime

from vFense.operations._db_admin import (
    fetch_admin_operation, insert_admin_operation
)

class AdminOperation(object):
    """This is what creates operations for an agent or multiple agents.

    """
    def __init__(self, username, view_name):
        """
        Args:
            username (str): the name of the user who created the operation.
            view_name (str): the name of the view this user is part of.

        Basic Usage:
            >>> from vFense.operations.admin_operations import AdminOperation
            >>> username = 'global_admin'
            >>> view_name = 'global'
            >>> oper = AdminOperation(username, view_name)
        """
        self.username = username
        self.view_name = view_name
        self.now = mktime(datetime.now().timetuple())
        self.db_time = DbTime.time_now()
        self.INIT_COUNT = 0


    def create(self, action, performed_on):
        """Create the operation and return the operation_id.
        Args:
            action (str): The action that was performed.
                (create view, create user, remove user, etc..).
            performed_on (str): The entity this action was performed on.
                (tag, agent, user, view, group)

        Basic Usage:
            >>> from vFense.operations.admin_operations import AdminOperation
            >>> username = 'global_admin'
            >>> view_name = 'global'
            >>> oper = AdminOperation(username, view_name)
            >>> action = 'create user'
            >>> performed_on = 'user'
            >>> oper.create(action, performed_on)

        Returns:
            String The 36 character UUID of the operation that was created.
            6c0209d5-b350-48b7-808a-158ddacb6940
        """

        number_of_agents = len(agent_ids)
        keys_to_insert = (
            {
                AgentOperationKey.Plugin: plugin,
                AgentOperationKey.Operation: operation,
                AgentOperationKey.OperationStatus: (
                    AgentOperationCodes.ResultsIncomplete
                ),
                AgentOperationKey.ViewName: self.view_name,
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
                AgentOperationKey.AgentsCompletedWithErrorsCount: (
                    self.INIT_COUNT
                ),
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

        return operation_id

