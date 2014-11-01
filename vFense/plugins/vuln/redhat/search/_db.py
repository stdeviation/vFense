import logging
import logging.config
from vFense._constants import VFENSE_LOGGING_CONFIG

from vFense.plugins.vuln.search._db_vuln_base import FetchVulnBase
from vFense.plugins.vuln.redhat._db_model import (
    RedHatVulnerabilityCollections
)

logging.config.fileConfig(VFENSE_LOGGING_CONFIG)
logger = logging.getLogger('cve')

class FetchRedhatVulns(FetchVulnBase):
    def __init__(self, **kwargs):
        self.collection = RedHatVulnerabilityCollections.Vulnerabilities
        super(FetchRedhatVulns, self).__init__(self.collection, **kwargs)
