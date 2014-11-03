from json import dumps

from vFense.core.api.base import BaseHandler
from vFense.core.decorators import (
    convert_json_to_arguments, api_catch_it, results_message
)
from vFense.core.receiver.api.decorators import (
    agent_results_message, agent_authenticated_request,
    receiver_catch_it, authenticate_agent
)

from vFense.core.agent.operations.agent_results import AgentOperationResults
from vFense.core.receiver.api.base import AgentBaseHandler


class RebootResultsV1(BaseHandler):
    @agent_authenticated_request
    @convert_json_to_arguments
    def put(self, agent_id):
        operation_id = self.arguments.get('operation_id')
        error = self.arguments.get('error', None)
        success = self.arguments.get('success')
        results = (
            self.reboot_results(agent_id, operation_id, success, error)
        )
        self.set_status(results.http_status_code)
        self.set_header('Content-Type', 'application/json')
        self.write(dumps(results.to_dict_non_null(), indent=4))

    @api_catch_it
    @results_message
    def reboot_results(self, agent_id, operation_id, success, error):
        operation_results = (
            AgentOperationResults(agent_id, operation_id, success, error)
        )
        results = operation_results.reboot()
        return results


class RebootResultsV2(AgentBaseHandler):
    @authenticate_agent
    @convert_json_to_arguments
    def put(self, agent_id):
        operation_id = self.arguments.get('operation_id')
        error = self.arguments.get('error', None)
        success = self.arguments.get('success')
        results = (
            self.reboot_results(agent_id, operation_id, success, error)
        )
        self.set_status(results.http_status_code)
        self.set_header('Content-Type', 'application/json')
        self.write(dumps(results.to_dict_non_null(), indent=4))

    @receiver_catch_it
    @agent_results_message
    def reboot_results(self, agent_id, operation_id, success, error):
        operation_results = (
            AgentOperationResults(agent_id, operation_id, success, error)
        )
        results = operation_results.reboot()
        return results


class ShutdownResultsV1(BaseHandler):
    @agent_authenticated_request
    @convert_json_to_arguments
    def put(self, agent_id):
        operation_id = self.arguments.get('operation_id')
        error = self.arguments.get('error', None)
        success = self.arguments.get('success')
        results = (
            self.shutdown_results(agent_id, operation_id, success, error)
        )
        self.set_status(results.http_status_code)
        self.set_header('Content-Type', 'application/json')
        self.write(dumps(results.to_dict_non_null(), indent=4))

    @api_catch_it
    @results_message
    def shutdown_results(self, agent_id, operation_id, success, error):
        operation_results = (
            AgentOperationResults(agent_id, operation_id, success, error)
        )
        results = operation_results.shutdown()
        return results


class ShutdownResultsV2(AgentBaseHandler):
    @authenticate_agent
    @convert_json_to_arguments
    def put(self, agent_id):
        operation_id = self.arguments.get('operation_id')
        error = self.arguments.get('error', None)
        success = self.arguments.get('success')
        status_code = self.arguments.get('status_code')
        results = (
            self.shutdown_results(
                agent_id, operation_id, success, error, status_code
            )
        )
        self.set_status(results.http_status_code)
        self.set_header('Content-Type', 'application/json')
        self.write(dumps(results.to_dict_non_null(), indent=4))

    @receiver_catch_it
    @agent_results_message
    def shutdown_results(self, agent_id, operation_id,
                         success, error, status_code):
        operation_results = (
            AgentOperationResults(
                agent_id, operation_id, success, error, status_code
            )
        )
        results = operation_results.shutdown()
        return results
