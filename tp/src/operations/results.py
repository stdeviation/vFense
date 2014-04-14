#!/usr/bin/env python
from json import loads
import logging
import logging.config
from time import time

from vFense.core._constants import CommonKeys
from vFense.core.agent import AgentKey
from vFense.core.errorz._constants import ApiResultKeys
from vFense.core.agent.agents import get_agent_info, update_agent_field
from vFense.operations._constants import AgentOperations
from vFense.operations.agent_operations import AgentOperation, \
    operation_for_agent_and_app_exist, operation_for_agent_exist, \
    get_agent_operation

from vFense.errorz.status_codes import AgentOperationCodes, GenericCodes, \
    GenericFailureCodes, AgentFailureResultCodes, AgentResultCodes

from vFense.errorz.results import Results


logging.config.fileConfig('/opt/TopPatch/conf/logging.config')
logger = logging.getLogger('rvapi')

class AgentOperationResults(object):
    """Update an operation for an agent, based on the results received."""
    def __init__(
        self, username, agent_id, operation_id,
        success, error=None, status_code=None,
        uri=None, method=None
        ):
        """
            Args:
                username (str): The name of the user who made this api call
                agent_id (str): 36 character UUID of the agent.
                operation_id (str): 36 character UUID of the operation.
                success (str): true or false.

            Kwargs:
                error (str): The error message, if the operation failed.
                status_code (int): The exact status of this operation.
                uri (str): The uri which was called for the results.
                method (str): The method used to call this api.
        """

        self.agent_id = agent_id
        self.operation_id = operation_id
        self.username = username
        self.uri = uri
        self.method = method
        self.agent_data = get_agent_info(self.agent_id)
        self.customer_name = self.agent_data[AgentKey.CustomerName]
        self.date_now = int(time())
        self.error = error
        self.success = success
        self.status_code = status_code
        self.operation = (
            AgentOperation(
                self.username, self.customer_name,
                self.uri, self.method
            )
        )

    def reboot(self):
        oper_type = AgentOperations.REBOOT
        results = self._update_operation(oper_type)

        if self.success == CommonKeys.TRUE:
            update_agent_field(
                self.agent_id,
                AgentKey.NeedsReboot,
                CommonKeys.NO, self.username,
                self.uri, self.method
            )

        return(results)

    def shutdown(self):
        oper_type = AgentOperations.SHUTDOWN
        results = self._update_operation(oper_type)
        return(results)


    def _update_operation(self, oper_type):

        results = {
            ApiResultKeys.DATA: [],
            ApiResultKeys.USERNAME: self.user_name,
            ApiResultKeys.URI: self.uri,
            ApiResultKeys.HTTP_METHOD: self.method
        }

        oper_exists = (
            operation_for_agent_exist(
                self.operation_id, self.agent_id
            )
        )

        if oper_exists:
            if (
                self.success == CommonKeys.TRUE or
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
                    msg = 'Results updated'
                    results[ApiResultKeys.GENERIC_STATUS_CODE] = (
                        GenericCodes.ObjectUpdated
                    )

                    results[ApiResultKeys.VFENSE_STATUS_CODE] = (
                        AgentResultCodes.ResultsUpdated
                    )

                    results[ApiResultKeys.MESSAGE] = msg

                else:
                    msg = 'Results failed to update'
                    results[ApiResultKeys.GENERIC_STATUS_CODE] = (
                        GenericFailureCodes.FailedToUpdateObject
                    )

                    results[ApiResultKeys.VFENSE_STATUS_CODE] = (
                        AgentFailureResultCodes.ResultsFailedToUpdate
                    )

                    results[ApiResultKeys.MESSAGE] = msg

            else:
                msg = 'Invalid success value'
                results[ApiResultKeys.GENERIC_STATUS_CODE] = (
                    GenericFailureCodes.FailedToUpdateObject
                )

                results[ApiResultKeys.VFENSE_STATUS_CODE] = (
                    AgentFailureResultCodes.InvalidSuccessValue
                )

                results[ApiResultKeys.MESSAGE] = msg

        else:
            msg = 'Invalid operation id'
            results[ApiResultKeys.GENERIC_STATUS_CODE] = (
                GenericFailureCodes.InvalidId
            )

            results[ApiResultKeys.VFENSE_STATUS_CODE] = (
                AgentFailureResultCodes.InvalidOperationId
            )

            results[ApiResultKeys.MESSAGE] = msg


        return(results)
