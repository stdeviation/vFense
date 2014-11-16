import logging, logging.config
from vFense._constants import VFENSE_LOGGING_CONFIG
from vFense.db.client import db_create_close, r
from vFense.core.queue._db_model import (
    QueueCollections, AgentQueueKey, AgentQueueIndexes
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
def initialize_queue_indexes(collection, indexes, conn=None):
    if not AgentQueueIndexes.AgentId in indexes:
        (
            r
            .table(collection)
            .index_create(
                AgentQueueIndexes.AgentId
            )
            .run(conn)
        )

try:
    queue_collections = [
        (QueueCollections.Agent, AgentQueueKey.Id),
    ]
    current_collections = retrieve_collections()
    for collection in queue_collections:
        initialize_collections(collection, current_collections)
        name, _ = collection
        indexes = retrieve_indexes(name)
        initialize_queue_indexes(name, indexes)

except Exception as e:
    logger.exception(e)
