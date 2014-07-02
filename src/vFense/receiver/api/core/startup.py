import logging

from json import dumps

from vFense import VFENSE_LOGGING_CONFIG
from vFense.core.api.base import BaseHandler
from vFense.core.api.decorators import authenticate_agent
from vFense.core.decorators import (
    convert_json_to_arguments, agent_authenticated_request, results_message
)

from vFense.core.agent._db_model import (
    AgentKeys
)
from vFense.result.error_messages import GenericResults
from vFense.core.queue.uris import get_result_uris
from vFense.result._constants import ApiResultKeys
from vFense.result.status_codes import AgentResultCodes

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
        username = self.get_current_user()
        uri = self.request.uri
        method = self.request.method
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
            uris = get_result_uris(agent_id, username, uri, method)
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
            status = (
                GenericResults(
                    username, uri, method
                ).something_broke(agent_id, 'startup', e)
            )

            logger.exception(status['message'])
            self.write(dumps(status))

    @results_message
    def update_agent(self, agent_id, agent_data, hardware, views):
        agent_data[AgentKeys.Hardware] = hardware
        agent_data[AgentKeys.Views] = views
        agent = Agent(**agent_data)
        manager = AgentManager(agent_id)
        results = manager.update(agent)
        status_code = results[ApiResultKeys.VFENSE_STATUS_CODE]
        if status_code == AgentResultCodes.StartUpSucceeded:
            uris = get_result_uris(agent_id)
            uris[AgentOperationKey.Operation] = (
                AgentOperations.REFRESH_RESPONSE_URIS
            )
            results[ApiResultKeys.DATA].append(uris)

        return results


class StartUpV2(BaseHandler):
    @authenticate_agent
    @convert_json_to_arguments
    def post(self, agent_id):
        username = self.get_current_user()
        uri = self.request.uri
        method = self.request.method

        try:
            views = self.arguments.get(AgentKeys.Views)
            system_info = self.arguments.get(AgentKeys.SystemInfo)
            hardware = self.arguments.get(AgentKeys.Hardware)
            tags = self.arguments.get(AgentKeys.Tags)
            plugins = self.arguments.get(AgentKeys.Plugins)
            results, agent_info = (
                self.update_agent(
                    system_info, hardware, views, tags
                )
            )
            status_code = results[ApiResultKeys.VFENSE_STATUS_CODE]

            if status_code == AgentResultCodes.StartUpSucceeded:
                if 'rv' in plugins:
                    RvHandOff(
                    ).startup_operation(agent_id, plugins['rv']['data'])

            self.set_header('Content-Type', 'application/json')
            self.set_status(results[ApiResultKeys.HTTP_STATUS_CODE])
            self.write(dumps(results, indent=4))

        except Exception as e:
            results = (
                GenericResults(
                    username, uri, method
                ).something_broke('agent', 'startup', e)
            )
            logger.exception(e)
            self.set_header('Content-Type', 'application/json')
            self.set_status(results[ApiResultKeys.HTTP_STATUS_CODE])
            self.write(dumps(results, indent=4))

    @results_message
    def update_agent(self, agent_id, system_info, hardware, views, tags):
        system_info[AgentKeys.Hardware] = hardware
        system_info[AgentKeys.Views] = views
        agent = Agent(**system_info)
        manager = AgentManager(agent_id)
        results = manager.update(agent, tags)
        results[ApiResultKeys.OPERATIONS] = (
            [results[ApiResultKeys.DATA]]
        )
        status_code = results[ApiResultKeys.VFENSE_STATUS_CODE]
        if status_code == AgentResultCodes.StartUpSucceeded:
            uris = get_result_uris(agent_id)
            uris[AgentOperationKey.Operation] = (
                AgentOperations.REFRESH_RESPONSE_URIS
            )
            results[ApiResultKeys.OPERATIONS].append(uris)
        return results
