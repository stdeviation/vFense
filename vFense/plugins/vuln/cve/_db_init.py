import logging, logging.config
from vFense import VFENSE_LOGGING_CONFIG
from vFense.db.client import db_create_close, r
from vFense.plugins.vuln.cve._db_model import (
    CVECollections, CveKeys, CveIndexes
)
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
def initialize_cve_indexes(collection, indexes, conn=None):
    if not CveIndexes.Categories in indexes:
        (
            r
            .table(collection)
            .index_create(
                CveIndexes.Categories,
                multi=True
            )
            .run(conn)
        )

try:
    cve_collections = [
        (
            CVECollections.CVE, CveKeys.CveId
        ),
    ]
    current_collections = retrieve_collections()
    for collection in cve_collections:
        initialize_collections(collection, current_collections)
        name, _ = collection
        indexes = retrieve_indexes(name)
        initialize_cve_indexes(name, indexes)

except Exception as e:
    logger.exception(e)
