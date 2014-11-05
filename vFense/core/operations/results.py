#!/usr/bin/env python
import logging
import logging.config
from vFense._constants import VFENSE_LOGGING_CONFIG

from vFense.core._constants import CommonKeys
from vFense.core.results import ApiResults
from vFense.core.agent.agents import get_agent_info
from vFense.core._db_constants import DbTime
from vFense.core.operations.agent_operations import (
    AgentOperationManager, operation_for_agent_exist, get_agent_operation
)
from vFense.core.receiver.status_codes import (
    AgentFailureResultCodes, AgentResultCodes
)
from vFense.core.status_codes import GenericCodes, GenericFailureCodes
from vFense.core.operations.status_codes import AgentOperationCodes


logging.config.fileConfig(VFENSE_LOGGING_CONFIG)
logger = logging.getLogger('rvapi')

class OperationResults(object):
    """Update an operation for an agent, based on the results received.
        This is the base class for adding results to an aegnt operation"""
    def __init__(
            self, agent_id, operation_id,
            success, error=None, status_code=None
        ):
        """
        Args:
            agent_id (str): 36 character UUID of the agent.
            operation_id (str): 36 character UUID of the operation.
            success (str): true or false.

        Kwargs:
            error (str): The error message, if the operation failed.
            status_code (int): The exact status of this operation.

        Basic Usage:
            >>> from vFense.core.operations.results import OperationResults
            >>> operation_id = '8fed3dc7-33d4-4278-9bd4-398a68bf7f22'
            >>> agent_id = 'db6bf07-c5da-4494-93bb-109db205ca64'
            >>> success = 'true'
            >>> results = OperationResults(
                    agent_id, operation_id, success
                )
        """

        self.agent_id = agent_id
        self.operation_id = operation_id
        self.agent_data = get_agent_info(self.agent_id)
        self.operation_data = get_agent_operation(self.operation_id)
        self.date_now = DbTime.now()
        self.begining_of_time = DbTime.begining_of_time()
        self.error = error
        self.success = success
        self.status_code = status_code
        self.operation = AgentOperationManager()

    def update_operation(self, oper_type):
        """Update an agent operation
        Args:
            oper_type (str): This is the operation type, such as
                reboot, shutdown, install_os_apps, etc...

        Basic Usage:
            >>> from vFense.core.operations.results import OperationResults
            >>> operation_id = '8fed3dc7-33d4-4278-9bd4-398a68bf7f22'
            >>> agent_id = 'db6bf07-c5da-4494-93bb-109db205ca64'
            >>> success = 'true'
            >>> results = OperationResults(
                    agent_id, operation_id, success
                )
            >>> results.update_operation('reboot')

        Returns:
            Dictionary
            {
                "rv_status_code": 3203,
                "updated_ids": [
                    "d5fb023c-82a0-4552-adc1-b3f83de7ae8a"
                ],
                "unchanged_ids": [],
                "message": "Results updated for operation id d5fb023c-82a0-4552-adc1-b3f83de7ae8a",
                "data": [],
            }
        """
        results = ApiResults()
        results.fill_in_defaults()

        oper_exists = (
            operation_for_agent_exist(self.operation_id, self.agent_id)
        )

        if oper_exists:
            if (self.success == CommonKeys.TRUE or
                    self.success == CommonKeys.FALSE):

                if self.success == CommonKeys.TRUE:
                    status_code = AgentOperationCodes.ResultsReceived
                else:
                    status_code = AgentOperationCodes.ResultsReceivedWithErrors

                operation_updated = (
                    self.operation.update_operation_results(
                        self.operation_id, self.agent_id,
                        status_code, oper_type, self.error
                    )
                )

                if operation_updated:
                    msg = (
                        'Results updated for operation id %s' %
                        (self.operation_id)
                    )
                    results.generic_status_code = GenericCodes.ObjectUpdated

                    results.vfense_status_code = (
                        AgentResultCodes.ResultsUpdated
                    )
                    results.message = msg
                    results.updated_ids = [self.operation_id]

                else:
                    msg = (
                        'Results failed to update operation id %s' %
                        (self.operation_id)
                    )
                    results.generic_status_code = (
                        GenericFailureCodes.FailedToUpdateObject
                    )
                    results.vfense_status_code = (
                        AgentFailureResultCodes.ResultsFailedToUpdate
                    )
                    results.message = msg
                    results.unchanged_ids = [self.operation_id]

            else:
                msg = (
                    'Invalid operation id %s' %
                    (self.operation_id)
                )
                results.generic_status_code = (
                    GenericFailureCodes.FailedToUpdateObject
                )
                results.vfense_status_code = (
                    AgentFailureResultCodes.InvalidSuccessValue
                )
                results.message = msg
                results.unchanged_ids = [self.operation_id]

        else:
            msg = 'Invalid operation id'
            results.generic_status_code = GenericFailureCodes.InvalidId
            results.vfense_status_code = (
                AgentFailureResultCodes.InvalidOperationId
            )
            results.message = msg
            results.unchanged_ids = [self.operation_id]

        return results
