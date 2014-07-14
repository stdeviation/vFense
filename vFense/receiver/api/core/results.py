import logging
from json import dumps

from vFense import VFENSE_LOGGING_CONFIG
from vFense.core.api.base import BaseHandler
from vFense.core.decorators import (
    agent_authenticated_request, convert_json_to_arguments,
    results_message
)
from vFense.receiver.api.decorators import authenticate_agent

from vFense.core.agent.operations.agent_results import AgentOperationResults
from vFense.db.notification_sender import send_notifications
from vFense.result.error_messages import GenericResults


logging.config.fileConfig(VFENSE_LOGGING_CONFIG)
logger = logging.getLogger('rvlistener')


class RebootResultsV1(BaseHandler):
    @agent_authenticated_request
    @convert_json_to_arguments
    def put(self, agent_id):
        uri = self.request.uri
        method = self.request.method
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
            results = (
                GenericResults(
                    'agent', uri, method
                ).something_broke(agent_id, 'reboot results', e)
            )
            logger.exception(results)

            self.set_status(results['http_status'])
            self.set_header('Content-Type', 'application/json')
            self.write(dumps(results, indent=4))

    @results_message
    def reboot_results(self, results):
        results_data = results.reboot()
        return results_data


class RebootResultsV2(BaseHandler):
    @authenticate_agent
    @convert_json_to_arguments
    def put(self, agent_id):
        uri = self.request.uri
        method = self.request.method
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
            results = (
                GenericResults(
                    'agent', uri, method
                ).something_broke(agent_id, 'reboot results', e)
            )
            logger.exception(results)

            self.set_status(results['http_status'])
            self.set_header('Content-Type', 'application/json')
            self.write(dumps(results, indent=4))

    @results_message
    def reboot_results(self, results):
        results_data = results.reboot()
        return results_data


class ShutdownResultsV1(BaseHandler):
    @agent_authenticated_request
    @convert_json_to_arguments
    def put(self, agent_id):
        uri = self.request.uri
        method = self.request.method
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
            results = (
                GenericResults(
                    'agents', uri, method
                ).something_broke(agent_id, 'shutdown results', e)
            )
            logger.exception(results)

            self.set_status(results['http_status'])
            self.set_header('Content-Type', 'application/json')
            self.write(dumps(results, indent=4))


    @results_message
    def shutdown_results(self, results):
        results_data = results.shutdown()
        return results_data


class ShutdownResultsV2(BaseHandler):
    @authenticate_agent
    @convert_json_to_arguments
    def put(self, agent_id):
        uri = self.request.uri
        method = self.request.method
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
            results = (
                GenericResults(
                    'agent', uri, method
                ).something_broke(agent_id, 'shutdown results', e)
            )
            logger.exception(results)

            self.set_status(results['http_status'])
            self.set_header('Content-Type', 'application/json')
            self.write(dumps(results, indent=4))


    @results_message
    def shutdown_results(self, results):
        results_data = results.shutdown()
        return results_data
