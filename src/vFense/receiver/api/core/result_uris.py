import logging
from json import dumps

from vFense import VFENSE_LOGGING_CONFIG
from vFense.core.api.base import BaseHandler
from vFense.receiver.api.base import AgentBaseHandler
from vFense.core.decorators import (
    results_message
)
from vFense.core.queue.uris import get_result_uris
from vFense.result.error_messages import GenericResults
from vFense.result._constants import AgentApiResultKeys
from vFense.core.operations._constants import AgentOperations
from vFense.result.agent_results import AgentResults
from vFense.receiver.api.decorators import (
    authenticate_token, agent_results_message
)

logging.config.fileConfig(VFENSE_LOGGING_CONFIG)
logger = logging.getLogger('rvlistener')

class AgentResultURIs(BaseHandler):
    @authenticate_token
    def get(self, agent_id):
        username = self.get_current_user()
        uri = self.request.uri
        method = self.request.method
        try:
            results = self.get_uris(agent_id)
            self.set_header('Content-Type', 'application/json')
            self.write(dumps(results, indent=4))

        except Exception as e:
            status = (
                GenericResults(
                    username, uri, method
                ).something_broke('uris', 'refresh_response_uris', e)
            )
            logger.exception(e)
            self.write(dumps(status, indent=4))

    @results_message
    def get_uris(self, agent_id):
        operation = get_result_uris(agent_id, 'v1')
        operation[AgentApiResultKeys.OPERATION] = (
            AgentOperations.REFRESH_RESPONSE_URIS
        )
        results = {AgentApiResultKeys.OPERATIONS: operation}
        return results

class ResultURIs(BaseHandler):
    @authenticate_token
    def get(self):
        username = self.get_current_user()
        uri = self.request.uri
        method = self.request.method
        try:
            results = self.get_uris()
            self.set_header('Content-Type', 'application/json')
            self.write(dumps(results, indent=4))

        except Exception as e:
            status = (
                GenericResults(
                    username, uri, method
                ).something_broke('uris', 'refresh_response_uris', e)
            )
            logger.exception(e)
            self.write(dumps(status, indent=4))

    @results_message
    def get_uris(self):
        operation = get_result_uris(version='v1')
        operation[AgentApiResultKeys.OPERATION] = (
            AgentOperations.REFRESH_RESPONSE_URIS
        )
        results = {AgentApiResultKeys.OPERATIONS: operation}
        return results

class AgentResultURIsV2(AgentBaseHandler):
    @authenticate_token
    def get(self, agent_id):
        results = self.get_uris(agent_id)
        self.set_header('Content-Type', 'application/json')
        self.write(dumps(results, indent=4))

    @agent_results_message
    def get_uris(self, agent_id):
        operation = get_result_uris(agent_id, 'v2')
        operation[AgentApiResultKeys.OPERATION] = (
            AgentOperations.REFRESH_RESPONSE_URIS
        )
        results = {AgentApiResultKeys.OPERATIONS: operation}
        return results

class ResultURIsV2(AgentBaseHandler):
    @authenticate_token
    def get(self):
        results = self.get_uris()
        self.set_header('Content-Type', 'application/json')
        self.write(dumps(results, indent=4))

    @agent_results_message
    def get_uris(self):
        operation = get_result_uris(version='v2')
        operation[AgentApiResultKeys.OPERATION] = (
            AgentOperations.REFRESH_RESPONSE_URIS
        )
        results = {AgentApiResultKeys.OPERATIONS: operation}
        return results
