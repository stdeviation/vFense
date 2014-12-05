import logging, logging.config
from vFense._constants import VFENSE_LOGGING_CONFIG
from vFense.db.client import r
from vFense.db.manager import DbInit
from vFense.plugins.vuln.redhat._db_model import (
    RedHatVulnerabilityCollections, RedhatVulnerabilityKeys,
    RedhatVulnerabilityIndexes
)
from vFense.plugins.vuln.redhat._constants import RedhatVulnSubKeys

logging.config.fileConfig(VFENSE_LOGGING_CONFIG)
logger = logging.getLogger('vfense_api')

collections = [
    (
        RedHatVulnerabilityCollections.Vulnerabilities,
        RedhatVulnerabilityKeys.VulnerabilityId
    ),
]

secondary_indexes = [
    (
        RedHatVulnerabilityCollections.Vulnerabilities,
        RedhatVulnerabilityIndexes.CveIds,
        (
            r
            .table(RedHatVulnerabilityCollections.Vulnerabilities)
            .index_create(
                RedhatVulnerabilityIndexes.CveIds,
                multi=True
            )
        )
    ),
    (
        RedHatVulnerabilityCollections.Vulnerabilities,
        RedhatVulnerabilityIndexes.NameAndVersion,
        (
            r
            .table(RedHatVulnerabilityCollections.Vulnerabilities)
            .index_create(
                RedhatVulnerabilityIndexes.NameAndVersion,
                lambda x:
                x[RedhatVulnerabilityKeys.Apps].map(
                    lambda y:
                    [
                        y[RedhatVulnSubKeys.NAME],
                        y[RedhatVulnSubKeys.VERSION]
                    ]
                ), multi=True
            )
        )
    ),
    (
        RedHatVulnerabilityCollections.Vulnerabilities,
        RedhatVulnerabilityIndexes.AppId,
        (
            r
            .table(RedHatVulnerabilityCollections.Vulnerabilities)
            .index_create(
                RedhatVulnerabilityIndexes.AppId,
                lambda x:
                x[RedhatVulnerabilityKeys.Apps].map(
                    lambda y: y[RedhatVulnSubKeys.APP_ID]
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
