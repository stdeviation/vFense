import logging

from json import dumps

from vFense import VFENSE_LOGGING_CONFIG
from vFense.core.api.base import BaseHandler
from vFense.core.decorators import (
    agent_authenticated_request, convert_json_to_arguments
)

from vFense.core.results import (
    Results, UpdateApplicationsResults
)

from vFense.receiver.rvhandler import RvHandOff
from vFense.receiver.api.base import AgentBaseHandler
from vFense.receiver.results import AgentResults, AgentApiResultKeys
from vFense.receiver.api.decorators import (
    authenticate_agent, agent_results_message
)

from vFense.core.operations._constants import AgentOperations

logging.config.fileConfig(VFENSE_LOGGING_CONFIG)
logger = logging.getLogger('rvlistener')


class AgentUpdateHandler(BaseHandler):
    @agent_authenticated_request
    @convert_json_to_arguments
    def put(self, agent_id):
        uri = self.request.uri
        method = self.request.method

        try:
            app_data = self.arguments.get('data')

            RvHandOff(
            ).available_agent_update_operation(agent_id, app_data)

            results = (
                UpdateApplicationsResults('agent', uri, method)
                .applications_updated(agent_id, app_data)
            )

            results['data'] = []
            self.set_status(results['http_status'])
            self.write(dumps(results))

        except Exception as e:
            results = Results(
                'agent', uri, method
            ).something_broke(
                agent_id, AgentOperations.AVAILABLE_AGENT_UPDATE, e
            )
            logger.exception(results)

            self.set_status(results['http_status'])
            self.write(dumps(results))


class AgentUpdateHandlerV2(AgentBaseHandler):
    @authenticate_agent
    @convert_json_to_arguments
    def put(self, agent_id):

        try:
            app_data = self.arguments.get('data')
            RvHandOff(
            ).available_agent_update_operation(agent_id, app_data)

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
                    'Failed to receive agent application data for agent {0}: {1}'
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

