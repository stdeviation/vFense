import logging, logging.config
from vFense._constants import VFENSE_LOGGING_CONFIG
from vFense.db.client import r
from vFense.db.manager import DbInit
from vFense.plugins.vuln.windows._db_model import (
    WindowsVulnerabilityCollections, WindowsVulnerabilityKeys,
    WindowsVulnerabilityIndexes
)
from vFense.plugins.vuln.windows._constants import WindowsVulnSubKeys

logging.config.fileConfig(VFENSE_LOGGING_CONFIG)
logger = logging.getLogger('vfense_api')


collections = [
    (
        WindowsVulnerabilityCollections.Vulnerabilities,
        WindowsVulnerabilityKeys.VulnerabilityId
    ),
]
secondary_indexes = [
    (
        WindowsVulnerabilityCollections.Vulnerabilities,
        WindowsVulnerabilityIndexes.CveIds,
        (
            r
            .table(WindowsVulnerabilityCollections.Vulnerabilities)
            .index_create(
                WindowsVulnerabilityIndexes.CveIds,
                multi=True
            )
        )
    ),
    (
        WindowsVulnerabilityCollections.Vulnerabilities,
        WindowsVulnerabilityIndexes.ComponentKb,
        (
            r
            .table(WindowsVulnerabilityCollections.Vulnerabilities)
            .index_create(
                WindowsVulnerabilityIndexes.ComponentKb,
                lambda x:
                x[WindowsVulnerabilityKeys.Apps].map(
                    lambda y: y[WindowsVulnSubKeys.KB]
                ), multi=True
            )
        )
    )
]

try:
    db = DbInit()
    db.initialize(collections, secondary_indexes)

except Exception as e:
    logger.exception(e)
