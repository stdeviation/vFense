import logging, logging.config
from vFense._constants import VFENSE_LOGGING_CONFIG
from vFense.db.client import db_create_close, r
from vFense.core.user._db_model import (
    UserCollections, UserKeys, UserIndexes
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
def initialize_user_indexes(collection, indexes, conn=None):
    if not UserIndexes.Views in indexes:
        (
            r
            .table(collection)
            .index_create(
                UserIndexes.Views, multi=True
            )
            .run(conn)
        )

try:
    user_collections = [
        (UserCollections.Users, UserKeys.UserName),
    ]
    current_collections = retrieve_collections()
    for collection in user_collections:
        initialize_collections(collection, current_collections)
        name, _ = collection
        indexes = retrieve_indexes(name)
        initialize_user_indexes(name, indexes)

except Exception as e:
    logger.exception(e)
