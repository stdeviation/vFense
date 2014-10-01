import logging, logging.config
from vFense import VFENSE_LOGGING_CONFIG
from vFense.db.client import db_create_close, r
from vFense.core.stats._db_model import (
    StatsCollections, StatsPerAgentIndexes, AgentStatKeys
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
def initialize_stat_indexes(collection, indexes, conn=None):
    if not StatsPerAgentIndexes.AgentId in indexes:
        (
            r
            .table(collection)
            .index_create(
                StatsPerAgentIndexes.AgentId
            )
            .run(conn)
        )

    if not StatsPerAgentIndexes.StatType in indexes:
        (
            r
            .table(collection)
            .index_create(StatsPerAgentIndexes.StatType)
            .run(conn)
        )

    if not StatsPerAgentIndexes.AgentIdAndStatType in indexes:
        (
            r
            .table(collection)
            .index_create(
                StatsPerAgentIndexes.AgentIdAndStatType,
                lambda x:
                [
                    x[StatsPerAgentIndexes.AgentId],
                    x[StatsPerAgentIndexes.StatType]
                ]
            )
            .run(conn)
        )


try:
    stat_collections = [
        (StatsCollections.AgentStats, AgentStatKeys.Id),
    ]
    current_collections = retrieve_collections()

    for collection in stat_collections:
        initialize_collections(collection, current_collections)
        name, _ = collection
        indexes = retrieve_indexes(name)
        initialize_stat_indexes(name, indexes)


except Exception as e:
    logger.exception(e)
