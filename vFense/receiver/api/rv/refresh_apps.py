import logging

from json import dumps

from vFense import VFENSE_LOGGING_CONFIG
from vFense.core.results import Results, UpdateApplicationsResults
from vFense.core.api.base import BaseHandler
from vFense.receiver.api.decorators import authenticate_agent
from vFense.core.decorators import (
    convert_json_to_arguments, results_message
)

from vFense.plugins.patching.operations.patching_results import (
    PatchingOperationResults
)
from vFense.receiver.rvhandler import RvHandOff

from vFense.core.operations._constants import AgentOperations

#from server.handlers import *

logging.config.fileConfig(VFENSE_LOGGING_CONFIG)
logger = logging.getLogger('rvlistener')

class RefreshAppsV2(BaseHandler):
    @authenticate_agent
    @convert_json_to_arguments
    def put(self, agent_id):
        uri = self.request.uri
        method = self.request.method

        try:
            operation_id = self.arguments.get('operation_id', None)
            error = self.arguments.get('error', None)
            success = self.arguments.get('success', 'true')
            apps_data = self.arguments.get('data')
            status_code = self.arguments.get('status_code', None)

            RvHandOff(
            ).refresh_apps_operation(agent_id, apps_data)

            if operation_id:
                logger.info("self.arguments: {0}".format(self.arguments))

                update_results = PatchingOperationResults(
                    agent_id, operation_id, success, error, status_code
                )

                results = self.refresh_apps_results(update_results)
                self.set_status(results['http_status'])
                self.write(dumps(results))

            else:
                results = (
                    UpdateApplicationsResults('agent', uri, method)
                    .applications_updated(agent_id, apps_data)
                )

                results['data'] = []
                self.set_status(results['http_status'])
                self.write(dumps(results))

        except Exception as e:
            results = Results(
                'agent', uri, method
            ).something_broke(agent_id, AgentOperations.REFRESH_APPS, e)
            logger.exception(results)

            self.set_status(results['http_status'])
            self.write(dumps(results))

    @results_message
    def refresh_apps_results(update_results):
        results = update_results.apps_refresh()
        return results
