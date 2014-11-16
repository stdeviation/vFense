import logging, logging.config
from vFense._constants import VFENSE_LOGGING_CONFIG
from vFense.db.client import db_create_close, r
from vFense.core.group._db_model import (
    GroupCollections, GroupKeys, GroupIndexes
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
def initialize_group_indexes(collection, indexes, conn=None):
    if not GroupIndexes.Views in indexes:
        (
            r
            .table(collection)
            .index_create(
                GroupIndexes.Views, multi=True
            )
            .run(conn)
        )

    if not GroupIndexes.Users in indexes:
        (
            r
            .table(collection)
            .index_create(
                GroupIndexes.Users, multi=True
            )
            .run(conn)
        )

    if not GroupIndexes.GroupName in indexes:
        (
            r
            .table(collection)
            .index_create(GroupIndexes.GroupName)
            .run(conn)
        )


try:
    group_collections = [
        (GroupCollections.Groups, GroupKeys.GroupId),
    ]
    current_collections = retrieve_collections()
    for collection in group_collections:
        initialize_collections(collection, current_collections)
        name, _ = collection
        indexes = retrieve_indexes(name)
        initialize_group_indexes(name, indexes)

except Exception as e:
    logger.exception(e)
