import logging

from json import dumps

from vFense import VFENSE_LOGGING_CONFIG
from vFense.errorz.error_messages import GenericResults, UpdateApplicationsResults
from vFense.core.api.base import BaseHandler
from vFense.core.decorators import (
    agent_authenticated_request, convert_json_to_arguments, results_message
)

from vFense.plugins.patching.operations.patching_results import \
    PatchingOperationResults

from vFense.receiver.rvhandler import RvHandOff
from vFense.core.user.manager import UserManager
from vFense.core.user import UserKeys

from vFense.core.operations._constants import AgentOperations

#from server.handlers import *

logging.config.fileConfig(VFENSE_LOGGING_CONFIG)
logger = logging.getLogger('rvlistener')


class UpdateApplicationsV1(BaseHandler):
    @agent_authenticated_request
    @convert_json_to_arguments
    def put(self, agent_id):
        username = self.get_current_user()
        view_name = (
            UserManager(username).get_attribute(UserKeys.CurrentView)
        )

        uri = self.request.uri
        method = self.request.method

        try:
            operation_id = self.arguments.get('operation_id', None)
            error = self.arguments.get('error', None)
            success = self.arguments.get('success', 'true')
            apps_data = self.arguments.get('data')
            status_code = self.arguments.get('status_code', None)

            RvHandOff(
                username, view_name, uri, method
            ).refresh_apps_operation(agent_id, apps_data)

            if operation_id:
                logger.info("self.arguments: {0}".format(self.arguments))

                update_results = PatchingOperationResults(
                    username, agent_id,
                    operation_id, success, error,
                    status_code
                )

                results = self.apps_refresh_results(update_results)
                self.set_status(results['http_status'])
                self.write(dumps(results))

            else:
                results = (
                    UpdateApplicationsResults(username, uri, method)
                    .applications_updated(agent_id, apps_data)
                )

                results['data'] = []
                self.set_status(results['http_status'])
                self.write(dumps(results))

        except Exception as e:
            results = GenericResults(
                username, uri, method
            ).something_broke(agent_id, AgentOperations.REFRESH_APPS, e)
            logger.exception(results)

            self.set_status(results['http_status'])
            self.write(dumps(results))

    @results_message
    def apps_refresh_results(update_results):
        results = update_results.apps_refresh()
        return results
