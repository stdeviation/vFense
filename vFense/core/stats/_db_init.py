import logging, logging.config
from vFense._constants import VFENSE_LOGGING_CONFIG
from vFense.db.client import r
from vFense.db.manager import DbInit
from vFense.core.stats._db_model import (
    StatsCollections, StatsPerAgentIndexes, AgentStatKeys
)

logging.config.fileConfig(VFENSE_LOGGING_CONFIG)
logger = logging.getLogger('vfense_api')

collections = [
    (StatsCollections.AgentStats, AgentStatKeys.Id)
]

secondary_indexes = [
    (
        StatsCollections.AgentStats,
        StatsPerAgentIndexes.AgentId,
        (
            r
            .table(StatsCollections.AgentStats)
            .index_create(StatsPerAgentIndexes.AgentId)
        )
    ),
    (
        StatsCollections.AgentStats,
        StatsPerAgentIndexes.StatType,
        (
            r
            .table(StatsCollections.AgentStats)
            .index_create(StatsPerAgentIndexes.StatType)
        )
    ),
    (
        StatsCollections.AgentStats,
        StatsPerAgentIndexes.AgentIdAndStatType,
        (
            r
            .table(StatsCollections.AgentStats)
            .index_create(
                StatsPerAgentIndexes.AgentIdAndStatType,
                lambda x:
                [
                    x[StatsPerAgentIndexes.AgentId],
                    x[StatsPerAgentIndexes.StatType]
                ]
            )
        )
    )
]

try:
    db = DbInit()
    db.initialize(collections, secondary_indexes)

except Exception as e:
    logger.exception(e)
