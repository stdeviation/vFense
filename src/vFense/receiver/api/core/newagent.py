import logging

from json import dumps

from vFense import VFENSE_LOGGING_CONFIG
from vFense.core.api.base import BaseHandler
from vFense.core.decorators import (
    convert_json_to_arguments, agent_authenticated_request,
    results_message
)
from vFense.core.agent._db_model import (
    AgentKeys
)
from vFense.core.operations._db_model import (
    AgentOperationKey, OperationPerAgentKey
)
from vFense.core.operations._constants import AgentOperations
from vFense.core.agent import Agent
from vFense.core.agent.manager import AgentManager
from vFense.core.queue.uris import get_result_uris
from vFense.errorz._constants import ApiResultKeys
from vFense.errorz.error_messages import GenericResults
from vFense.errorz.status_codes import AgentResultCodes
from vFense.receiver.rvhandler import RvHandOff
from vFense.core.operations.decorators import log_operation
from vFense.core.operations._admin_constants import AdminActions
from vFense.core.operations._constants import vFenseObjects


import plugins.ra.handoff as RaHandoff
#from server.handlers import *

logging.config.fileConfig(VFENSE_LOGGING_CONFIG)
logger = logging.getLogger('rvlistener')


class NewAgentV1(BaseHandler):
    @agent_authenticated_request
    @convert_json_to_arguments
    def post(self):
        self.username = self.get_current_user()
        self.uri = self.request.uri
        self.http_method = self.request.method

        try:
            view_name = self.arguments.get('customer_name')
            plugins = self.arguments.get(AgentKeys.Plugins)
            system_info = self.arguments.get(AgentKeys.SystemInfo)
            hardware = self.arguments.get(AgentKeys.Hardware)
            results, agent_info = (
                self.add_agent(
                    system_info, hardware, view_name
                )
            )
            status_code = results[ApiResultKeys.VFENSE_STATUS_CODE]
            if status_code == AgentResultCodes.NewAgentSucceeded:
                agent_id = results[ApiResultKeys.GENERATED_IDS][-1]
                try:
                    if 'rv' in plugins:
                        RvHandOff(
                            self.username, view_name, self.uri,
                            self.http_method
                        ).new_agent_operation(
                            agent_id,
                            plugins['rv']['data'],
                            agent_info
                        )

                    if 'ra' in plugins:
                        RaHandoff.startup(agent_id, plugins['ra'])

                except Exception as e:
                    logger.exception(e)

            self.set_header('Content-Type', 'application/json')
            self.set_status(results[ApiResultKeys.HTTP_STATUS_CODE])
            self.write(dumps(results, indent=4))

        except Exception as e:
            results = (
                GenericResults(
                    self.username, self.uri, self.http_method
                ).something_broke('agent', 'new_agent', e)
            )
            logger.exception(e)
            self.set_header('Content-Type', 'application/json')
            self.set_status(results[ApiResultKeys.HTTP_STATUS_CODE])
            self.write(dumps(results, indent=4))

    @log_operation(AdminActions.NEW_AGENT, vFenseObjects.AGENT)
    @results_message
    def add_agent(self, system_info, hardware, view):
        system_info[AgentKeys.Hardware] = hardware
        system_info[AgentKeys.Views] = [view]
        agent = Agent(**system_info)
        manager = AgentManager()
        results = manager.create(agent)
        agent_info = results[ApiResultKeys.DATA][-1]
        status_code = results[ApiResultKeys.VFENSE_STATUS_CODE]
        if status_code == AgentResultCodes.NewAgentSucceeded:
            agent_id = results[ApiResultKeys.GENERATED_IDS][-1]
            uris = (
                get_result_uris(
                    agent_id, self.username, self.uri, self.http_method
                )
            )
            uris[AgentOperationKey.Operation] = (
                AgentOperations.REFRESH_RESPONSE_URIS
            )
            json_msg = {
                AgentOperationKey.Operation: "new_agent_id",
                AgentOperationKey.OperationId: "",
                OperationPerAgentKey.AgentId: agent_id
            }
            results[ApiResultKeys.DATA] = [json_msg, uris]

        return(results, agent_info)


class NewAgentV2(BaseHandler):
    @agent_authenticated_request
    @convert_json_to_arguments
    def post(self):
        username = self.get_current_user()
        uri = self.request.uri
        method = self.request.method

        try:
            views = self.arguments.get(AgentKeys.Views)
            system_info = self.arguments.get(AgentKeys.SystemInfo)
            hardware = self.arguments.get(AgentKeys.Hardware)
            tags = self.arguments.get(AgentKeys.Tags)
            results, agent_info = (
                self.add_agent(
                    system_info, hardware, views, tags
                )
            )
            self.set_header('Content-Type', 'application/json')
            self.set_status(results[ApiResultKeys.HTTP_STATUS_CODE])
            self.write(dumps(results, indent=4))

        except Exception as e:
            results = (
                GenericResults(
                    username, uri, method
                ).something_broke('agent', 'new_agent', e)
            )
            logger.exception(e)
            self.set_header('Content-Type', 'application/json')
            self.set_status(results[ApiResultKeys.HTTP_STATUS_CODE])
            self.write(dumps(results, indent=4))

    @log_operation(AdminActions.NEW_AGENT, vFenseObjects.AGENT)
    @results_message
    def add_agent(self, system_info, hardware, views, tags):
        system_info[AgentKeys.Hardware] = hardware
        system_info[AgentKeys.Views] = views
        agent = Agent(**system_info)
        manager = AgentManager()
        results = manager.create(agent, tags)
        return results
