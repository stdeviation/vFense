import logging
from json import dumps

from vFense import VFENSE_LOGGING_CONFIG
from vFense.core.api.base import BaseHandler
from vFense.core.decorators import (
    results_message
)
from vFense.core.queue.uris import get_result_uris
from vFense.result.error_messages import GenericResults
from vFense.receiver.api.decorators import authenticate_token


logging.config.fileConfig(VFENSE_LOGGING_CONFIG)
logger = logging.getLogger('rvlistener')

class AgentResultURIs(BaseHandler):
    @authenticate_token
    def get(self, agent_id):
        username = self.get_current_user()
        uri = self.request.uri
        method = self.request.method
        try:
            results = self.get_uris(agent_id)
            self.set_header('Content-Type', 'application/json')
            self.write(dumps(results, indent=4))

        except Exception as e:
            status = (
                GenericResults(
                    username, uri, method
                ).something_broke('uris', 'refresh_response_uris', e)
            )
            logger.exception(e)
            self.write(dumps(status, indent=4))

    @results_message
    def get_uris(self, agent_id):
        results = get_result_uris(agent_id, 'v1')
        return results

class ResultURIs(BaseHandler):
    @authenticate_token
    def get(self):
        username = self.get_current_user()
        uri = self.request.uri
        method = self.request.method
        try:
            results = self.get_uris()
            self.set_header('Content-Type', 'application/json')
            self.write(dumps(results, indent=4))

        except Exception as e:
            status = (
                GenericResults(
                    username, uri, method
                ).something_broke('uris', 'refresh_response_uris', e)
            )
            logger.exception(e)
            self.write(dumps(status, indent=4))

    @results_message
    def get_uris(self):
        results = get_result_uris(version='v1')
        return results

class AgentResultURIsV2(BaseHandler):
    @authenticate_token
    def get(self, agent_id):
        username = self.get_current_user()
        uri = self.request.uri
        method = self.request.method
        try:
            results = self.get_uris(agent_id)
            self.set_header('Content-Type', 'application/json')
            self.write(dumps(results, indent=4))

        except Exception as e:
            status = (
                GenericResults(
                    username, uri, method
                ).something_broke('uris', 'refresh_response_uris', e)
            )
            logger.exception(e)
            self.write(dumps(status, indent=4))

    @results_message
    def get_uris(self, agent_id):
        results = get_result_uris(agent_id, 'v2')
        return results

class ResultURIsV2(BaseHandler):
    @authenticate_token
    def get(self):
        username = self.get_current_user()
        uri = self.request.uri
        method = self.request.method
        try:
            results = self.get_uris()
            self.set_header('Content-Type', 'application/json')
            self.write(dumps(results, indent=4))

        except Exception as e:
            status = (
                GenericResults(
                    username, uri, method
                ).something_broke('uris', 'refresh_response_uris', e)
            )
            logger.exception(e)
            self.write(dumps(status, indent=4))

    @results_message
    def get_uris(self):
        results = get_result_uris(version='v2')
        return results
