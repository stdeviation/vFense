from vFense.core.api.base import BaseHandler
from vFense.core.api._constants import ApiArguments
from vFense.core.decorators import (
    authenticated_request, results_message, api_catch_it
)
from vFense.core.permissions._constants import Permissions
from vFense.core.permissions.decorators import check_permissions
from vFense.plugins.vuln.cve.search.search import RetrieveCVEs

class CveIdHandler(BaseHandler):
    @api_catch_it
    @authenticated_request
    def get(self, cve_id):
        output = self.get_argument(ApiArguments.OUTPUT, 'json')
        results = self.get_cve_id(cve_id)
        self.set_status(results.http_status_code)
        self.modified_output(results, output, 'cve')

    @results_message
    @check_permissions(Permissions.READ)
    def get_cve_id(self, cve_id):
        vuln = RetrieveCVEs()
        results = vuln.by_id(cve_id)
        if len(results.data) > 0:
            results.data = results.data[0]
        return results
