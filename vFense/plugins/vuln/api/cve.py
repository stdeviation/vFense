import simplejson as json

from vFense.core.api.base import BaseHandler
import logging
import logging.config
from vFense import VFENSE_LOGGING_CONFIG

from vFense.plugins.vuln.cve.search.search import RetrieveCVEs

from vFense.core.decorators import authenticated_request, results_message
from vFense.core.results import ApiResultKeys

logging.config.fileConfig(VFENSE_LOGGING_CONFIG)
logger = logging.getLogger('rvapi')


class CveIdHandler(BaseHandler):
    @authenticated_request
    def get(self, cve_id):
        results = self.get_cve_id(cve_id)
        self.set_status(results['http_status'])
        self.set_header('Content-Type', 'application/json')
        self.write(json.dumps(results, indent=4))

    @results_message
    def get_cve_id(self, cve_id):
        vuln = RetrieveCVEs()
        results = vuln.by_id(cve_id)
        if len(results[ApiResultKeys.DATA]) > 0:
            results[ApiResultKeys.DATA] = results[ApiResultKeys.DATA][0]
        return results
