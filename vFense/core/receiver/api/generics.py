import logging

from json import dumps

from vFense._constants import VFENSE_LOGGING_CONFIG
from vFense.core.results import ApiResults
from vFense.receiver.tokens import validate_token
from vFense.receiver.api.base import AgentBaseHandler
from vFense.receiver.status_codes import (
    AgentResultCodes, AgentFailureResultCodes
)
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
        self.set_status(results.http_status_code)
        self.write(dumps(results.to_dict_non_null(), indent=4))

    @agent_results_message
    def validate_token(self, token):
        validated = validate_token(token)
        results = ApiResults()
        results.fill_in_defaults()
        if validated:
            results.message = 'Token {0} validated successfully'
            results.generic_status_code = AgentResultCodes.TokenValidated
            results.vfense_status_code = AgentResultCodes.TokenValidated
        else:
            results.message = 'Token {0} is invalid'
            results.generic_status_code = AgentFailureResultCodes.InvalidToken
            results.vfense_status_code = AgentFailureResultCodes.InvalidToken

        return results
