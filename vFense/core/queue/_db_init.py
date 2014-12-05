import logging, logging.config
from vFense._constants import VFENSE_LOGGING_CONFIG
from vFense.db.client import r
from vFense.db.manager import DbInit
from vFense.core.queue._db_model import (
    QueueCollections, AgentQueueKey, AgentQueueIndexes
)

logging.config.fileConfig(VFENSE_LOGGING_CONFIG)
logger = logging.getLogger('vfense_api')

collections = [
    (QueueCollections.Agent, AgentQueueKey.Id),
]

secondary_indexes = [
    (
        QueueCollections.Agent,
        AgentQueueIndexes.AgentId,
        (
            r
            .table(QueueCollections.Agent)
            .index_create(AgentQueueIndexes.AgentId)
        )
    )
]

try:
    db = DbInit()
    db.initialize(collections, secondary_indexes)

except Exception as e:
    logger.exception(e)
