import logging, logging.config
from vFense import VFENSE_LOGGING_CONFIG
from vFense.db.client import db_create_close, r
from vFense.plugins.vuln.windows._db_model import (
    WindowsVulnerabilityCollections, WindowsVulnerabilityKeys,
    WindowsVulnerabilityIndexes
)
from vFense.plugins.vuln.windows._constants import WindowsVulnSubKeys
from vFense.core._db import (
    retrieve_collections, create_collection, retrieve_indexes
)

logging.config.fileConfig(VFENSE_LOGGING_CONFIG)
logger = logging.getLogger('rvapi')

def initialize_collections(collection, current_collections):
    name, key = collection
    if name not in current_collections:
        create_collection(name, key)

@db_create_close
def initialize_windows_indexes(collection, indexes, conn=None):
    if not WindowsVulnerabilityIndexes.CveIds in indexes:
        (
            r
            .table(collection)
            .index_create(
                WindowsVulnerabilityIndexes.CveIds,
                multi=True
            )
            .run(conn)
        )

    if not WindowsVulnerabilityIndexes.ComponentKb in indexes:
        (
            r
            .table(collection)
            .index_create(
                WindowsVulnerabilityIndexes.ComponentKb,
                lambda x:
                x[WindowsVulnerabilityKeys.Apps].map(
                    lambda y: y[WindowsVulnSubKeys.KB]
                ), multi=True
            )
            .run(conn)
        )

try:
    windows_collections = [
        (
            WindowsVulnerabilityCollections.Vulnerabilities,
            WindowsVulnerabilityKeys.VulnerabilityId
        ),
    ]
    current_collections = retrieve_collections()
    for collection in windows_collections:
        initialize_collections(collection, current_collections)
        name, _ = collection
        indexes = retrieve_indexes(name)
        initialize_windows_indexes(name, indexes)

except Exception as e:
    logger.exception(e)
