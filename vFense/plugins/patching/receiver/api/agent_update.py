from json import dumps

from vFense.core.api.base import BaseHandler
from vFense.core.decorators import (
    convert_json_to_arguments, api_catch_it, results_message
)
from vFense.core.results import ApiResults

from vFense.core.receiver.api.base import AgentBaseHandler
from vFense.core.receiver.decorators import (
    agent_results_message, agent_authenticated_request,
    receiver_catch_it, authenticate_agent
)
from vFense.core.receiver.status_codes import AgentResultCodes
from vFense.plugins.patching.receiver.handoff import PatcherHandOff


class AgentUpdateHandlerV1(BaseHandler):
    @agent_authenticated_request
    @convert_json_to_arguments
    def put(self, agent_id):
        app_data = self.arguments.get('data')
        results = self.agent_update(agent_id, app_data)
        self.set_status(results.http_status_code)
        self.write(dumps(results.to_dict_non_null()))

    @api_catch_it
    @results_message
    def avail_agent_update(self, agent_id, app_data):
        handoff = PatcherHandOff(agent_id=agent_id, app_data=app_data)
        handoff.available_agent_update_operation()
        results = ApiResults()
        results.fill_in_defaults()
        results.message = 'Received agent update for {0}'.format(agent_id)
        results.generic_status_code = AgentResultCodes.InformationRetrieved
        results.vfense_status_code = AgentResultCodes.InformationRetrieved
        return results

class AgentUpdateHandlerV2(AgentBaseHandler):
    @authenticate_agent
    @convert_json_to_arguments
    def put(self, agent_id):
        app_data = self.arguments.get('data')
        print self.arguments.keys()
        results = self.agent_update(agent_id, app_data)
        self.set_status(results.http_status_code)
        self.write(dumps(results.to_dict_non_null()))

    @receiver_catch_it
    @agent_results_message
    def agent_update(self, agent_id, app_data):
        handoff = PatcherHandOff(agent_id=agent_id, apps_data=app_data)
        handoff.available_agent_update_operation()
        results = ApiResults()
        results.fill_in_defaults()
        results.message = 'Received agent update for {0}'.format(agent_id)
        results.generic_status_code = AgentResultCodes.InformationRetrieved
        results.vfense_status_code = AgentResultCodes.InformationRetrieved
        return results
