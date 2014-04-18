#!/usr/bin/env python

import logging
import logging.config
from vFense.db.client import db_create_close, r
from vFense.operations import *
from vFense.core.agent import *
from vFense.errorz.error_messages import GenericResults, OperationResults, AgentOperationCodes
from vFense.plugins.patching import *
from vFense.plugins.patching.rv_db_calls import *
from vFense.utils.common import *

logging.config.fileConfig('/opt/TopPatch/conf/logging.config')
logger = logging.getLogger('rvapi')

class OperationRetriever(object):
    def __init__(self, username, customer_name,
                 uri, method, count=30,
                 offset=0, sort='desc',
                 sort_key=AgentOperationKey.CreatedTime):
        self.username = username
        self.customer_name = customer_name
        self.uri = uri
        self.method = method
        self.offset = offset
        self.count = count
        self.pluck_list = (
            [
                AgentOperationKey.OperationId,
                AgentOperationKey.TagId,
                AgentOperationKey.Operation,
                AgentOperationKey.CreatedTime,
                AgentOperationKey.UpdatedTime,
                AgentOperationKey.CompletedTime,
                AgentOperationKey.OperationStatus,
                AgentOperationKey.CreatedBy,
                AgentOperationKey.CustomerName,
                AgentOperationKey.AgentsTotalCount,
                AgentOperationKey.AgentsExpiredCount,
                AgentOperationKey.AgentsPendingResultsCount,
                AgentOperationKey.AgentsPendingPickUpCount,
                AgentOperationKey.AgentsFailedCount,
                AgentOperationKey.AgentsCompletedCount,
                AgentOperationKey.AgentsCompletedWithErrorsCount,

            ]
        )
        self.map_hash = (
            {
                AgentOperationKey.OperationId: r.row[AgentOperationKey.OperationId],
                AgentOperationKey.OperationStatus: r.row[AgentOperationKey.OperationStatus],
                AgentOperationKey.TagId: r.row[AgentOperationKey.TagId],
                AgentOperationKey.Operation: r.row[AgentOperationKey.Operation],
                AgentOperationKey.CreatedTime: r.row[AgentOperationKey.CreatedTime].to_epoch_time(),
                AgentOperationKey.UpdatedTime: r.row[AgentOperationKey.UpdatedTime].to_epoch_time(),
                AgentOperationKey.CompletedTime: r.row[AgentOperationKey.CompletedTime].to_epoch_time(),
                AgentOperationKey.CreatedBy: r.row[AgentOperationKey.CreatedBy],
                AgentOperationKey.CustomerName: r.row[AgentOperationKey.CustomerName],
                AgentOperationKey.AgentsTotalCount: r.row[AgentOperationKey.AgentsTotalCount],
                AgentOperationKey.AgentsExpiredCount: r.row[AgentOperationKey.AgentsExpiredCount],
                AgentOperationKey.AgentsPendingResultsCount: r.row[AgentOperationKey.AgentsPendingResultsCount],
                AgentOperationKey.AgentsPendingPickUpCount: r.row[AgentOperationKey.AgentsPendingPickUpCount],
                AgentOperationKey.AgentsFailedCount: r.row[AgentOperationKey.AgentsFailedCount],
                AgentOperationKey.AgentsCompletedCount: r.row[AgentOperationKey.AgentsCompletedCount],
                AgentOperationKey.AgentsCompletedWithErrorsCount: r.row[AgentOperationKey.AgentsCompletedWithErrorsCount],

            }
        )
        order_by_list = (
            [
                AgentOperationKey.Operation,
                AgentOperationKey.OperationStatus,
                AgentOperationKey.CreatedTime,
                AgentOperationKey.UpdatedTime,
                AgentOperationKey.CompletedTime,
                AgentOperationKey.CreatedBy,
                AgentOperationKey.CustomerName,
            ]
        )
        if sort_key in order_by_list:
            self.sort_key = sort_key
        else:
            self.sort_key = AgentOperationKey.CreatedTime

        if sort == 'asc':
            self.sort = r.asc
        else:
            self.sort = r.desc

    @db_create_close
    def get_all_operations(self, conn=None):
        try:
            count = (
                r
                .table(OperationsCollection)
                .get_all(
                    self.customer_name,
                    index=AgentOperationIndexes.CustomerName
                )
                .count()
                .run(conn)
            )
            operations = list(
                r
                .table(OperationsCollection)
                .get_all(
                    self.customer_name,
                    index=AgentOperationIndexes.CustomerName
                )
                .pluck(self.pluck_list)
                .order_by(self.sort(self.sort_key))
                .skip(self.offset)
                .limit(self.count)
                .map(self.map_hash)
                .run(conn)
            )
            results = (
                GenericResults(
                    self.username, self.uri, self.method
                ).information_retrieved(operations, count)
            )
            logger.info(results)

        except Exception as e:
            results = (
                GenericResults(
                    self.username, self.uri, self.method
                ).something_broke('Operations Query', 'Operations', e)
            )
            logger.exception(results)

        return(results)

    @db_create_close
    def get_all_operations_by_agentid(self, agent_id, conn=None):
        try:
            count = (
                r
                .table(OperationsPerAgentCollection)
                .get_all(
                    [agent_id, self.customer_name],
                    index=OperationPerAgentIndexes.AgentIdAndCustomer
                )
                .count()
                .run(conn)
            )

            operations = list(
                r
                .table(OperationsPerAgentCollection)
                .get_all(
                    [agent_id, self.customer_name],
                    index=OperationPerAgentIndexes.AgentIdAndCustomer
                )
                .eq_join(
                    AgentOperationKey.OperationId,
                    r.table(OperationsCollection)
                )
                .zip()
                .pluck(self.pluck_list)
                .order_by(self.sort(self.sort_key))
                .skip(self.offset)
                .limit(self.count)
                .map(self.map_hash)
                .run(conn)
            )

            results = (
                GenericResults(
                    self.username, self.uri, self.method
                ).information_retrieved(operations, count)
            )
            logger.info(results)

        except Exception as e:
            results = (
                GenericResults(
                    self.username, self.uri, self.method
                ).something_broke('Operations Query', 'Operations', e)
            )
            logger.exception(results)

        return(results)


    @db_create_close
    def get_all_operations_by_tagid(self, tag_id, conn=None):
        try:
            count = (
                r
                .table(OperationsCollection)
                .get_all(tag_id, index=AgentOperationKey.TagId)
                .count()
                .run(conn)
            )

            operations = list(
                r
                .table(OperationsCollection)
                .get_all(tag_id, index=AgentOperationKey.TagId)
                .pluck(self.pluck_list)
                .order_by(self.sort(self.sort_key))
                .skip(self.offset)
                .limit(self.count)
                .map(self.map_hash)
                .run(conn)
            )

            results = (
                GenericResults(
                    self.username, self.uri, self.method
                ).information_retrieved(operations, count)
            )
            logger.info(results)

        except Exception as e:
            results = (
                GenericResults(
                    self.username, self.uri, self.method
                ).something_broke('Operations Query', 'Operations', e)
            )
            logger.exception(results)

        return(results)


    @db_create_close
    def get_all_operations_by_type(self, oper_type, conn=None):
        try:
            if oper_type in VALID_OPERATIONS:
                count = (
                    r
                    .table(OperationsCollection)
                    .get_all(
                        [oper_type, self.customer_name],
                        index=AgentOperationIndexes.OperationAndCustomer
                    )
                    .count()
                    .run(conn)
                )

                operations = list(
                    r
                    .table(OperationsCollection)
                    .get_all(
                        [oper_type, self.customer_name],
                        index=AgentOperationIndexes.OperationAndCustomer
                    )
                    .pluck(self.pluck_list)
                    .order_by(self.sort(self.sort_key))
                    .skip(self.offset)
                    .limit(self.count)
                    .map(self.map_hash)
                    .run(conn)
                )

                results = (
                    GenericResults(
                        self.username, self.uri, self.method
                    ).information_retrieved(operations, count)
                )
                logger.info(results)

            else:
                results = (
                    OperationResults(
                        self.username, self.uri, self.method
                    ).invalid_operation_type(oper_type)
                )
                logger.warn(results)

        except Exception as e:
            results = (
                GenericResults(
                    self.username, self.uri, self.method
                ).something_broke('Operations Query', 'Operations', e)
            )
            logger.exception(results)

        return(results)


    @db_create_close
    def get_install_operation_by_id(self, oper_id, conn=None):
        pluck_list = (
            [
                AgentOperationKey.OperationId,
                AgentOperationKey.Operation,
                AgentOperationKey.OperationStatus,
                AgentOperationKey.CreatedTime,
                AgentOperationKey.CreatedBy,
                AgentOperationKey.UpdatedTime,
                AgentOperationKey.CompletedTime,
                AgentOperationKey.CustomerName,
                AgentOperationKey.AgentsTotalCount,
                AgentOperationKey.AgentsExpiredCount,
                AgentOperationKey.AgentsPendingResultsCount,
                AgentOperationKey.AgentsPendingPickUpCount,
                AgentOperationKey.AgentsFailedCount,
                AgentOperationKey.AgentsCompletedCount,
                AgentOperationKey.AgentsCompletedWithErrorsCount,
                OperationPerAgentKey.PickedUpTime,
                OperationPerAgentKey.CompletedTime,
                OperationPerAgentKey.AppsTotalCount,
                OperationPerAgentKey.AppsPendingCount,
                OperationPerAgentKey.AppsFailedCount,
                OperationPerAgentKey.AppsCompletedCount,
                OperationPerAgentKey.Errors,
                OperationPerAgentKey.Status,
                OperationPerAgentKey.AgentId,
                AgentKey.ComputerName,
                AgentKey.DisplayName,
                OperationPerAppKey.AppId,
                OperationPerAppKey.AppName,
                OperationPerAppKey.Results,
                OperationPerAppKey.ResultsReceivedTime,
            ]
        )
        map_list = (
            {
                AgentOperationKey.OperationId: r.row[AgentOperationKey.OperationId],
                AgentOperationKey.Operation: r.row[AgentOperationKey.Operation],
                AgentOperationKey.OperationStatus: r.row[AgentOperationKey.OperationStatus],
                AgentOperationKey.CreatedTime: r.row[AgentOperationKey.CreatedTime].to_epoch_time(),
                AgentOperationKey.CreatedBy: r.row[AgentOperationKey.CreatedBy],
                AgentOperationKey.UpdatedTime: r.row[AgentOperationKey.UpdatedTime].to_epoch_time(),
                AgentOperationKey.CompletedTime: r.row[AgentOperationKey.CompletedTime].to_epoch_time(),
                AgentOperationKey.CustomerName: r.row[AgentOperationKey.CustomerName],
                AgentOperationKey.AgentsTotalCount: r.row[AgentOperationKey.AgentsTotalCount],
                AgentOperationKey.AgentsExpiredCount: r.row[AgentOperationKey.AgentsExpiredCount],
                AgentOperationKey.AgentsPendingResultsCount: r.row[AgentOperationKey.AgentsPendingResultsCount],
                AgentOperationKey.AgentsPendingPickUpCount: r.row[AgentOperationKey.AgentsPendingPickUpCount],
                AgentOperationKey.AgentsFailedCount: r.row[AgentOperationKey.AgentsFailedCount],
                AgentOperationKey.AgentsCompletedCount: r.row[AgentOperationKey.AgentsCompletedCount],
                AgentOperationKey.AgentsCompletedWithErrorsCount: r.row[AgentOperationKey.AgentsCompletedWithErrorsCount],
                "agents": (
                    r
                    .table(OperationsPerAgentCollection)
                    .get_all(
                        r.row[AgentOperationKey.OperationId],
                        index=OperationPerAgentIndexes.OperationId
                    )
                    .coerce_to('array')
                    .eq_join(OperationPerAgentKey.AgentId, r.table(AgentsCollection))
                    .zip()
                    .map(lambda x:
                        {
                            OperationPerAgentKey.PickedUpTime: x[OperationPerAgentKey.PickedUpTime].to_epoch_time(),
                            OperationPerAgentKey.CompletedTime: x[OperationPerAgentKey.CompletedTime].to_epoch_time(),
                            OperationPerAgentKey.ExpiredTime: x[OperationPerAgentKey.ExpiredTime].to_epoch_time(),
                            OperationPerAgentKey.AppsTotalCount: x[OperationPerAgentKey.AppsTotalCount],
                            OperationPerAgentKey.AppsPendingCount: x[OperationPerAgentKey.AppsPendingCount],
                            OperationPerAgentKey.AppsFailedCount: x[OperationPerAgentKey.AppsFailedCount],
                            OperationPerAgentKey.AppsCompletedCount: x[OperationPerAgentKey.AppsCompletedCount],
                            OperationPerAgentKey.Errors: x[OperationPerAgentKey.Errors],
                            OperationPerAgentKey.Status: x[OperationPerAgentKey.Status],
                            OperationPerAgentKey.AgentId: x[OperationPerAgentKey.AgentId],
                            AgentKey.ComputerName: x[AgentKey.ComputerName],
                            AgentKey.DisplayName: x[AgentKey.DisplayName],
                            "applications": (
                                r
                                .table(OperationsPerAppCollection)
                                .get_all(
                                    [
                                        x[AgentOperationKey.OperationId],
                                        x[OperationPerAgentKey.AgentId]
                                    ],
                                    index=OperationPerAppIndexes.OperationIdAndAgentId
                                )
                                .coerce_to('array')
                                .map(lambda y:
                                    {
                                        OperationPerAppKey.AppId: y[OperationPerAppKey.AppId],
                                        OperationPerAppKey.AppName: y[OperationPerAppKey.AppName],
                                        OperationPerAppKey.Results: y[OperationPerAppKey.Results],
                                        OperationPerAppKey.Errors: y[OperationPerAppKey.Errors],
                                        OperationPerAppKey.ResultsReceivedTime: y[OperationPerAppKey.ResultsReceivedTime].to_epoch_time()
                                    }
                                )
                            )
                        }
                    )
                )
            }
        )
        try:
            operations = list(
                r
                .table(OperationsCollection)
                .get_all(
                    oper_id,
                    index=AgentOperationIndexes.OperationId
                )
                .pluck(pluck_list)
                .map(map_list)
                .run(conn)
            )
            if operations:
                operations = operations[0]

            results = (
                GenericResults(
                    self.username, self.uri, self.method
                ).information_retrieved(operations, 1)
            )
            logger.info(results)

        except Exception as e:
            results = (
                GenericResults(
                    self.username, self.uri, self.method
                ).something_broke('Operations Query', 'Operations', e)
            )
            logger.exception(results)

        return(results)

    @db_create_close
    def get_operation_by_id(self, oper_id, conn=None):
        pluck_list = (
            [
                AgentOperationKey.OperationId,
                AgentOperationKey.Operation,
                AgentOperationKey.OperationStatus,
                AgentOperationKey.CreatedTime,
                AgentOperationKey.CreatedBy,
                AgentOperationKey.UpdatedTime,
                AgentOperationKey.CompletedTime,
                AgentOperationKey.CustomerName,
                AgentOperationKey.AgentsTotalCount,
                AgentOperationKey.AgentsExpiredCount,
                AgentOperationKey.AgentsPendingResultsCount,
                AgentOperationKey.AgentsPendingPickUpCount,
                AgentOperationKey.AgentsFailedCount,
                AgentOperationKey.AgentsCompletedCount,
                AgentOperationKey.AgentsCompletedWithErrorsCount,
                OperationPerAgentKey.PickedUpTime,
                OperationPerAgentKey.CompletedTime,
                OperationPerAgentKey.ExpiredTime,
                OperationPerAgentKey.Errors,
                OperationPerAgentKey.Status,
                OperationPerAgentKey.AgentId,
                AgentKey.ComputerName,
                AgentKey.DisplayName,
            ]
        )
        map_list = (
            {
                AgentOperationKey.OperationId: r.row[AgentOperationKey.OperationId],
                AgentOperationKey.Operation: r.row[AgentOperationKey.Operation],
                AgentOperationKey.OperationStatus: r.row[AgentOperationKey.OperationStatus],
                AgentOperationKey.CreatedTime: r.row[AgentOperationKey.CreatedTime].to_epoch_time(),
                AgentOperationKey.CreatedBy: r.row[AgentOperationKey.CreatedBy],
                AgentOperationKey.UpdatedTime: r.row[AgentOperationKey.UpdatedTime].to_epoch_time(),
                AgentOperationKey.CompletedTime: r.row[AgentOperationKey.CompletedTime].to_epoch_time(),
                AgentOperationKey.CustomerName: r.row[AgentOperationKey.CustomerName],
                AgentOperationKey.AgentsTotalCount: r.row[AgentOperationKey.AgentsTotalCount],
                AgentOperationKey.AgentsExpiredCount: r.row[AgentOperationKey.AgentsExpiredCount],
                AgentOperationKey.AgentsPendingResultsCount: r.row[AgentOperationKey.AgentsPendingResultsCount],
                AgentOperationKey.AgentsPendingPickUpCount: r.row[AgentOperationKey.AgentsPendingPickUpCount],
                AgentOperationKey.AgentsFailedCount: r.row[AgentOperationKey.AgentsFailedCount],
                AgentOperationKey.AgentsCompletedCount: r.row[AgentOperationKey.AgentsCompletedCount],
                AgentOperationKey.AgentsCompletedWithErrorsCount: r.row[AgentOperationKey.AgentsCompletedWithErrorsCount],
                "agents": (
                    r
                    .table(OperationsPerAgentCollection)
                    .get_all(
                        r.row[AgentOperationKey.OperationId],
                        index=OperationPerAgentIndexes.OperationId
                    )
                    .coerce_to('array')
                    .eq_join(OperationPerAgentKey.AgentId, r.table(AgentsCollection))
                    .zip()
                    .map(lambda x:
                        {
                            OperationPerAgentKey.PickedUpTime: x[OperationPerAgentKey.PickedUpTime].to_epoch_time(),
                            OperationPerAgentKey.CompletedTime: x[OperationPerAgentKey.CompletedTime].to_epoch_time(),
                            OperationPerAgentKey.ExpiredTime: x[OperationPerAgentKey.ExpiredTime].to_epoch_time(),
                            OperationPerAgentKey.Errors: x[OperationPerAgentKey.Errors],
                            OperationPerAgentKey.Status: x[OperationPerAgentKey.Status],
                            OperationPerAgentKey.AgentId: x[OperationPerAgentKey.AgentId],
                            AgentKey.ComputerName: x[AgentKey.ComputerName],
                            AgentKey.DisplayName: x[AgentKey.DisplayName],
                        }
                    )
                )
            }
        )

        try:
            operations = list(
                r
                .table(OperationsCollection)
                .get_all(
                    oper_id,
                    index=AgentOperationIndexes.OperationId
                )
                .pluck(pluck_list)
                .map(map_list)
                .run(conn)
            )
            if operations:
                operations = operations[0]

            results = (
                GenericResults(
                    self.username, self.uri, self.method
                ).information_retrieved(operations, 1)
            )
            logger.info(results)

        except Exception as e:
            results = (
                GenericResults(
                    self.username, self.uri, self.method
                ).something_broke('Operations Query', 'Operations', e)
            )
            logger.exception(results)

        return(results)


    @db_create_close
    def get_install_operation_for_email_alert(self, oper_id, conn=None):
        pluck_list = (
            [
                AgentOperationKey.OperationId,
                AgentOperationKey.OperationStatus,
                AgentOperationKey.CreatedTime,
                AgentOperationKey.CreatedBy,
                AgentOperationKey.UpdatedTime,
                AgentOperationKey.CompletedTime,
                AgentOperationKey.CustomerName,
                OperationPerAgentKey.PickedUpTime,
                OperationPerAgentKey.CompletedTime,
                OperationPerAgentKey.Errors,
                OperationPerAgentKey.AgentId,
                AgentKey.ComputerName,
                AgentKey.DisplayName,
                OperationPerAppKey.AppName,
                OperationPerAppKey.Results,
                OperationPerAppKey.ResultsReceivedTime,
            ]
        )
        map_list = (
            {
                AgentOperationKey.OperationStatus: r.row[AgentOperationKey.OperationStatus],
                AgentOperationKey.CreatedTime: r.row[AgentOperationKey.CreatedTime].to_iso8601(),
                AgentOperationKey.CreatedBy: r.row[AgentOperationKey.CreatedBy],
                AgentOperationKey.UpdatedTime: r.row[AgentOperationKey.UpdatedTime].to_iso8601(),
                AgentOperationKey.CompletedTime: r.row[AgentOperationKey.CompletedTime].to_iso8601(),
                AgentOperationKey.CustomerName: r.row[AgentOperationKey.CustomerName],
                "agents": (
                    r
                    .table(OperationsPerAgentCollection)
                    .get_all(
                        r.row[AgentOperationKey.OperationId],
                        index=OperationPerAgentIndexes.OperationId
                    )
                    .coerce_to('array')
                    .eq_join(OperationPerAgentKey.AgentId, r.table(AgentsCollection))
                    .zip()
                    .map(lambda x:
                        {
                            OperationPerAgentKey.PickedUpTime: x[OperationPerAgentKey.PickedUpTime].to_iso8601(),
                            OperationPerAgentKey.CompletedTime: x[OperationPerAgentKey.CompletedTime].to_iso8601(),
                            OperationPerAgentKey.Errors: x[OperationPerAgentKey.Errors],
                            OperationPerAgentKey.AgentId: x[OperationPerAgentKey.AgentId],
                            AgentKey.ComputerName: x[AgentKey.ComputerName],
                            AgentKey.DisplayName: x[AgentKey.DisplayName],
                            "applications_failed": (
                                r
                                .table(OperationsPerAppCollection)
                                .get_all(
                                    [
                                        x[AgentOperationKey.OperationId],
                                        x[OperationPerAgentKey.AgentId]
                                    ],
                                    index=OperationPerAppIndexes.OperationIdAndAgentId
                                )
                                .filter(lambda y: y[OperationPerAppKey.Results] == AgentOperationCodes.ResultsReceivedWithErrors)
                                .coerce_to('array')
                                .map(lambda y:
                                    {
                                        OperationPerAppKey.AppName: y[OperationPerAppKey.AppName],
                                        OperationPerAppKey.Errors: y[OperationPerAppKey.Errors],
                                        OperationPerAppKey.ResultsReceivedTime: y[OperationPerAppKey.ResultsReceivedTime].to_iso8601()
                                    }
                                )
                            ),
                            "applications_passed": (
                                r
                                .table(OperationsPerAppCollection)
                                .get_all(
                                    [
                                        x[AgentOperationKey.OperationId],
                                        x[OperationPerAgentKey.AgentId]
                                    ],
                                    index=OperationPerAppIndexes.OperationIdAndAgentId
                                )
                                .filter(lambda y: y[OperationPerAppKey.Results] == AgentOperationCodes.ResultsReceived)
                                .coerce_to('array')
                                .map(lambda y:
                                    {
                                        OperationPerAppKey.AppName: y[OperationPerAppKey.AppName],
                                        OperationPerAppKey.Errors: y[OperationPerAppKey.Errors],
                                        OperationPerAppKey.ResultsReceivedTime: y[OperationPerAppKey.ResultsReceivedTime].to_iso8601()
                                    }
                                )
                            )
                        }
                    )
                )
            }
        )
        try:
            operations = list(
                r
                .table(OperationsCollection)
                .get_all(
                    oper_id,
                    index=AgentOperationIndexes.OperationId
                )
                .pluck(pluck_list)
                .map(map_list)
                .run(conn)
            )
            if operations:
                operations = operations[0]

        except Exception as e:
            logger.exception(e)
            operations = None

        return(operations)


    @db_create_close
    def get_base_operation_for_email_alert(self, oper_id, conn=None):
        pluck_list = (
            [
                AgentOperationKey.OperationId,
                AgentOperationKey.Operation,
                AgentOperationKey.OperationStatus,
                AgentOperationKey.CreatedTime,
                AgentOperationKey.CreatedBy,
                AgentOperationKey.CompletedTime,
                AgentOperationKey.CustomerName,
                AgentOperationKey.AgentsTotalCount,
                AgentOperationKey.AgentsFailedCount,
                AgentOperationKey.AgentsCompletedCount,
                AgentOperationKey.AgentsCompletedWithErrorsCount,
                OperationPerAgentKey.PickedUpTime,
                OperationPerAgentKey.CompletedTime,
                OperationPerAgentKey.Errors,
                OperationPerAgentKey.Status,
                OperationPerAgentKey.AgentId,
                AgentKey.ComputerName,
                AgentKey.DisplayName,
            ]
        )
        map_list = (
            {
                AgentOperationKey.OperationId: r.row[AgentOperationKey.OperationId],
                AgentOperationKey.Operation: r.row[AgentOperationKey.Operation],
                AgentOperationKey.OperationStatus: r.row[AgentOperationKey.OperationStatus],
                AgentOperationKey.CreatedTime: r.row[AgentOperationKey.CreatedTime].to_epoch_time(),
                AgentOperationKey.CreatedBy: r.row[AgentOperationKey.CreatedBy],
                AgentOperationKey.CompletedTime: r.row[AgentOperationKey.CompletedTime].to_epoch_time(),
                AgentOperationKey.CustomerName: r.row[AgentOperationKey.CustomerName],
                AgentOperationKey.AgentsTotalCount: r.row[AgentOperationKey.AgentsTotalCount],
                AgentOperationKey.AgentsFailedCount: r.row[AgentOperationKey.AgentsFailedCount],
                AgentOperationKey.AgentsCompletedCount: r.row[AgentOperationKey.AgentsCompletedCount],
                AgentOperationKey.AgentsCompletedWithErrorsCount: r.row[AgentOperationKey.AgentsCompletedWithErrorsCount],
                "agents": (
                    r
                    .table(OperationsPerAgentCollection)
                    .get_all(
                        r.row[AgentOperationKey.OperationId],
                        index=OperationPerAgentIndexes.OperationId
                    )
                    .coerce_to('array')
                    .eq_join(OperationPerAgentKey.AgentId, r.table(AgentsCollection))
                    .zip()
                    .map(lambda x:
                        {
                            OperationPerAgentKey.PickedUpTime: x[OperationPerAgentKey.PickedUpTime].to_epoch_time(),
                            OperationPerAgentKey.CompletedTime: x[OperationPerAgentKey.CompletedTime].to_epoch_time(),
                            OperationPerAgentKey.Errors: x[OperationPerAgentKey.Errors],
                            OperationPerAgentKey.Status: x[OperationPerAgentKey.Status],
                            AgentKey.ComputerName: x[AgentKey.ComputerName],
                            AgentKey.DisplayName: x[AgentKey.DisplayName],
                        }
                    )
                )
            }
        )

        try:
            operations = list(
                r
                .table(OperationsCollection)
                .get_all(
                    oper_id,
                    index=AgentOperationIndexes.OperationId
                )
                .pluck(pluck_list)
                .map(map_list)
                .run(conn)
            )
            if operations:
                operations = operations[0]

            results = (
                GenericResults(
                    self.username, self.uri, self.method
                ).information_retrieved(operations, 1)
            )
            logger.info(results)

        except Exception as e:
            results = (
                GenericResults(
                    self.username, self.uri, self.method
                ).something_broke('Operations Query', 'Operations', e)
            )
            logger.exception(results)

        return(results)


