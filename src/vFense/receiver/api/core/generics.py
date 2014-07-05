import logging

from json import dumps

from vFense import VFENSE_LOGGING_CONFIG
from vFense.core.api.base import BaseHandler
from vFense.core.decorators import (
    convert_json_to_arguments, results_message
)
from vFense.result._constants import ApiResultKeys
from vFense.result.error_messages import GenericResults
from vFense.core.operations.decorators import log_operation
from vFense.core.operations._admin_constants import AdminActions
from vFense.core.operations._constants import vFenseObjects
from vFense.receiver.api.decorators import authenticate_token


logging.config.fileConfig(VFENSE_LOGGING_CONFIG)
logger = logging.getLogger('rvlistener')

class ValidateToken(BaseHandler):
    @authenticate_token
    def get(self):
        pass

