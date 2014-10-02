import logging, logging.config
from vFense import VFENSE_LOGGING_CONFIG
from vFense.db.client import db_create_close, r
from vFense.core.operations._db_model import (
    OperationCollections, AdminOperationKey, AdminOperationIndexes,
    AgentOperationKey, AgentOperationIndexes, OperationPerAgentKey,
    OperationPerAgentIndexes, OperationPerAppKey, OperationPerAppIndexes
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
def initialize_admin_operation_indexes(collection, indexes, conn=None):
    if not AdminOperationIndexes.CreatedBy in indexes:
        (
            r
            .table(collection)
            .index_create(
                AdminOperationIndexes.CreatedBy
            )
            .run(conn)
        )

    if not AdminOperationIndexes.GenericStatusCode in indexes:
        (
            r
            .table(collection)
            .index_create(
                AdminOperationIndexes.GenericStatusCode
            )
            .run(conn)
        )

    if not AdminOperationIndexes.VfenseStatusCode in indexes:
        (
            r
            .table(collection)
            .index_create(
                AdminOperationIndexes.VfenseStatusCode
            )
            .run(conn)
        )

    if not AdminOperationIndexes.Action in indexes:
        (
            r
            .table(collection)
            .index_create(
                AdminOperationIndexes.Action
            )
            .run(conn)
        )

    if not AdminOperationIndexes.ActionPerformedOn in indexes:
        (
            r
            .table(collection)
            .index_create(
                AdminOperationIndexes.ActionPerformedOn
            )
            .run(conn)
        )


@db_create_close
def initialize_agent_operation_indexes(collection, indexes, conn=None):

    if not AgentOperationIndexes.TagId in indexes:
        (
            r
            .table(collection)
            .index_create(
                AgentOperationIndexes.TagId
            )
            .run(conn)
        )

    if not AgentOperationIndexes.AgentIds in indexes:
        (
            r
            .table(collection)
            .index_create(
                AgentOperationIndexes.AgentIds,
                multi=True
            )
            .run(conn)
        )

    if not AgentOperationIndexes.ViewName in indexes:
        (
            r
            .table(collection)
            .index_create(
                AgentOperationIndexes.ViewName
            )
            .run(conn)
        )

    if not AgentOperationIndexes.Operation in indexes:
        (
            r
            .table(collection)
            .index_create(
                AgentOperationIndexes.Operation
            )
            .run(conn)
        )

    if not AgentOperationIndexes.OperationId in indexes:
        (
            r
            .table(collection)
            .index_create(
                AgentOperationIndexes.OperationId
            )
            .run(conn)
        )

    if not AgentOperationIndexes.OperationAndView in indexes:
        (
            r
            .table(collection)
            .index_create(
                AgentOperationIndexes.OperationAndView,
                lambda x:
                [
                    x[AgentOperationKey.Operation],
                    x[AgentOperationKey.ViewName]
                ]
            )
            .run(conn)
        )

    if not AgentOperationIndexes.PluginAndView in indexes:
        (
            r
            .table(collection)
            .index_create(
                AgentOperationIndexes.PluginAndView,
                lambda x:
                [
                    x[AgentOperationKey.Plugin],
                    x[AgentOperationKey.ViewName]
                ]
            )
            .run(conn)
        )

    if not AgentOperationIndexes.CreatedByAndView in indexes:
        (
            r
            .table(collection)
            .index_create(
                AgentOperationIndexes.CreatedByAndView,
                lambda x:
                [
                    x[AgentOperationKey.CreatedBy],
                    x[AgentOperationKey.ViewName]
                ]
            )
            .run(conn)
        )


@db_create_close
def initialize_operation_per_agent_indexes(collection, indexes, conn=None):
    if not OperationPerAgentIndexes.OperationId in indexes:
        (
            r
            .table(collection)
            .index_create(
                OperationPerAgentIndexes.OperationId
            )
            .run(conn)
        )

    if not OperationPerAgentIndexes.AgentIdAndView in indexes:
        (
            r
            .table(collection)
            .index_create(
                OperationPerAgentIndexes.AgentIdAndView,
                lambda x:
                [
                    x[OperationPerAgentKey.AgentId],
                    x[OperationPerAgentKey.ViewName]
                ]
            )
            .run(conn)
        )

    if not OperationPerAgentIndexes.OperationIdAndAgentId in indexes:
        (
            r
            .table(collection)
            .index_create(
                OperationPerAgentIndexes.OperationIdAndAgentId,
                lambda x:
                [
                    x[OperationPerAgentKey.OperationId],
                    x[OperationPerAgentKey.AgentId]
                ]
            )
            .run(conn)
        )

    if not OperationPerAgentIndexes.TagIdAndView in indexes:
        (
            r
            .table(collection)
            .index_create(
                OperationPerAgentIndexes.TagIdAndView,
                lambda x:
                [
                    x[OperationPerAgentKey.TagId],
                    x[OperationPerAgentKey.ViewName]
                ]
            )
            .run(conn)
        )

    if not OperationPerAgentIndexes.StatusAndView in indexes:
        (
            r
            .table(collection)
            .index_create(
                OperationPerAgentIndexes.StatusAndView,
                lambda x:
                [
                    x[OperationPerAgentKey.Status],
                    x[OperationPerAgentKey.ViewName]
                ]
            )
            .run(conn)
        )


@db_create_close
def initialize_operation_per_app_indexes(collection, indexes, conn=None):
    if not OperationPerAppIndexes.OperationId in indexes:
        (
            r
            .table(collection)
            .index_create(
                OperationPerAppIndexes.OperationId
            )
            .run(conn)
        )

    if not OperationPerAppIndexes.OperationIdAndAgentId in indexes:
        (
            r
            .table(collection)
            .index_create(
                OperationPerAppIndexes.OperationIdAndAgentId,
                lambda x:
                [
                    x[OperationPerAgentKey.OperationId],
                    x[OperationPerAgentKey.AgentId]
                ]
            )
            .run(conn)
        )

    if not OperationPerAppIndexes.OperationIdAndAgentIdAndAppId in indexes:
        (
            r
            .table(collection)
            .index_create(
                OperationPerAgentIndexes.OperationIdAndAgentIdAndAppId,
                lambda x:
                [
                    x[OperationPerAgentKey.OperationId],
                    x[OperationPerAgentKey.AgentId],
                    x[OperationPerAgentKey.AppId]
                ]
            )
            .run(conn)
        )

try:
    admin_oper_collections = [
        (OperationCollections.Admin, AdminOperationKey.OperationId),
    ]
    agent_oper_collections = [
        (OperationCollections.Agent, AgentOperationKey.Id),
    ]
    oper_per_agent_collections = [
        (OperationCollections.OperationPerAgent, OperationPerAgentKey.Id),
    ]
    oper_per_app_collections = [
        (OperationCollections.OperationPerApp, OperationPerAppKey.Id),
    ]
    current_collections = retrieve_collections()
    for collection in admin_oper_collections:
        initialize_collections(collection, current_collections)
        name, _ = collection
        indexes = retrieve_indexes(name)
        initialize_admin_operation_indexes(name, indexes)
    for collection in agent_oper_collections:
        initialize_collections(collection, current_collections)
        name, _ = collection
        indexes = retrieve_indexes(name)
        initialize_agent_operation_indexes(collection, current_collections)
    for collection in oper_per_agent_collections:
        initialize_collections(collection, current_collections)
        name, _ = collection
        indexes = retrieve_indexes(name)
        initialize_operation_per_agent_indexes(collection, current_collections)
    for collection in oper_per_app_collections:
        initialize_collections(collection, current_collections)
        name, _ = collection
        indexes = retrieve_indexes(name)
        initialize_operation_per_app_indexes(collection, current_collections)

except Exception as e:
    logger.exception(e)
