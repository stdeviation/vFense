import logging, logging.config
from vFense._constants import VFENSE_LOGGING_CONFIG
from vFense.db.client import r
from vFense.db.manager import DbInit
from vFense.core.user._db_model import (
    UserCollections, UserKeys, UserIndexes
)

logging.config.fileConfig(VFENSE_LOGGING_CONFIG)
logger = logging.getLogger('vfense_api')

collections = [
    (UserCollections.Users, UserKeys.UserName),
]

secondary_indexes = [
    (
        UserCollections.Users,
        UserIndexes.Views,
        (
            r
            .table(UserCollections.Users)
            .index_create(UserIndexes.Views, multi=True)
        )
    )
]

try:
    db = DbInit()
    db.initialize(collections, secondary_indexes)

except Exception as e:
    print e
    logger.exception(e)
