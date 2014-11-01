import logging, logging.config
from vFense._constants import VFENSE_LOGGING_CONFIG
from vFense.db.client import db_create_close, r
from vFense.core.agent._db_model import (
    AgentCollections, AgentKeys, AgentIndexes, HardwarePerAgentKeys,
    HardwarePerAgentIndexes
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
def initialize_agent_indexes(collection, indexes, conn=None):
    if not AgentIndexes.Views in indexes:
        (
            r
            .table(collection)
            .index_create(
                AgentIndexes.Views, multi=True
            )
            .run(conn)
        )

    if not AgentIndexes.OsCode in indexes:
        (
            r
            .table(collection)
            .index_create(AgentIndexes.OsCode)
            .run(conn)
        )


@db_create_close
def initialize_hardware_indexes(collection, indexes, conn=None):
    if not HardwarePerAgentIndexes.AgentId in indexes:
        (
            r
            .table(collection)
            .index_create(
                HardwarePerAgentIndexes.AgentId
            )
            .run(conn)
        )

    if not HardwarePerAgentIndexes.Type in indexes:
        (
            r
            .table(collection)
            .index_create(
                HardwarePerAgentIndexes.Type
            )
            .run(conn)
        )

    if not HardwarePerAgentIndexes.AgentIdAndType in indexes:
        (
            r
            .table(collection)
            .index_create(
                HardwarePerAgentIndexes.AgentIdAndType,
                lambda x:
                [
                    x[HardwarePerAgentKeys.AgentId],
                    x[HardwarePerAgentKeys.Type]
                ]
            )
            .run(conn)
        )


try:
    agent_collections = [
        (AgentCollections.Agents, AgentKeys.AgentId),
    ]
    hardware_collections = [
        (AgentCollections.Hardware, HardwarePerAgentKeys.Id),
    ]
    current_collections = retrieve_collections()
    for collection in agent_collections:
        initialize_collections(collection, current_collections)
        name, _ = collection
        indexes = retrieve_indexes(name)
        initialize_agent_indexes(name, indexes)
    for collection in hardware_collections:
        initialize_collections(collection, current_collections)
        name, _ = collection
        indexes = retrieve_indexes(name)
        initialize_hardware_indexes(name, indexes)


except Exception as e:
    logger.exception(e)
