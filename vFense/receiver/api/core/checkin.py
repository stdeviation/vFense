import logging
from json import dumps

from vFense import VFENSE_LOGGING_CONFIG
from vFense.core.agent.manager import AgentManager
from vFense.core.results import ApiResultKeys, Results
from vFense.core.api.base import BaseHandler
from vFense.core.decorators import (
    agent_authenticated_request, results_message
)

from vFense.receiver.api.base import AgentBaseHandler
from vFense.receiver.results import AgentResults, AgentApiResultKeys
from vFense.receiver.corehandler import process_queue_data

from vFense.receiver.api.decorators import authenticate_agent

logging.config.fileConfig(VFENSE_LOGGING_CONFIG)
logger = logging.getLogger('rvlistener')


class CheckInV1(BaseHandler):
    @agent_authenticated_request
    def get(self, agent_id):
        active_user = self.get_current_user()
        try:
            agent_queue = process_queue_data(agent_id)
            data = {
                ApiResultKeys.DATA: agent_queue,
                ApiResultKeys.MESSAGE: (
                    '{0} - checkin succeeded for agent_id {1}'
                    .format(active_user, agent_id)
                )
            }
            results = (
                Results(
                    active_user, self.request.uri, self.request.method
                ).something_broke(**data)
            )
            self.update_agent_status(agent_id)
            self.set_status(results['http_status'])
            self.set_header('Content-Type', 'application/json')
            self.write(dumps(results))

        except Exception as e:
            data = {
                ApiResultKeys.MESSAGE: (
                    'Checkin operation for agent {0} broke: {1}'
                    .format(agent_id, e)
                )
            }
            results = (
                Results(
                    active_user, self.request.uri, self.request.method
                ).something_broke(**data)
            )
            logger.exception(e)
            self.set_status(results['http_status'])
            self.set_header('Content-Type', 'application/json')
            self.write(dumps(results))


    @results_message
    def update_agent_status(self, agent_id):
        manager = AgentManager(agent_id)
        results = manager.update_last_checkin_time()
        return results


class CheckInV2(AgentBaseHandler):
    @authenticate_agent
    def get(self, agent_id):
        try:
            results = (
                self.update_agent_status(
                    agent_id
                )
            )
            self.set_status(results['http_status'])
            self.set_header('Content-Type', 'application/json')
            self.write(dumps(results))

        except Exception as e:
            data = {
                AgentApiResultKeys.MESSAGE: (
                    'Checkin operation for agent {0} broke: {1}'
                    .format(agent_id, e)
                )
            }
            results = (
                AgentResults(
                    self.request.uri, self.request.method, self.get_token(),
                    agent_id
                ).something_broke(**data)
            )
            logger.exception(e)
            self.set_status(results['http_status'])
            self.set_header('Content-Type', 'application/json')
            self.write(dumps(results))


    def update_agent_status(self, agent_id):
        manager = AgentManager(agent_id)
        manager.update_last_checkin_time()
        agent_queue = process_queue_data(agent_id)
        data = {ApiResultKeys.OPERATIONS: agent_queue}
        status = (
            AgentResults(
                self.request.uri, self.request.method,
                self.get_token(), agent_id
            ).check_in(**data)
        )
        return status
