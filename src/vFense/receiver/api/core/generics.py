import logging

from json import dumps

from vFense import VFENSE_LOGGING_CONFIG
from vFense.receiver.api.base import AgentBaseHandler
from vFense.core.decorators import (
    convert_json_to_arguments, results_message
)
from vFense.receiver.results import AgentApiResultKeys
from vFense.receiver.status_codes import AgentResultCodes
from vFense.core.operations.decorators import log_operation
from vFense.core.operations._admin_constants import AdminActions
from vFense.core.operations._constants import vFenseObjects
from vFense.receiver.api.decorators import (
    authenticate_token, agent_results_message
)


logging.config.fileConfig(VFENSE_LOGGING_CONFIG)
logger = logging.getLogger('rvlistener')

class ValidateToken(AgentBaseHandler):
    @authenticate_token
    def get(self):
        results = self.validate_token()
        self.set_header('Content-Type', 'application/json')
        self.set_status(results[AgentApiResultKeys.HTTP_STATUS_CODE])
        self.write(dumps(results, indent=4))

    @agent_results_message
    def validate_token(self):
        return {
            AgentApiResultKeys.VFENSE_STATUS_CODE: (
                AgentResultCodes.TokenValidated
            )
        }

