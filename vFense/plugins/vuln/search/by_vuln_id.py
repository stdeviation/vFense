import re
import logging
import logging.config
from vFense._constants import VFENSE_LOGGING_CONFIG

from vFense.search.base import RetrieveBase
from vFense.plugins.vuln.cve._db_model import *
from vFense.plugins.vuln.cve._constants import *
from vFense.plugins.vuln.ubuntu.search.search import RetrieveUbuntuVulns
import vFense.plugins.vuln.windows.ms as ms

logging.config.fileConfig(VFENSE_LOGGING_CONFIG)
logger = logging.getLogger('cve')

class RetrieveByVulnerabilityId(RetrieveBase):
    def __init__(self, vuln_id=None, **kwargs):
        super(RetrieveByVulnerabilityId, self).__init__(**kwargs)
        self.vuln_id = vuln_id
        self.__os_director()

    def __os_director(self):
        if re.search('^MS', self.vuln_id, re.IGNORECASE):
            self.get_vuln = ms.get_vuln_data_by_vuln_id

        elif re.search('^USN-', self.vuln_id, re.IGNORECASE):
            self.get_vuln = RetrieveUbuntuVulns()

    def get_vuln(self):
        results = self.get_vuln.by_id(self.vuln_id)

        return results
