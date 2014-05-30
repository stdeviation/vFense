import logging, logging.config
from vFense import VFENSE_LOGGING_CONFIG
from vFense.db.client import db_create_close, r
from vFense.plugins.patching._db_model import (
    DbCommonAppIndexes, DbCommonAppKeys, DbCommonAppPerAgentKeys,
    DbCommonAppPerAgentIndexes, AppCollections, FileCollections,
    FilesIndexes, FilesKey
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
def initialize_app_indexes(collection, indexes, conn=None):
    if not DbCommonAppIndexes.RvSeverity in indexes:
        (
            r
            .table(collection)
            .index_create(
                DbCommonAppIndexes.RvSeverity
            )
            .run(conn)
        )

    if not DbCommonAppIndexes.Name in indexes:
        (
            r
            .table(collection)
            .index_create(DbCommonAppIndexes.Name)
            .run(conn)
        )

    if not DbCommonAppIndexes.NameAndVersion in indexes:
        (
            r
            .table(collection)
            .index_create(
                DbCommonAppIndexes.NameAndVersion,
                lambda x:
                [
                    x[DbCommonAppKeys.Name],
                    x[DbCommonAppKeys.Version]
                ]
            )
            .run(conn)
        )

    if not DbCommonAppIndexes.Views in indexes:
        (
            r
            .table(collection)
            .index_create(
                DbCommonAppIndexes.Views, multi=True
            )
            .run(conn)
        )

    if not DbCommonAppIndexes.ViewAndRvSeverity in indexes:
        (
            r
            .table(collection)
            .index_create(
                DbCommonAppIndexes.ViewAndRvSeverity,
                lambda x: 
                [
                    x[DbCommonAppKeys.Views],
                    x[DbCommonAppKeys.RvSeverity]
                ],
                multi=True
            )
            .run(conn)
        )

    if not DbCommonAppIndexes.AppIdAndRvSeverity in indexes:
        (
            r
            .table(collection)
            .index_create(
                DbCommonAppIndexes.AppIdAndRvSeverity,
                lambda x:
                [
                    x[DbCommonAppKeys.AppId],
                    x[DbCommonAppKeys.RvSeverity]
                ]
            )
            .run(conn)
        )

@db_create_close
def initialize_file_indexes(collection, indexes, conn=None):
    if not FilesIndexes.FilesDownloadStatus in indexes:
        (
            r
            .table(collection)
            .index_create(
                FilesIndexes.FilesDownloadStatus
            )
            .run(conn)
        )

@db_create_close
def initialize_apps_per_agent_indexes(collection, indexes, conn=None):
    if not DbCommonAppPerAgentIndexes.Status in indexes:
        (
            r
            .table(collection)
            .index_create(
                DbCommonAppPerAgentIndexes.Status
            )
            .run(conn)
        )

    if not DbCommonAppPerAgentIndexes.AgentId in indexes:
        (
            r
            .table(collection)
            .index_create(
                DbCommonAppPerAgentIndexes.AgentId
            )
            .run(conn)
        )

    if not DbCommonAppPerAgentIndexes.AppId in indexes:
        (
            r
            .table(collection)
            .index_create(
                DbCommonAppPerAgentIndexes.AppId
            ).run(conn)
        )

    if not DbCommonAppPerAgentIndexes.ViewName in indexes:
        (
            r
            .table(collection)
            .index_create(
                DbCommonAppPerAgentIndexes.ViewName
            )
            .run(conn)
        )

    if not DbCommonAppPerAgentIndexes.AgentIdAndAppId in indexes:
        (
            r
            .table(collection)
            .index_create(
                DbCommonAppPerAgentIndexes.AgentIdAndAppId,
                lambda x:
                [
                    x[DbCommonAppPerAgentKeys.AgentId],
                    x[DbCommonAppPerAgentKeys.AppId]
                ]
            )
            .run(conn)
        )


    if not DbCommonAppPerAgentIndexes.AppIdAndView in indexes:
        (
            r
            .table(collection)
            .index_create(
                DbCommonAppPerAgentIndexes.AppIdAndView,
                lambda x:
                [
                    x[DbCommonAppPerAgentKeys.AppId],
                    x[DbCommonAppPerAgentKeys.ViewName]
                ]
            )
            .run(conn)
        )

    if not DbCommonAppPerAgentIndexes.AppIdAndStatus in indexes:
        (
            r
            .table(collection)
            .index_create(
                DbCommonAppPerAgentIndexes.AppIdAndStatus,
                lambda x:
                [
                    x[DbCommonAppPerAgentKeys.AppId],
                    x[DbCommonAppPerAgentKeys.Status]
                ]
            )
            .run(conn)
        )

    if not DbCommonAppPerAgentIndexes.StatusAndView in indexes:
        (
            r
            .table(collection)
            .index_create(
                DbCommonAppPerAgentIndexes.StatusAndView,
                lambda x:
                [
                    x[DbCommonAppPerAgentKeys.Status],
                    x[DbCommonAppPerAgentKeys.ViewName]
                ]
            )
            .run(conn)
        )

    if not DbCommonAppPerAgentIndexes.AppIdAndStatusAndView in indexes:
        (
            r
            .table(collection)
            .index_create(
                DbCommonAppPerAgentIndexes.AppIdAndStatusAndView,
                lambda x:
                [
                    x[DbCommonAppPerAgentKeys.AppId],
                    x[DbCommonAppPerAgentKeys.Status],
                    x[DbCommonAppPerAgentKeys.ViewName]
                ]
            )
            .run(conn)
        )

    if not DbCommonAppPerAgentIndexes.StatusAndAgentId in indexes:
        (
            r
            .table(collection)
            .index_create(
                DbCommonAppPerAgentIndexes.StatusAndAgentId,
                lambda x:
                [
                    x[DbCommonAppPerAgentKeys.Status],
                    x[DbCommonAppPerAgentKeys.AgentId]
                ]
            )
            .run(conn)
        )

try:
    app_collections = [
        (AppCollections.UniqueApplications, DbCommonAppKeys.AppId),
        (AppCollections.CustomApps, DbCommonAppKeys.AppId),
        (AppCollections.SupportedApps, DbCommonAppKeys.AppId),
        (AppCollections.vFenseApps, DbCommonAppKeys.AppId),
    ]
    apps_per_agent_collections = [
        (AppCollections.AppsPerAgent, DbCommonAppPerAgentKeys.Id),
        (AppCollections.CustomAppsPerAgent, DbCommonAppPerAgentKeys.Id),
        (AppCollections.SupportedAppsPerAgent, DbCommonAppPerAgentKeys.Id),
        (AppCollections.vFenseAppsPerAgent, DbCommonAppPerAgentKeys.Id),
    ]
    file_collections = [
        (FileCollections.Files, FilesKey.FileName)
    ]
    current_collections = retrieve_collections()
    for collection in app_collections:
        initialize_collections(collection, current_collections)
        name, _ = collection
        indexes = retrieve_indexes(name)
        initialize_app_indexes(name, indexes)
    for collection in apps_per_agent_collections:
        initialize_collections(collection, current_collections)
        name, _ = collection
        indexes = retrieve_indexes(name)
        initialize_apps_per_agent_indexes(name, indexes)
    for collection in file_collections:
        initialize_collections(collection, current_collections)
        name, _ = collection
        indexes = retrieve_indexes(name)
        initialize_file_indexes(name, indexes)


except Exception as e:
    logger.exception(e)
