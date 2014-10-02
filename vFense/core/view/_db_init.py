import logging, logging.config
from vFense import VFENSE_LOGGING_CONFIG
from vFense.db.client import db_create_close, r
from vFense.core.view._db_model import (
    ViewCollections, ViewKeys, ViewIndexes
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
def initialize_view_indexes(collection, indexes, conn=None):
    if not ViewIndexes.Users in indexes:
        (
            r
            .table(collection)
            .index_create(
                ViewIndexes.Users, multi=True
            )
            .run(conn)
        )

    if not ViewIndexes.Token in indexes:
        (
            r
            .table(collection)
            .index_create(ViewIndexes.Token)
            .run(conn)
        )

    if not ViewIndexes.PreviousTokens in indexes:
        (
            r
            .table(collection)
            .index_create(
                ViewIndexes.PreviousTokens, multi=True
            )
            .run(conn)
        )

try:
    view_collections = [
        (ViewCollections.Views, ViewKeys.ViewId),
    ]
    current_collections = retrieve_collections()
    for collection in view_collections:
        initialize_collections(collection, current_collections)
        name, _ = collection
        indexes = retrieve_indexes(name)
        initialize_view_indexes(name, indexes)

except Exception as e:
    logger.exception(e)
