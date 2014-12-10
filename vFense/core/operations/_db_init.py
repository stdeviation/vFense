import logging, logging.config
from vFense._constants import VFENSE_LOGGING_CONFIG
from vFense.db.client import r
from vFense.db.manager import DbInit
from vFense.core.operations._db_model import (
    OperationCollections, AdminOperationKey, AdminOperationIndexes,
    AgentOperationKey, AgentOperationIndexes, OperationPerAgentKey,
    OperationPerAgentIndexes, OperationPerAppKey, OperationPerAppIndexes
)

logging.config.fileConfig(VFENSE_LOGGING_CONFIG)
logger = logging.getLogger('vfense_api')

collections = [
   (OperationCollections.Admin, AdminOperationKey.OperationId),
   (OperationCollections.Agent, AgentOperationKey.OperationId),
   (OperationCollections.OperationPerAgent, OperationPerAgentKey.Id),
   (OperationCollections.OperationPerApp, OperationPerAppKey.Id),
]

secondary_indexes = [
    (
        OperationCollections.Admin,
        AdminOperationIndexes.CreatedBy,
        (
            r
            .table(OperationCollections.Admin)
            .index_create(AdminOperationIndexes.CreatedBy)
        )
    ),
    (
        OperationCollections.Admin,
        AdminOperationIndexes.GenericStatusCode,
        (
            r
            .table(OperationCollections.Admin)
            .index_create(AdminOperationIndexes.GenericStatusCode)
        )
    ),
    (
        OperationCollections.Admin,
        AdminOperationIndexes.VfenseStatusCode,
        (
            r
            .table(OperationCollections.Admin)
            .index_create(AdminOperationIndexes.VfenseStatusCode)
        )
    ),
    (
        OperationCollections.Admin,
        AdminOperationIndexes.Action,
        (
            r
            .table(OperationCollections.Admin)
            .index_create(AdminOperationIndexes.Action)
        )
    ),
    (
        OperationCollections.Admin,
        AdminOperationIndexes.ActionPerformedOn,
        (
            r
            .table(OperationCollections.Admin)
            .index_create(AdminOperationIndexes.ActionPerformedOn)
        )
    ),
    (
        OperationCollections.Agent,
        AgentOperationIndexes.TagId,
        (
            r
            .table(OperationCollections.Agent)
            .index_create(AgentOperationIndexes.TagId)
        )
    ),
    (
        OperationCollections.Agent,
        AgentOperationIndexes.AgentIds,
        (
            r
            .table(OperationCollections.Agent)
            .index_create(
                AgentOperationIndexes.AgentIds,
                multi=True
            )
        )
    ),
    (
        OperationCollections.Agent,
        AgentOperationIndexes.ViewName,
        (
            r
            .table(OperationCollections.Agent)
            .index_create(AgentOperationIndexes.ViewName)
        )
    ),
    (
        OperationCollections.Agent,
        AgentOperationIndexes.Operation,
        (
            r
            .table(OperationCollections.Agent)
            .index_create(AgentOperationIndexes.Operation)
        )
    ),
    (
        OperationCollections.Agent,
        AgentOperationIndexes.OperationAndView,
        (
            r
            .table(OperationCollections.Agent)
            .index_create(
                AgentOperationIndexes.OperationAndView,
                lambda x:
                [
                    x[AgentOperationKey.Operation],
                    x[AgentOperationKey.ViewName]
                ]
            )
        )
    ),
    (
        OperationCollections.Agent,
        AgentOperationIndexes.PluginAndView,
        (
            r
            .table(OperationCollections.Agent)
            .index_create(
                AgentOperationIndexes.PluginAndView,
                lambda x:
                [
                    x[AgentOperationKey.Plugin],
                    x[AgentOperationKey.ViewName]
                ]
            )
        )
    ),
    (
        OperationCollections.Agent,
        AgentOperationIndexes.CreatedByAndView,
        (
            r
            .table(OperationCollections.Agent)
            .index_create(
                AgentOperationIndexes.CreatedByAndView,
                lambda x:
                [
                    x[AgentOperationKey.CreatedBy],
                    x[AgentOperationKey.ViewName]
                ]
            )
        )
    ),
    (
        OperationCollections.OperationPerAgent,
        OperationPerAgentIndexes.OperationId,
        (
            r
            .table(OperationCollections.OperationPerAgent)
            .index_create(OperationPerAgentIndexes.OperationId)
        )
    ),
    (
        OperationCollections.OperationPerAgent,
        OperationPerAgentIndexes.AgentIdAndView,
        (
            r
            .table(OperationCollections.OperationPerAgent)
            .index_create(
                OperationPerAgentIndexes.AgentIdAndView,
                lambda x:
                [
                    x[OperationPerAgentKey.AgentId],
                    x[OperationPerAgentKey.ViewName]
                ]
            )
        )
    ),
    (
        OperationCollections.OperationPerAgent,
        OperationPerAgentIndexes.OperationIdAndAgentId,
        (
            r
            .table(OperationCollections.OperationPerAgent)
            .index_create(
                OperationPerAgentIndexes.OperationIdAndAgentId,
                lambda x:
                [
                    x[OperationPerAgentKey.OperationId],
                    x[OperationPerAgentKey.AgentId]
                ]
            )
        )
    ),
    (
        OperationCollections.OperationPerAgent,
        OperationPerAgentIndexes.TagIdAndView,
        (
            r
            .table(OperationCollections.OperationPerAgent)
            .index_create(
                OperationPerAgentIndexes.TagIdAndView,
                lambda x:
                [
                    x[OperationPerAgentKey.TagId],
                    x[OperationPerAgentKey.ViewName]
                ]
            )
        )
    ),
    (
        OperationCollections.OperationPerAgent,
        OperationPerAgentIndexes.StatusAndView,
        (
            r
            .table(OperationCollections.OperationPerAgent)
            .index_create(
                OperationPerAgentIndexes.StatusAndView,
                lambda x:
                [
                    x[OperationPerAgentKey.Status],
                    x[OperationPerAgentKey.ViewName]
                ]
            )
        )
    ),
    (
        OperationCollections.OperationPerApp,
        OperationPerAppIndexes.OperationId,
        (
            r
            .table(OperationCollections.OperationPerApp)
            .index_create(OperationPerAppIndexes.OperationId)
        )
    ),
    (
        OperationCollections.OperationPerApp,
        OperationPerAppIndexes.OperationIdAndAgentId,
        (
            r
            .table(OperationCollections.OperationPerApp)
            .index_create(
                OperationPerAppIndexes.OperationIdAndAgentId,
                lambda x:
                [
                    x[OperationPerAppKey.OperationId],
                    x[OperationPerAppKey.AgentId]
                ]
            )
        )
    ),
    (
        OperationCollections.OperationPerApp,
        OperationPerAppIndexes.OperationIdAndAgentIdAndAppId,
        (
            r
            .table(OperationCollections.OperationPerApp)
            .index_create(
                OperationPerAppIndexes.OperationIdAndAgentIdAndAppId,
                lambda x:
                [
                    x[OperationPerAppKey.OperationId],
                    x[OperationPerAppKey.AgentId],
                    x[OperationPerAppKey.AppId]
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
