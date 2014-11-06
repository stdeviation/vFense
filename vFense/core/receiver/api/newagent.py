from json import dumps

from vFense.core.api.base import BaseHandler
from vFense.core.decorators import (
    convert_json_to_arguments, results_message, api_catch_it
)
from vFense.core.agent._db_model import AgentKeys
from vFense.core.operations._constants import AgentOperations
from vFense.core.agent import Agent
from vFense.core.agent.manager import AgentManager
from vFense.core.queue import AgentQueueOperation
from vFense.core.queue.uris import get_result_uris
from vFense.core.results import AgentApiResults
from vFense.core.operations.decorators import log_operation
from vFense.core.operations._admin_constants import AdminActions
from vFense.core.operations._constants import vFenseObjects
from vFense.core.receiver.decorators import (
    authenticate_token, agent_results_message, agent_authenticated_request,
    receiver_catch_it
)
from vFense.core.receiver.api.base import AgentBaseHandler
from vFense.core.receiver.status_codes import AgentResultCodes
from vFense.core.receiver.handoff import HandOff


class NewAgentV1(BaseHandler):
    @agent_authenticated_request
    @convert_json_to_arguments
    def post(self):
        view_name = self.arguments.get('customer_name')
        plugins = self.arguments.get(AgentKeys.Plugins)
        system_info = self.arguments.get(AgentKeys.SystemInfo)
        hardware = self.arguments.get(AgentKeys.Hardware)
        results = self.add_agent(system_info, hardware, view_name, plugins)

        self.set_header('Content-Type', 'application/json')
        self.set_status(results.http_status_code)
        self.write(dumps(results.to_dict_non_null(), indent=4))

    @api_catch_it
    @results_message
    @log_operation(AdminActions.NEW_AGENT, vFenseObjects.AGENT)
    def add_agent(self, system_info, hardware, view, plugins):
        system_info[AgentKeys.Hardware] = hardware
        system_info[AgentKeys.Views] = [view]
        system_info.pop(AgentKeys.HostName, None)
        system_info.pop('customer_name', None)
        agent = Agent(**system_info)
        manager = AgentManager()
        results = AgentApiResults(**manager.create(agent))
        status_code = results.vfense_status_code
        if status_code == AgentResultCodes.NewAgentSucceeded:
            agent_id = results.generated_ids
            uri_results = get_result_uris(agent_id, version='v1')
            uri_operation = AgentQueueOperation()
            uri_operation.fill_in_defaults()
            uri_operation.plugin = 'core'
            uri_operation.agent_id = agent_id
            uri_operation.operation = AgentOperations.REFRESH_RESPONSE_URIS
            uri_operation.data = uri_results.data
            newagent_operation = AgentQueueOperation()
            newagent_operation.fill_in_defaults()
            newagent_operation.operation = 'new_agent_id'
            newagent_operation.plugin = 'core'
            newagent_operation.agent_id = agent_id
            results.operations.append(newagent_operation.to_dict_non_null())
            results.operations.append(uri_operation.to_dict_non_null())
            if 'rv' in plugins:
                HandOff().new_agent_operation(
                    agent_id, plugins['rv']['data']
                )

        return results


class NewAgentV2(AgentBaseHandler):
    @authenticate_token
    @convert_json_to_arguments
    def post(self):
        views = self.arguments.get(AgentKeys.Views)
        system_info = self.arguments.get(AgentKeys.SystemInfo)
        hardware = self.arguments.get(AgentKeys.Hardware)
        tags = self.arguments.get(AgentKeys.Tags)
        plugins = self.arguments.get(AgentKeys.Plugins)
        results = self.add_agent(system_info, hardware, views, tags, plugins)
        self.set_header('Content-Type', 'application/json')
        self.set_status(results.http_status_code)
        self.write(dumps(results.to_dict_non_null(), indent=4))

    @receiver_catch_it
    @agent_results_message
    def add_agent(self, system_info, hardware, views, tags, plugins):
        system_info[AgentKeys.Hardware] = hardware
        system_info[AgentKeys.Views] = views
        agent = Agent(**system_info)
        manager = AgentManager()
        results = AgentApiResults(**manager.create(agent, tags))
        results.fill_in_defaults()
        results.data = [results.data]
        status_code = results.vfense_status_code
        if status_code == AgentResultCodes.NewAgentSucceeded:
            agent_id = results.generated_ids
            uri_results = get_result_uris(agent_id, version='v2')
            uri_operation = AgentQueueOperation()
            uri_operation.fill_in_defaults()
            uri_operation.plugin = 'core'
            uri_operation.agent_id = agent_id
            uri_operation.operation = AgentOperations.REFRESH_RESPONSE_URIS
            uri_operation.data = uri_results.data
            newagent_operation = AgentQueueOperation()
            newagent_operation.fill_in_defaults()
            newagent_operation.operation = 'new_agent_id'
            newagent_operation.plugin = 'core'
            newagent_operation.agent_id = agent_id
            results.operations.append(newagent_operation.to_dict_non_null())
            results.operations.append(uri_operation.to_dict_non_null())
            if 'rv' in plugins:
                HandOff().new_agent_operation(
                    agent_id, plugins['rv']['data']
                )
        return results
