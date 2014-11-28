import logging, logging.config
from vFense._constants import VFENSE_LOGGING_CONFIG
from vFense.db.client import db_create_close, r
from vFense.plugins.relay_server._db_model import (
    RelayServerCollections, RelayServerKeys, RelayServerIndexes
)
from vFense.core._db import (
    retrieve_collections, create_collection, retrieve_indexes
)

logging.config.fileConfig(VFENSE_LOGGING_CONFIG)
logger = logging.getLogger('vfense_api')

def initialize_collections(collection, current_collections):
    name, key = collection
    if name not in current_collections:
        create_collection(name, key)

@db_create_close
def initialize_app_indexes(collection, indexes, conn=None):
    if not RelayServerIndexes.Views in indexes:
        (
            r
            .table(collection)
            .index_create(RelayServerIndexes.Views)
            .run(conn)
        )

try:
    relay_collections = [
        (RelayServerCollections.RelayServers, RelayServerKeys.RelayName)
    ]

    current_collections = retrieve_collections()
    for collection in relay_collections:
        initialize_collections(collection, current_collections)
        name, _ = collection
        indexes = retrieve_indexes(name)
        initialize_app_indexes(name, indexes)

except Exception as e:
    logger.exception(e)
