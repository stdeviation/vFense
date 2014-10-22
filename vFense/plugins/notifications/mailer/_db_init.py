import logging, logging.config
from vFense import VFENSE_LOGGING_CONFIG
from vFense.db.client import db_create_close, r
from vFense.plugins.notifications._db_model import NotificationCollections
from vFense.plugins.notifications.mailer._db_model import (
    NotificationPluginIndexes, NotificationPluginKeys
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
def initialize_notification_plugin_indexes(collection, indexes, conn=None):
    if not NotificationPluginIndexes.ViewName in indexes:
        (
            r
            .table(collection)
            .index_create(
                NotificationPluginIndexes.ViewName
            )
            .run(conn)
        )

try:
    notification_collections = [
        (
            NotificationCollections.NotificationPlugins,
            NotificationPluginKeys.Id
        ),
    ]
    current_collections = retrieve_collections()
    for collection in notification_collections:
        initialize_collections(collection, current_collections)
        name, _ = collection
        indexes = retrieve_indexes(name)
        initialize_notification_plugin_indexes(name, indexes)


except Exception as e:
    logger.exception(e)
