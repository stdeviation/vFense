from json import dumps

from vFense.core.api.base import BaseHandler
from vFense.core.decorators import (
    convert_json_to_arguments, api_catch_it, results_message
)
from vFense.core.agent._db_model import AgentKeys
from vFense.core.agent import Agent
from vFense.core.agent.manager import AgentManager
from vFense.core.operations._constants import AgentOperations
from vFense.core.queue import AgentQueueOperation
from vFense.core.queue.uris import get_result_uris
from vFense.core.results import AgentApiResults
from vFense.core.receiver.api.base import AgentBaseHandler
from vFense.core.receiver.api.decorators import (
    agent_results_message, agent_authenticated_request, receiver_catch_it,
    authenticate_agent
)
from vFense.core.receiver.status_codes import AgentResultCodes
from vFense.core.receiver.handler import HandOff


class StartUpV1(BaseHandler):
    @agent_authenticated_request
    @convert_json_to_arguments
    def put(self, agent_id):
        rebooted = self.arguments.get(AgentKeys.Rebooted)
        plugins = self.arguments.get(AgentKeys.Plugins)
        system_info = self.arguments.get(AgentKeys.SystemInfo)
        hardware = self.arguments.get(AgentKeys.Hardware)
        view_name = self.arguments.get('customer_name')
        results = (
            self.update_agent(
                agent_id, system_info, hardware, [view_name],
                plugins, rebooted
            )
        )
        self.set_status(results.http_status_code)
        self.set_header('Content-Type', 'application/json')
        self.write(dumps(results.to_dict_non_null()))

    @api_catch_it
    @results_message
    def update_agent(self, agent_id, system_info, hardware, views,
                     plugins, rebooted):
        system_info[AgentKeys.Hardware] = hardware
        system_info[AgentKeys.Views] = views
        agent = Agent(**system_info)
        manager = AgentManager(agent_id)
        results = AgentApiResults(**manager.update(agent))
        status_code = results.vfense_status_code
        if status_code == AgentResultCodes.StartUpSucceeded:
            uri_results = get_result_uris(agent_id, version='v1')
            uri_operation = AgentQueueOperation()
            uri_operation.fill_in_defaults()
            uri_operation.plugin = 'core'
            uri_operation.agent_id = agent_id
            uri_operation.operation = AgentOperations.REFRESH_RESPONSE_URIS
            uri_operation.data = uri_results.data
            results.operations.append(uri_operation.to_dict_non_null())
            if 'rv' in plugins:
                HandOff().startup_operation(
                    agent_id, plugins['rv']['data']
                )

        return results


class StartUpV2(AgentBaseHandler):
    @convert_json_to_arguments
    @authenticate_agent
    def put(self, agent_id):
        views = self.arguments.get(AgentKeys.Views)
        system_info = self.arguments.get(AgentKeys.SystemInfo)
        hardware = self.arguments.get(AgentKeys.Hardware)
        tags = self.arguments.get(AgentKeys.Tags)
        plugins = self.arguments.get(AgentKeys.Plugins)
        results = (
            self.update_agent(
                agent_id, system_info, hardware, views, tags, plugins
            )
        )
        self.set_header('Content-Type', 'application/json')
        self.set_status(results.http_status_code)
        self.write(dumps(results.to_dict_non_null(), indent=4))

    @receiver_catch_it
    @agent_results_message
    def update_agent(self, agent_id, system_info, hardware, views,
                     tags, plugins):
        system_info[AgentKeys.Hardware] = hardware
        system_info[AgentKeys.Views] = views
        agent = Agent(**system_info)
        manager = AgentManager(agent_id)
        results = AgentApiResults(**manager.update(agent, tags))
        if results.status_code == AgentResultCodes.StartUpSucceeded:
            uri_results = get_result_uris(agent_id, version='v1')
            uri_operation = AgentQueueOperation()
            uri_operation.fill_in_defaults()
            uri_operation.plugin = 'core'
            uri_operation.agent_id = agent_id
            uri_operation.operation = AgentOperations.REFRESH_RESPONSE_URIS
            uri_operation.data = uri_results.data
            results.operations.append(uri_operation.to_dict_non_null())
            if 'rv' in plugins:
                HandOff().startup_operation(
                    agent_id, plugins['rv']['data']
                )

        return results
