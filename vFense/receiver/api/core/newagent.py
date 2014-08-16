import logging

from json import dumps

from vFense import VFENSE_LOGGING_CONFIG
from vFense.core.api.base import BaseHandler
from vFense.receiver.api.base import AgentBaseHandler
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
from vFense.core.results import ApiResultKeys, Results
from vFense.receiver.status_codes import AgentResultCodes
from vFense.receiver.results import AgentResults
from vFense.receiver.rvhandler import RvHandOff
from vFense.core.operations.decorators import log_operation
from vFense.core.operations._admin_constants import AdminActions
from vFense.core.operations._constants import vFenseObjects
from vFense.receiver.api.decorators import (
    authenticate_token, agent_results_message
)

logging.config.fileConfig(VFENSE_LOGGING_CONFIG)
logger = logging.getLogger('rvlistener')


class NewAgentV1(BaseHandler):
    @agent_authenticated_request
    @convert_json_to_arguments
    def post(self):
        active_user = self.get_current_user()

        try:
            view_name = self.arguments.get('customer_name')
            plugins = self.arguments.get(AgentKeys.Plugins)
            system_info = self.arguments.get(AgentKeys.SystemInfo)
            hardware = self.arguments.get(AgentKeys.Hardware)
            results = (
                self.add_agent(
                    system_info, hardware, view_name
                )
            )
            status_code = results[ApiResultKeys.VFENSE_STATUS_CODE]
            if status_code == AgentResultCodes.NewAgentSucceeded:
                results[ApiResultKeys.DATA].pop(0)
                agent_id = results[ApiResultKeys.GENERATED_IDS]
                try:
                    if 'rv' in plugins:
                        RvHandOff().new_agent_operation(
                            agent_id,
                            plugins['rv']['data'],
                        )

                except Exception as e:
                    logger.exception(e)

            self.set_header('Content-Type', 'application/json')
            self.set_status(results[ApiResultKeys.HTTP_STATUS_CODE])
            self.write(dumps(results, indent=4))

        except Exception as e:
            data = {
                ApiResultKeys.MESSAGE: (
                    'New agent operation broke: {0}'
                    .format(e)
                )
            }
            results = (
                Results(
                    active_user, self.request.uri, self.request.method
                ).something_broke(**data)
            )
            logger.exception(e)
            self.set_header('Content-Type', 'application/json')
            self.set_status(results[ApiResultKeys.HTTP_STATUS_CODE])
            self.write(dumps(results, indent=4))

    @results_message
    @log_operation(AdminActions.NEW_AGENT, vFenseObjects.AGENT)
    def add_agent(self, system_info, hardware, view):
        system_info[AgentKeys.Hardware] = hardware
        system_info[AgentKeys.Views] = [view]
        system_info.pop(AgentKeys.HostName, None)
        system_info.pop('customer_name', None)
        agent = Agent(**system_info)
        manager = AgentManager()
        results = manager.create(agent)
        status_code = results[ApiResultKeys.VFENSE_STATUS_CODE]
        if status_code == AgentResultCodes.NewAgentSucceeded:
            agent_id = results[ApiResultKeys.GENERATED_IDS]
            uris = get_result_uris(agent_id, version='v1')
            uris[AgentOperationKey.Operation] = (
                AgentOperations.REFRESH_RESPONSE_URIS
            )
            json_msg = {
                AgentOperationKey.Operation: "new_agent_id",
                AgentOperationKey.OperationId: "",
                OperationPerAgentKey.AgentId: agent_id
            }
            results[ApiResultKeys.DATA] = [results[ApiResultKeys.DATA]]
            results[ApiResultKeys.DATA].append(json_msg)
            results[ApiResultKeys.DATA].append(uris)
        return results


class NewAgentV2(AgentBaseHandler):
    @authenticate_token
    @convert_json_to_arguments
    def post(self):
        try:
            views = self.arguments.get(AgentKeys.Views)
            system_info = self.arguments.get(AgentKeys.SystemInfo)
            hardware = self.arguments.get(AgentKeys.Hardware)
            tags = self.arguments.get(AgentKeys.Tags)
            plugins = self.arguments.get(AgentKeys.Plugins)
            results = (
                self.add_agent(system_info, hardware, views, tags)
            )
            status_code = results[ApiResultKeys.VFENSE_STATUS_CODE]
            if status_code == AgentResultCodes.NewAgentSucceeded:
                results[ApiResultKeys.DATA].pop(0)
                agent_id = results[ApiResultKeys.GENERATED_IDS]
                try:
                    if 'rv' in plugins:
                        RvHandOff(
                        ).new_agent_operation(
                            agent_id, plugins['rv']['data']
                        )

                except Exception as e:
                    logger.exception(e)

            self.set_header('Content-Type', 'application/json')
            self.set_status(results[ApiResultKeys.HTTP_STATUS_CODE])
            self.write(dumps(results, indent=4))

        except Exception as e:
            data = {
                ApiResultKeys.MESSAGE: (
                    'New agent operation broke: {0}'
                    .format(e)
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
    def add_agent(self, system_info, hardware, views, tags):
        system_info[AgentKeys.Hardware] = hardware
        system_info[AgentKeys.Views] = views
        agent = Agent(**system_info)
        manager = AgentManager()
        results = manager.create(agent, tags)
        results[ApiResultKeys.OPERATIONS] = []
        results[ApiResultKeys.DATA] = [results[ApiResultKeys.DATA]]
        status_code = results[ApiResultKeys.VFENSE_STATUS_CODE]
        if status_code == AgentResultCodes.NewAgentSucceeded:
            agent_id = results[ApiResultKeys.GENERATED_IDS]
            uris = get_result_uris(agent_id, version='v2')
            uris[AgentOperationKey.Operation] = (
                AgentOperations.REFRESH_RESPONSE_URIS
            )
            new_agent_id = {
                AgentOperationKey.Operation: "new_agent_id",
                AgentOperationKey.OperationId: "",
                OperationPerAgentKey.AgentId: agent_id
            }
            results[ApiResultKeys.OPERATIONS].append(new_agent_id)
            results[ApiResultKeys.OPERATIONS].append(uris)
        return results
