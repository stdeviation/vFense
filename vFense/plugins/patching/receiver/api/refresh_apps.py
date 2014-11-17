from json import dumps

from vFense.core.api.base import BaseHandler
from vFense.core.decorators import convert_json_to_arguments
from vFense.core.operations.status_codes import AgentOperationCodes
from vFense.core.receiver.api.base import AgentBaseHandler
from vFense.core.results import ApiResults
from vFense.core.receiver.decorators import (
    authenticate_agent, agent_results_message, receiver_catch_it,
    agent_authenticated_request
)
from vFense.core.receiver.status_codes import (
    AgentFailureResultCodes, AgentResultCodes
)
from vFense.plugins.patching.receiver import RefreshAppsResults
from vFense.plugins.patching.receiver.handoff import PatcherHandOff
from vFense.plugins.patching.operations.patching_results import (
    PatchingOperationResults
)


class RefreshAppsV1(BaseHandler):
    @agent_authenticated_request
    @convert_json_to_arguments
    def put(self, agent_id):
        refresh_results = RefreshAppsResults(agent_id=agent_id)
        refresh_results.operation_id = (
            self.arguments.get('operation_id', None)
        )
        refresh_results.error = self.arguments.get('error', None)
        refresh_results.success = self.arguments.get('success', 'true')
        refresh_results.apps_data = self.arguments.get('data')
        refresh_results.status_code = self.arguments.get('status_code', None)
        results = self.refresh_apps_results(refresh_results)
        self.set_status(results.http_status_code)
        self.write(dumps(results.to_dict_non_null()))

    @receiver_catch_it
    @agent_results_message
    def refresh_apps_results(self, refresh_results):
        results = ApiResults()
        handoff = PatcherHandOff(
            agent_id=refresh_results.agent_id,
            apps_data=refresh_results.apps_data
        )
        handoff.refresh_apps_operation()
        if refresh_results.operation_id:
            update_results = PatchingOperationResults(
                refresh_results.agent_id, refresh_results.operation_id,
                refresh_results.success, refresh_results.error,
                refresh_results.status_code
            )
            results = update_results.refresh_apps()

        else:
            results.message = (
                'Received application updates for agent {0}'
                .format(refresh_results.agent_id)
            )
            if refresh_results.error:
                results.generic_status_code = (
                    AgentOperationCodes.ResultsReceivedWithErrors
                )
                results.vfense_status_code = (
                    AgentFailureResultCodes.ResultsFailedToUpdate
                )
            else:
                results.generic_status_code = (
                    AgentOperationCodes.ResultsReceived
                )
                results.vfense_status_code = (
                    AgentResultCodes.ResultsUpdated
                )

        return results

class RefreshAppsV2(AgentBaseHandler):
    @authenticate_agent
    @convert_json_to_arguments
    def put(self, agent_id):
        refresh_results = RefreshAppsResults(agent_id=agent_id)
        refresh_results.operation_id = (
            self.arguments.get('operation_id', None)
        )
        refresh_results.error = self.arguments.get('error', None)
        refresh_results.success = self.arguments.get('success', 'true')
        refresh_results.apps_data = self.arguments.get('data')
        refresh_results.status_code = self.arguments.get('status_code', None)
        results = self.refresh_apps_results(refresh_results)
        self.set_status(results.http_status_code)
        self.write(dumps(results.to_dict_non_null()))

    @receiver_catch_it
    @agent_results_message
    def refresh_apps_results(self, refresh_results):
        results = ApiResults()
        handoff = PatcherHandOff(
            agent_id=refresh_results.agent_id,
            apps_data=refresh_results.apps_data
        )
        handoff.refresh_apps_operation()
        if refresh_results.operation_id:
            update_results = PatchingOperationResults(
                refresh_results.agent_id, refresh_results.operation_id,
                refresh_results.success, refresh_results.error,
                refresh_results.status_code
            )
            results = update_results.refresh_apps()

        else:
            results.message = (
                'Received application updates for agent {0}'
                .format(refresh_results.agent_id)
            )
            if refresh_results.error:
                results.generic_status_code = (
                    AgentOperationCodes.ResultsReceivedWithErrors
                )
                results.vfense_status_code = (
                    AgentFailureResultCodes.ResultsFailedToUpdate
                )
            else:
                results.generic_status_code = (
                    AgentOperationCodes.ResultsReceived
                )
                results.vfense_status_code = (
                    AgentResultCodes.ResultsUpdated
                )

        return results
