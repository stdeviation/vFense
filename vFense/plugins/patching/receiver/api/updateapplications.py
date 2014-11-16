import logging

from json import dumps

from vFense._constants import VFENSE_LOGGING_CONFIG
from vFense.core.results import Results, ApiResultKeys
from vFense.core.api.base import BaseHandler
from vFense.core.decorators import (
    agent_authenticated_request, convert_json_to_arguments, results_message
)

from vFense.plugins.patching.operations.patching_results import (
    PatchingOperationResults
)
from vFense.core.receiver.rvhandler import RvHandOff


#from server.handlers import *

logging.config.fileConfig(VFENSE_LOGGING_CONFIG)
logger = logging.getLogger('vfense_listenerener')


class UpdateApplicationsV1(BaseHandler):
    @agent_authenticated_request
    @convert_json_to_arguments
    def put(self, agent_id):
        active_user = self.get_current_user()
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
                data = {
                    ApiResultKeys.MESSAGE: (
                        'Received application updates for agent {0}'
                    .format(agent_id)
                    )
                }
                results = (
                    Results(
                        active_user, self.request.uri, self.request.method
                    ).information_retrieved(**data)
                )
                results['data'] = []
                self.set_status(results['http_status'])
                self.write(dumps(results))

        except Exception as e:
            data = {
                ApiResultKeys.MESSAGE: (
                    'Refresh apps failed for agent {0} broke: {1}'
                    .format(agent_id, e)
                )
            }
            results = (
                Results(
                    active_user, self.request.uri, self.request.method
                ).something_broke(**data)
            )
            logger.exception(results)

            self.set_status(results['http_status'])
            self.write(dumps(results))

    @results_message
    def refresh_apps_results(update_results):
        results = update_results.refresh_apps()
        return results

