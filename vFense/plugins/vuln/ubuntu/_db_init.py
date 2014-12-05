import logging, logging.config
from vFense._constants import VFENSE_LOGGING_CONFIG
from vFense.db.client import r
from vFense.db.manager import DbInit
from vFense.plugins.vuln.ubuntu._db_model import (
    UbuntuVulnerabilityCollections, UbuntuVulnerabilityKeys,
    UbuntuVulnerabilityIndexes
)
from vFense.plugins.vuln.ubuntu._constants import UbuntuVulnSubKeys

logging.config.fileConfig(VFENSE_LOGGING_CONFIG)
logger = logging.getLogger('vfense_api')

collections = [
    (
        UbuntuVulnerabilityCollections.Vulnerabilities,
        UbuntuVulnerabilityKeys.VulnerabilityId
    ),
]
secondary_indexes = [
    (
        UbuntuVulnerabilityCollections.Vulnerabilities,
        UbuntuVulnerabilityIndexes.CveIds,
        (
            r
            .table(UbuntuVulnerabilityCollections.Vulnerabilities)
            .index_create(
                UbuntuVulnerabilityIndexes.CveIds,
                multi=True
            )
        )
    ),
    (
        UbuntuVulnerabilityCollections.Vulnerabilities,
        UbuntuVulnerabilityIndexes.NameAndVersion,
        (
            r
            .table(UbuntuVulnerabilityCollections.Vulnerabilities)
            .index_create(
                UbuntuVulnerabilityIndexes.NameAndVersion,
                lambda x:
                x[UbuntuVulnerabilityKeys.Apps].map(
                    lambda y:
                    [
                        y[UbuntuVulnSubKeys.NAME],
                        y[UbuntuVulnSubKeys.VERSION]
                    ]
                ), multi=True
            )
        )
    ),
    (
        UbuntuVulnerabilityCollections.Vulnerabilities,
        UbuntuVulnerabilityIndexes.AppId,
        (
            r
            .table(UbuntuVulnerabilityCollections.Vulnerabilities)
            .index_create(
                UbuntuVulnerabilityIndexes.AppId,
                lambda x:
                x[UbuntuVulnerabilityKeys.Apps].map(
                    lambda y: y[UbuntuVulnSubKeys.APP_ID]
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
