from json import dumps

from vFense.core.agent.manager import AgentManager
from vFense.core.api.base import BaseHandler
from vFense.core.decorators import api_catch_it, results_message
from vFense.core.receiver.decorators import (
    agent_results_message, receiver_catch_it, agent_authenticated_request
)
from vFense.receiver.api.base import AgentBaseHandler
from vFense.receiver.api.decorators import authenticate_agent
from vFense.receiver.corehandler import process_queue_data

class CheckInV1(BaseHandler):
    @agent_authenticated_request
    def get(self, agent_id):
        operations = process_queue_data(agent_id)
        results = self.update_agent_status(agent_id)
        results.message = 'checkin succeeded for agent {0}'.format(agent_id)
        results.operations = operations
        self.set_status(results.http_status_code)
        self.set_header('Content-Type', 'application/json')
        self.write(dumps(results.to_dict_non_null()))

    @api_catch_it
    @results_message
    def update_agent_status(self, agent_id):
        manager = AgentManager(agent_id)
        results = manager.update_last_checkin_time()
        return results


class CheckInV2(AgentBaseHandler):
    @authenticate_agent
    def get(self, agent_id):
        operations = process_queue_data(agent_id)
        results = self.update_agent_status(agent_id)
        results.message = 'checkin succeeded for agent {0}'.format(agent_id)
        results.operations = operations
        self.set_status(results.http_status_code)
        self.set_header('Content-Type', 'application/json')
        self.write(dumps(results.to_dict_non_null()))

    @receiver_catch_it
    @agent_results_message
    def update_agent_status(self, agent_id):
        manager = AgentManager(agent_id)
        results = manager.update_last_checkin_time()
        return results
