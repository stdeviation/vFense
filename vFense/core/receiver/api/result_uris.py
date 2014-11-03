from json import dumps

from vFense.core.api.base import BaseHandler
from vFense.core.decorators import results_message, api_catch_it
from vFense.core.queue import AgentQueueOperation
from vFense.core.queue.uris import get_result_uris
from vFense.core.operations._constants import AgentOperations
from vFense.core.receiver.api.base import AgentBaseHandler
from vFense.core.receiver.api.decorators import (
    agent_results_message, receiver_catch_it, authenticate_token
)

class AgentResultURIs(BaseHandler):
    @authenticate_token
    def get(self, agent_id):
        results = self.get_uris(agent_id)
        self.set_header('Content-Type', 'application/json')
        self.write(dumps(results, indent=4))

    @api_catch_it
    @results_message
    def get_uris(self, agent_id):
        results = get_result_uris(agent_id, version='v1')
        uri_operation = AgentQueueOperation()
        uri_operation.fill_in_defaults()
        uri_operation.plugin = 'core'
        uri_operation.agent_id = agent_id
        uri_operation.operation = AgentOperations.REFRESH_RESPONSE_URIS
        uri_operation.data = results.data
        results.operations.append(uri_operation.to_dict_non_null())
        return results

class ResultURIs(BaseHandler):
    @authenticate_token
    def get(self):
        results = self.get_uris()
        self.set_header('Content-Type', 'application/json')
        self.write(dumps(results, indent=4))

    @api_catch_it
    @results_message
    def get_uris(self):
        results = get_result_uris(version='v1')
        uri_operation = AgentQueueOperation()
        uri_operation.fill_in_defaults()
        uri_operation.plugin = 'core'
        uri_operation.operation = AgentOperations.REFRESH_RESPONSE_URIS
        uri_operation.data = results.data
        results.operations.append(uri_operation.to_dict_non_null())
        return results

class AgentResultURIsV2(AgentBaseHandler):
    @authenticate_token
    def get(self, agent_id):
        results = self.get_uris(agent_id)
        self.set_header('Content-Type', 'application/json')
        self.write(dumps(results, indent=4))

    @receiver_catch_it
    @agent_results_message
    def get_uris(self, agent_id):
        results = get_result_uris(agent_id, version='v2')
        uri_operation = AgentQueueOperation()
        uri_operation.fill_in_defaults()
        uri_operation.plugin = 'core'
        uri_operation.agent_id = agent_id
        uri_operation.operation = AgentOperations.REFRESH_RESPONSE_URIS
        uri_operation.data = results.data
        results.operations.append(uri_operation.to_dict_non_null())
        return results

class ResultURIsV2(AgentBaseHandler):
    @authenticate_token
    def get(self):
        results = self.get_uris()
        self.set_header('Content-Type', 'application/json')
        self.write(dumps(results, indent=4))

    @receiver_catch_it
    @agent_results_message
    def get_uris(self):
        results = get_result_uris(version='v1')
        uri_operation = AgentQueueOperation()
        uri_operation.fill_in_defaults()
        uri_operation.plugin = 'core'
        uri_operation.operation = AgentOperations.REFRESH_RESPONSE_URIS
        uri_operation.data = results.data
        results.operations.append(uri_operation.to_dict_non_null())
        return results
