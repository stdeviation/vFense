import logging
from json import dumps

from vFense import VFENSE_LOGGING_CONFIG
from vFense.core.api.base import BaseHandler
from vFense.receiver.api.base import AgentBaseHandler
from vFense.core.decorators import (
    results_message
)
from vFense.core.queue.uris import get_result_uris
from vFense.core.results import Results
from vFense.core.operations._constants import AgentOperations
from vFense.receiver.results import AgentApiResultKeys
from vFense.receiver.api.decorators import (
    authenticate_token, agent_results_message
)

logging.config.fileConfig(VFENSE_LOGGING_CONFIG)
logger = logging.getLogger('rvlistener')

class AgentResultURIs(BaseHandler):
    @authenticate_token
    def get(self, agent_id):
        active_user = self.get_current_user()
        try:
            results = self.get_uris(agent_id)
            self.set_header('Content-Type', 'application/json')
            self.write(dumps(results, indent=4))

        except Exception as e:
            data = {
                AgentApiResultKeys.MESSAGE: (
                    'Response URIs for agent {0} broke: {1}'
                    .format(agent_id, e)
                )
            }
            results = (
                Results(
                    active_user, self.request.uri, self.request.method
                ).something_broke(**data)
            )
            logger.exception(e)
            self.write(dumps(results, indent=4))

    @results_message
    def get_uris(self, agent_id):
        results = get_result_uris(agent_id, 'v1')
        results[AgentApiResultKeys.OPERATION] = (
            AgentOperations.REFRESH_RESPONSE_URIS
        )
        results[AgentApiResultKeys.OPERATIONS] = [results.copy()]
        return results

class ResultURIs(BaseHandler):
    @authenticate_token
    def get(self):
        active_user = self.get_current_user()
        try:
            results = self.get_uris()
            self.set_header('Content-Type', 'application/json')
            self.write(dumps(results, indent=4))

        except Exception as e:
            data = {
                AgentApiResultKeys.MESSAGE: (
                    'Response URIs broke: {0}'.format(e)
                )
            }
            results = (
                Results(
                    active_user, self.request.uri, self.request.method
                ).something_broke(**data)
            )
            logger.exception(e)
            self.write(dumps(results, indent=4))

    @results_message
    def get_uris(self):
        results = get_result_uris(version='v1')
        results[AgentApiResultKeys.OPERATION] = (
            AgentOperations.REFRESH_RESPONSE_URIS
        )
        results[AgentApiResultKeys.OPERATIONS] = [results.copy()]
        return results

class AgentResultURIsV2(AgentBaseHandler):
    @authenticate_token
    def get(self, agent_id):
        results = self.get_uris(agent_id)
        self.set_header('Content-Type', 'application/json')
        self.write(dumps(results, indent=4))

    @agent_results_message
    def get_uris(self, agent_id):
        results = get_result_uris(agent_id, 'v2')
        results[AgentApiResultKeys.OPERATION] = (
            AgentOperations.REFRESH_RESPONSE_URIS
        )
        results[AgentApiResultKeys.OPERATIONS] = [results.copy()]
        return results

class ResultURIsV2(AgentBaseHandler):
    @authenticate_token
    def get(self):
        results = self.get_uris()
        self.set_header('Content-Type', 'application/json')
        self.write(dumps(results, indent=4))

    @agent_results_message
    def get_uris(self):
        results = get_result_uris(version='v2')
        results[AgentApiResultKeys.OPERATION] = (
            AgentOperations.REFRESH_RESPONSE_URIS
        )
        results[AgentApiResultKeys.OPERATIONS] = [results.copy()]
        return results
