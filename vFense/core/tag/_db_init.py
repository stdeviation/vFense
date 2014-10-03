import logging, logging.config
from vFense import VFENSE_LOGGING_CONFIG
from vFense.db.client import db_create_close, r
from vFense.core.tag._db_model import (
    TagCollections, TagKeys, TagsIndexes, TagsPerAgentKeys, TagsPerAgentIndexes
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
def initialize_tag_indexes(collection, indexes, conn=None):
    if not TagsIndexes.ViewName in indexes:
        (
            r
            .table(collection)
            .index_create(
                TagsIndexes.ViewName
            )
            .run(conn)
        )

    if not TagsIndexes.TagNameAndView in indexes:
        (
            r
            .table(collection)
            .index_create(
                TagsIndexes.TagNameAndView,
                lambda x:
                [
                    x[TagKeys.TagName],
                    x[TagKeys.ViewName]
                ]
            )
            .run(conn)
        )


@db_create_close
def initialize_tag_per_agent_indexes(collection, indexes, conn=None):
    if not TagsPerAgentIndexes.AgentId in indexes:
        (
            r
            .table(collection)
            .index_create(
                TagsPerAgentIndexes.AgentId
            )
            .run(conn)
        )


    if not TagsPerAgentIndexes.TagId in indexes:
        (
            r
            .table(collection)
            .index_create(
                TagsPerAgentIndexes.TagId
            )
            .run(conn)
        )

    if not TagsPerAgentIndexes.ViewName in indexes:
        (
            r
            .table(collection)
            .index_create(
                TagsPerAgentIndexes.ViewName
            )
            .run(conn)
        )

    if not TagsPerAgentIndexes.AgentIdAndTagId in indexes:
        (
            r
            .table(collection)
            .index_create(
                TagsPerAgentIndexes.AgentIdAndTagId,
                lambda x:
                [
                    x[TagsPerAgentKeys.AgentId],
                    x[TagsPerAgentKeys.TagId]
                ]
            )
            .run(conn)
        )


try:
    tag_collections = [
        (TagCollections.Tags, TagKeys.TagId),
    ]
    tag_per_agent_collections = [
        (TagCollections.TagsPerAgent, TagsPerAgentKeys.Id),
    ]
    current_collections = retrieve_collections()
    for collection in tag_collections:
        initialize_collections(collection, current_collections)
        name, _ = collection
        indexes = retrieve_indexes(name)
        initialize_tag_indexes(name, indexes)
    for collection in tag_per_agent_collections:
        initialize_collections(collection, current_collections)
        name, _ = collection
        indexes = retrieve_indexes(name)

except Exception as e:
    logger.exception(e)
