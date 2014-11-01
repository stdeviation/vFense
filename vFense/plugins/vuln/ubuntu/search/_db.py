import logging
import logging.config
from vFense._constants import VFENSE_LOGGING_CONFIG

from vFense.plugins.vuln.search._db_vuln_base import FetchVulnBase
from vFense.plugins.vuln.ubuntu._db_model import (
    UbuntuVulnerabilityCollections
)

logging.config.fileConfig(VFENSE_LOGGING_CONFIG)
logger = logging.getLogger('cve')

class FetchUbuntuVulns(FetchVulnBase):
    def __init__(self, **kwargs):
        self.collection = UbuntuVulnerabilityCollections.Vulnerabilities
        super(FetchUbuntuVulns, self).__init__(self.collection, **kwargs)
