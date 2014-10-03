import logging, logging.config
from vFense import VFENSE_LOGGING_CONFIG
from vFense.db.client import db_create_close, r
from vFense.plugins.notifications._db_model import (
    NotificationIndexes, NotificationKeys, NotificationCollections,
    NotificationPluginIndexes, NotificationHistoryIndexes,
    NotificationPluginKeys, NotificationHistoryKeys
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
def initialize_notification_indexes(collection, indexes, conn=None):
    if not NotificationIndexes.ViewName in indexes:
        (
            r
            .table(collection)
            .index_create(
                NotificationIndexes.ViewName
            )
            .run(conn)
        )

    if not NotificationIndexes.RuleNameAndView in indexes:
        (
            r
            .table(collection)
            .index_create(
                NotificationIndexes.RuleNameAndView,
                lambda x:
                [
                    x[NotificationKeys.RuleName],
                    x[NotificationKeys.ViewName]
                ]
            )
            .run(conn)
        )

    if not NotificationIndexes.NotificationTypeAndView in indexes:
        (
            r
            .table(collection)
            .index_create(
                NotificationIndexes.NotificationTypeAndView,
                lambda x:
                [
                    x[NotificationKeys.NotificationType],
                    x[NotificationKeys.ViewName]
                ]
            )
            .run(conn)
        )

    if not NotificationIndexes.ThresholdAndView in indexes:
        (
            r
            .table(collection)
            .index_create(
                NotificationIndexes.ThresholdAndView,
                lambda x:
                [
                    x[NotificationKeys.Threshold],
                    x[NotificationKeys.ViewName]
                ]
            )
            .run(conn)
        )

    if not NotificationIndexes.ThresholdAndFileSystemAndView in indexes:
        (
            r
            .table(collection)
            .index_create(
                NotificationIndexes.ThresholdAndFileSystemAndView,
                lambda x:
                [
                    x[NotificationKeys.Threshold],
                    x[NotificationKeys.FileSystem],
                    x[NotificationKeys.ViewName]
                ]
            )
            .run(conn)
        )

@db_create_close
def initialize_notification_history_indexes(collection, indexes, conn=None):
    if not NotificationHistoryIndexes.NotificationId in indexes:
        (
            r
            .table(collection)
            .index_create(
                NotificationHistoryIndexes.NotificationId
            )
            .run(conn)
        )


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
            NotificationCollections.Notifications,
            NotificationKeys.NotificationId
        ),
        (
            NotificationCollections.NotificationsHistory,
            NotificationHistoryKeys.Id
        ),
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
        initialize_notification_indexes(name, indexes)


except Exception as e:
    logger.exception(e)
