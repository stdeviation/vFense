import logging

from json import dumps

from vFense._constants import VFENSE_LOGGING_CONFIG
from vFense.core.decorators import (
    convert_json_to_arguments
)

from vFense.plugins.patching.operations.patching_results import (
    PatchingOperationResults
)
from vFense.core.receiver.rvhandler import RvHandOff
from vFense.core.receiver.api.base import AgentBaseHandler
from vFense.core.receiver.results import AgentResults, AgentApiResultKeys
from vFense.core.receiver.decorators import (
    authenticate_agent, agent_results_message
)


logging.config.fileConfig(VFENSE_LOGGING_CONFIG)
logger = logging.getLogger('rvlistener')

class RefreshAppsV2(AgentBaseHandler):
    @authenticate_agent
    @convert_json_to_arguments
    def put(self, agent_id):
        try:
            operation_id = self.arguments.get('operation_id', None)
            error = self.arguments.get('error', None)
            success = self.arguments.get('success', 'true')
            apps_data = self.arguments.get('data')
            status_code = self.arguments.get('status_code', None)

            RvHandOff(
            ).refresh_apps_operation(agent_id, apps_data)

            if operation_id:
                logger.info("self.arguments: {0}".format(self.arguments))

                update_results = PatchingOperationResults(
                    agent_id, operation_id, success, error, status_code
                )

                results = self.refresh_apps_results(update_results)
                self.set_status(results['http_status'])
                self.write(dumps(results))

            else:
                data = {
                    AgentApiResultKeys.MESSAGE: (
                        'Received application updates for agent {0}'
                    .format(agent_id)
                    )
                }
                results = (
                    AgentResults(
                        self.request.uri, self.request.method,
                        self.get_token(), agent_id
                    ).data_received(**data)
                )

                results['data'] = []
                self.set_status(results['http_status'])
                self.write(dumps(results))

        except Exception as e:
            data = {
                AgentApiResultKeys.MESSAGE: (
                    'Failed to receive application data for agent {0}: {1}'
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
            self.write(dumps(results))

    @agent_results_message
    def refresh_apps_results(self, update_results):
        results = update_results.refresh_apps()
        return results
