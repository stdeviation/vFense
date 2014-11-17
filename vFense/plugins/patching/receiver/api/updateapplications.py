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

