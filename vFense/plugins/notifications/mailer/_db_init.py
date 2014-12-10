import logging, logging.config
from vFense._constants import VFENSE_LOGGING_CONFIG
from vFense.db.client import r
from vFense.db.manager import DbInit
from vFense.plugins.notifications.mailer._db_model import (
    NotificationPluginIndexes, NotificationPluginKeys,
    NotificationPluginCollections
)

logging.config.fileConfig(VFENSE_LOGGING_CONFIG)
logger = logging.getLogger('vfense_api')

collections = [
    (
        NotificationPluginCollections.NotificationPlugins,
        NotificationPluginKeys.Id
    ),
]

secondary_indexes = [
    (
        NotificationPluginCollections.NotificationPlugins,
        NotificationPluginIndexes.ViewName,
        (
            r
            .table(NotificationPluginCollections.NotificationPlugins)
            .index_create(
                NotificationPluginIndexes.ViewName
            )
        )
    )
]

try:
    db = DbInit()
    db.initialize(collections, secondary_indexes)

except Exception as e:
    logger.exception(e)
