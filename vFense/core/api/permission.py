import logging
import logging.config
from vFense._constants import VFENSE_LOGGING_CONFIG

from vFense.core.api.base import BaseHandler
from vFense.core.api._constants import ApiArguments
from vFense.core.status_codes import GenericCodes
from vFense.core.decorators import (
    authenticated_request, api_catch_it, results_message
)

from vFense.core.permissions._constants import Permissions
from vFense.core.permissions.decorators import check_permissions
from vFense.core.results import ApiResults

logging.config.fileConfig(VFENSE_LOGGING_CONFIG)
logger = logging.getLogger('vfense_api')


class RetrieveValidPermissionsHandler(BaseHandler):
    @api_catch_it
    @authenticated_request
    def get(self):
        output = self.get_argument(ApiArguments.OUTPUT, 'json')
        results = self.get_permissions()
        self.set_status(results.http_status_code)
        self.modified_output(results, output, 'uris')

    @results_message
    @check_permissions(Permissions.READ)
    def get_permissions(self):
        results = ApiResults()
        results.data = Permissions.get_valid_permissions()
        results.generic_status_code = GenericCodes.InformationRetrieved
        results.vfense_status_code = GenericCodes.InformationRetrieved
        results.count = len(results.data)
        return results
