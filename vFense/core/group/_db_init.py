import logging, logging.config
from vFense._constants import VFENSE_LOGGING_CONFIG
from vFense.db.client import r
from vFense.db.manager import DbInit
from vFense.core.group._db_model import (
    GroupCollections, GroupKeys, GroupIndexes
)

logging.config.fileConfig(VFENSE_LOGGING_CONFIG)
logger = logging.getLogger('vfense_api')

collections = [
    (GroupCollections.Groups, GroupKeys.GroupId),
]

secondary_indexes = [
    (
        GroupCollections.Groups,
        GroupIndexes.Views,
        (
            r
            .table(GroupCollections.Groups)
            .index_create(
                GroupIndexes.Views, multi=True
            )
        )
    ),
    (
        GroupCollections.Groups,
        GroupIndexes.Users,
        (
            r
            .table(GroupCollections.Groups)
            .index_create(
                GroupIndexes.Users, multi=True
            )
        )
    ),
    (
        GroupCollections.Groups,
        GroupIndexes.GroupName,
        (
            r
            .table(GroupCollections.Groups)
            .index_create(GroupIndexes.GroupName)
        )
    )
]

try:
    db = DbInit()
    db.initialize(collections, secondary_indexes)

except Exception as e:
    logger.exception(e)
