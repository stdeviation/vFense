import logging

from json import dumps

from vFense._constants import VFENSE_LOGGING_CONFIG
from vFense.core.api.base import BaseHandler
from vFense.receiver.api.decorators import authenticate_agent
from vFense.core.decorators import (
    convert_json_to_arguments, agent_authenticated_request, results_message
)

from vFense.core.agent._db_model import (
    AgentKeys
)
from vFense.core.results import Results, ApiResultKeys
from vFense.receiver.results import AgentResults, AgentApiResultKeys
from vFense.receiver.api.base import AgentBaseHandler
from vFense.receiver.api.decorators import agent_results_message
from vFense.core.queue.uris import get_result_uris
from vFense.receiver.status_codes import AgentResultCodes

from vFense.core.operations._constants import AgentOperations
from vFense.core.operations._db_model import AgentOperationKey

from vFense.receiver.rvhandler import RvHandOff

from vFense.core.agent import Agent
from vFense.core.agent.manager import AgentManager

logging.config.fileConfig(VFENSE_LOGGING_CONFIG)
logger = logging.getLogger('rvlistener')


class StartUpV1(BaseHandler):
    @agent_authenticated_request
    @convert_json_to_arguments
    def put(self, agent_id):
        active_user = self.get_current_user()
        try:
            rebooted = self.arguments.get(AgentKeys.Rebooted)
            plugins = self.arguments.get(AgentKeys.Plugins)
            system_info = self.arguments.get(AgentKeys.SystemInfo)
            hardware = self.arguments.get(AgentKeys.Hardware)
            view_name = self.arguments.get('customer_name')
            agent_data = (
                self.update_agent(
                    agent_id, system_info, hardware, [view_name], rebooted
                )
            )
            uris = get_result_uris(agent_id, 'v1')
            uris[AgentOperationKey.Operation] = (
                AgentOperations.REFRESH_RESPONSE_URIS
            )
            agent_data.pop('data')
            agent_data['data'] = [uris]
            status_code = agent_data[ApiResultKeys.VFENSE_STATUS_CODE]

            if status_code == AgentResultCodes.StartUpSucceeded:
                if 'rv' in plugins:
                    RvHandOff(
                    ).startup_operation(agent_id, plugins['rv']['data'])

            self.set_status(agent_data['http_status'])
            self.set_header('Content-Type', 'application/json')
            self.write(dumps(agent_data))

        except Exception as e:
            data = {
                AgentApiResultKeys.MESSAGE: (
                    'Checkin operation for agent {0} broke: {1}'
                    .format(agent_id, e)
                )
            }
            results = (
                Results(
                    active_user, self.request.uri, self.request.method
                ).something_broke(**data)
            )

            logger.exception(results['message'])
            self.write(dumps(results))

    @results_message
    def update_agent(self, agent_id, agent_data, hardware, views):
        agent_data[AgentKeys.Hardware] = hardware
        agent_data[AgentKeys.Views] = views
        agent = Agent(**agent_data)
        manager = AgentManager(agent_id)
        results = manager.update(agent)
        status_code = results.vfense_status_code
        if status_code == AgentResultCodes.StartUpSucceeded:
            uris = get_result_uris(agent_id)
            uris[AgentOperationKey.Operation] = (
                AgentOperations.REFRESH_RESPONSE_URIS
            )
            results.data.append(uris)

        return results


class StartUpV2(AgentBaseHandler):
    @convert_json_to_arguments
    @authenticate_agent
    def put(self, agent_id):
        try:
            views = self.arguments.get(AgentKeys.Views)
            system_info = self.arguments.get(AgentKeys.SystemInfo)
            hardware = self.arguments.get(AgentKeys.Hardware)
            tags = self.arguments.get(AgentKeys.Tags)
            plugins = self.arguments.get(AgentKeys.Plugins)
            results = (
                self.update_agent(
                    agent_id, system_info, hardware, views, tags
                )
            )
            status_code = results.vfense_status_code

            if status_code == AgentResultCodes.StartUpSucceeded:
                if 'rv' in plugins:
                    RvHandOff(
                    ).startup_operation(agent_id, plugins['rv']['data'])

            self.set_header('Content-Type', 'application/json')
            self.set_status(results[ApiResultKeys.HTTP_STATUS_CODE])
            self.write(dumps(results, indent=4))

        except Exception as e:
            data = {
                ApiResultKeys.MESSAGE: (
                    'start up operation for agent {0} broke: {1}'
                    .format(agent_id, e)
                )
            }
            results = (
                AgentResults(
                    self.request.uri, self.request.method, self.get_token()
                ).something_broke(**data)
            )
            logger.exception(e)
            self.set_header('Content-Type', 'application/json')
            self.set_status(results[ApiResultKeys.HTTP_STATUS_CODE])
            self.write(dumps(results, indent=4))

    @agent_results_message
    def update_agent(self, agent_id, system_info, hardware, views, tags):
        system_info[AgentKeys.Hardware] = hardware
        system_info[AgentKeys.Views] = views
        agent = Agent(**system_info)
        manager = AgentManager(agent_id)
        results = manager.update(agent, tags)
        results[ApiResultKeys.OPERATIONS] = []
        status_code = results.vfense_status_code
        if status_code == AgentResultCodes.StartUpSucceeded:
            uris = get_result_uris(agent_id)
            uris[AgentOperationKey.Operation] = (
                AgentOperations.REFRESH_RESPONSE_URIS
            )
            results[ApiResultKeys.OPERATIONS].append(uris)

        return results
