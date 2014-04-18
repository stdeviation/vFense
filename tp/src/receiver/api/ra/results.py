import logging

import simplejson as json

from vFense.server.handlers import BaseHandler
from vFense.server.hierarchy.decorators import authenticated_request
from vFense.server.hierarchy.decorators import convert_json_to_arguments

from vFense.plugins.ra.operations.ra_results import RaOperationResults

from vFense.plugins.ra.processor import Processor

logging.config.fileConfig('/opt/TopPatch/conf/logging.config')
logger = logging.getLogger('rvlistener')


class RemoteDesktopResults(BaseHandler):

    @authenticated_request
    @convert_json_to_arguments
    def post(self):

        username = self.get_current_user()
        uri = self.request.uri
        method = self.request.method
        agent_id = self.arguments.get('agent_id')
        operation_id = self.arguments.get('operation_id')
        success = self.arguments.get('success')
        error = self.arguments.get('error', None)
        status_code = self.arguments.get('status_code', None)

        logger.info(
            'Data received on remote desktop results: %s' %
            (self.request.body)
        )

        processor = Processor()
        processor.handle(self.arguments)

        print self.arguments
        results = (
            RaOperationResults(
                username, agent_id,
                operation_id, success, error,
                status_code, uri, method
            )
        )
        results_data = results.ra()

        #result = AgentResults(
        #    username, self.request.uri, "POST"
        #).ra_results(agent_id)

        self.set_header('Content-Type', 'application/json')
        self.write(json.dumps(results_data))
