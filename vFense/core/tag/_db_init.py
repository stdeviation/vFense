import logging, logging.config
from vFense._constants import VFENSE_LOGGING_CONFIG
from vFense.db.client import r
from vFense.db.manager import DbInit
from vFense.core.tag._db_model import (
    TagCollections, TagKeys, TagsIndexes, TagsPerAgentKeys, TagsPerAgentIndexes
)

logging.config.fileConfig(VFENSE_LOGGING_CONFIG)
logger = logging.getLogger('vfense_api')

collections = [
    (TagCollections.Tags, TagKeys.TagId),
    (TagCollections.TagsPerAgent, TagsPerAgentKeys.Id),
]

secondary_indexes = [
    (
        TagCollections.Tags,
        TagsIndexes.ViewName,
        (
            r
            .table(TagCollections.Tags)
            .index_create(TagsIndexes.ViewName)
        )
    ),
    (
        TagCollections.Tags,
        TagsIndexes.TagNameAndView,
        (
            r
            .table(TagCollections.Tags)
            .index_create(
                TagsIndexes.TagNameAndView,
                lambda x:
                [
                    x[TagKeys.TagName],
                    x[TagKeys.ViewName]
                ]
            )
        )
    ),
    (
        TagCollections.TagsPerAgent,
        TagsPerAgentIndexes.AgentId,
        (
            r
            .table(TagCollections.TagsPerAgent)
            .index_create(TagsPerAgentIndexes.AgentId)
        )
    ),
    (
        TagCollections.TagsPerAgent,
        TagsPerAgentIndexes.TagId,
        (
            r
            .table(TagCollections.TagsPerAgent)
            .index_create(TagsPerAgentIndexes.TagId)
        )
    ),
    (
        TagCollections.TagsPerAgent,
        TagsPerAgentIndexes.ViewName,
        (
            r
            .table(TagCollections.TagsPerAgent)
            .index_create(TagsPerAgentIndexes.ViewName)
        )
    ),
    (
        TagCollections.TagsPerAgent,
        TagsPerAgentIndexes.AgentIdAndTagId,
        (
            r
            .table(TagCollections.TagsPerAgent)
            .index_create(
                TagsPerAgentIndexes.AgentIdAndTagId,
                lambda x:
                [
                    x[TagsPerAgentKeys.AgentId],
                    x[TagsPerAgentKeys.TagId]
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
