import logging
from json import dumps

from vFense._constants import VFENSE_LOGGING_CONFIG
from vFense.core.api.base import BaseHandler
from vFense.core.decorators import (
    agent_authenticated_request, convert_json_to_arguments,
    results_message
)
from vFense.receiver.api.decorators import (
    authenticate_agent, agent_results_message
)

from vFense.core.agent.operations.agent_results import AgentOperationResults
from vFense.core.results import Results
from vFense.receiver.results import AgentResults, AgentApiResultKeys
from vFense.receiver.api.base import AgentBaseHandler

logging.config.fileConfig(VFENSE_LOGGING_CONFIG)
logger = logging.getLogger('rvlistener')


class RebootResultsV1(BaseHandler):
    @agent_authenticated_request
    @convert_json_to_arguments
    def put(self, agent_id):
        active_user = self.get_current_user()
        try:
            operation_id = self.arguments.get('operation_id')
            error = self.arguments.get('error', None)
            success = self.arguments.get('success')
            results = (
                AgentOperationResults(
                    agent_id, operation_id, success, error
                )
            )
            results_data = self.reboot_results(results)
            self.set_status(results_data['http_status'])
            self.set_header('Content-Type', 'application/json')
            self.write(dumps(results_data, indent=4))

        except Exception as e:
            data = {
                AgentApiResultKeys.MESSAGE: (
                    'Reboot results for agent {0} broke: {1}'
                    .format(agent_id, e)
                )
            }
            results = (
                Results(
                    active_user, self.request.uri, self.request.method
                ).something_broke(**data)
            )
            logger.exception(results)

            self.set_status(results['http_status'])
            self.set_header('Content-Type', 'application/json')
            self.write(dumps(results, indent=4))

    @results_message
    def reboot_results(self, results):
        results_data = results.reboot()
        return results_data


class RebootResultsV2(AgentBaseHandler):
    @authenticate_agent
    @convert_json_to_arguments
    def put(self, agent_id):
        try:
            operation_id = self.arguments.get('operation_id')
            error = self.arguments.get('error', None)
            success = self.arguments.get('success')
            results = (
                AgentOperationResults(
                    agent_id, operation_id, success, error
                )
            )
            results_data = self.reboot_results(results)
            self.set_status(results_data['http_status'])
            self.set_header('Content-Type', 'application/json')
            self.write(dumps(results_data, indent=4))

        except Exception as e:
            data = {
                AgentApiResultKeys.MESSAGE: (
                    'Reboot results for agent {0} broke: {1}'
                    .format(agent_id, e)
                )
            }
            results = (
                AgentResults(
                    self.request.uri, self.request.method,
                    self.get_token(), agent_id
                ).something_broke(**data)
            )
            logger.exception(results)

            self.set_status(results['http_status'])
            self.set_header('Content-Type', 'application/json')
            self.write(dumps(results, indent=4))

    @agent_results_message
    def reboot_results(self, results):
        results_data = results.reboot()
        return results_data


class ShutdownResultsV1(BaseHandler):
    @agent_authenticated_request
    @convert_json_to_arguments
    def put(self, agent_id):
        active_user = self.get_current_user()
        try:
            operation_id = self.arguments.get('operation_id')
            error = self.arguments.get('error', None)
            success = self.arguments.get('success')
            results = (
                AgentOperationResults(
                    agent_id, operation_id, success, error
                )
            )
            results_data = self.shutdown_results(results)
            self.set_status(results_data['http_status'])
            self.set_header('Content-Type', 'application/json')
            self.write(dumps(results_data, indent=4))

        except Exception as e:
            data = {
                AgentApiResultKeys.MESSAGE: (
                    'Shutdown results for agent {0} broke: {1}'
                    .format(agent_id, e)
                )
            }
            results = (
                Results(
                    active_user, self.request.uri, self.request.method
                ).something_broke(**data)
            )
            logger.exception(results)

            self.set_status(results['http_status'])
            self.set_header('Content-Type', 'application/json')
            self.write(dumps(results, indent=4))


    @results_message
    def shutdown_results(self, results):
        results_data = results.shutdown()
        return results_data


class ShutdownResultsV2(AgentBaseHandler):
    @authenticate_agent
    @convert_json_to_arguments
    def put(self, agent_id):
        try:
            operation_id = self.arguments.get('operation_id')
            error = self.arguments.get('error', None)
            success = self.arguments.get('success')
            status_code = self.arguments.get('status_code')
            results = (
                AgentOperationResults(
                    agent_id, operation_id, success, error, status_code
                )
            )
            results_data = self.shutdown_results(results)
            self.set_status(results_data['http_status'])
            self.set_header('Content-Type', 'application/json')
            self.write(dumps(results_data, indent=4))

        except Exception as e:
            data = {
                AgentApiResultKeys.MESSAGE: (
                    'Shutdown results for agent {0} broke: {1}'
                    .format(agent_id, e)
                )
            }
            results = (
                AgentResults(
                    self.request.uri, self.request.method,
                    self.get_token(), agent_id
                ).something_broke(**data)
            )
            logger.exception(results)

            self.set_status(results['http_status'])
            self.set_header('Content-Type', 'application/json')
            self.write(dumps(results, indent=4))


    @agent_results_message
    def shutdown_results(self, results):
        results_data = results.shutdown()
        return results_data
