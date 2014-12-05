import logging, logging.config
from vFense._constants import VFENSE_LOGGING_CONFIG
from vFense.db.client import r
from vFense.db.manager import DbInit
from vFense.core.agent._db_model import (
    AgentCollections, AgentKeys, AgentIndexes, HardwarePerAgentKeys,
    HardwarePerAgentIndexes
)

logging.config.fileConfig(VFENSE_LOGGING_CONFIG)
logger = logging.getLogger('vfense_api')

collections = [
    (AgentCollections.Agents, AgentKeys.AgentId),
    (AgentCollections.Hardware, HardwarePerAgentKeys.Id),
]

secondary_indexes = [
    (
        AgentCollections.Agents,
        AgentIndexes.Views,
        (
            r
            .table(AgentCollections.Agents)
            .index_create(
                AgentIndexes.Views, multi=True
            )
        )
    ),
    (
        AgentCollections.Agents,
        AgentIndexes.OsCode,
        (
            r
            .table(AgentCollections.Agents)
            .index_create(AgentIndexes.OsCode)
        )
    ),
    (
        AgentCollections.Hardware,
        HardwarePerAgentIndexes.AgentId,
        (
            r
            .table(AgentCollections.Hardware)
            .index_create(
                HardwarePerAgentIndexes.AgentId
            )
        )
    ),
    (
        AgentCollections.Hardware,
        HardwarePerAgentIndexes.Type,
        (
            r
            .table(AgentCollections.Hardware)
            .index_create(
                HardwarePerAgentIndexes.Type
            )
        )
    ),
    (
        AgentCollections.Hardware,
        HardwarePerAgentIndexes.AgentIdAndType,
        (
            r
            .table(AgentCollections.Hardware)
            .index_create(
                HardwarePerAgentIndexes.AgentIdAndType,
                lambda x:
                [
                    x[HardwarePerAgentKeys.AgentId],
                    x[HardwarePerAgentKeys.Type]
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
