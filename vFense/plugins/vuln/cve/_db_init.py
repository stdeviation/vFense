import logging, logging.config
from vFense._constants import VFENSE_LOGGING_CONFIG
from vFense.db.client import r
from vFense.db.manager import DbInit
from vFense.plugins.vuln.cve._db_model import (
    CVECollections, CveKeys, CveIndexes
)

logging.config.fileConfig(VFENSE_LOGGING_CONFIG)
logger = logging.getLogger('vfense_api')

collections = [
    (
        CVECollections.CVE, CveKeys.CveId
    ),
]

secondary_indexes = [
    (
        CVECollections.CVE,
        CveIndexes.Categories,
        (
            r
            .table(CVECollections.CVE)
            .index_create(CveIndexes.Categories, multi=True)
        )
    )
]

try:
    db = DbInit()
    db.initialize(collections, secondary_indexes)

except Exception as e:
    logger.exception(e)
