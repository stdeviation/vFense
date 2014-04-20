#!/usr/bin/env python

import logging
import logging.config
from vFense.db.client import db_create_close, r
from vFense.operations import *
from vFense.operations.search._constants import OperationSearchValues
from vFense.plugins.patching import *
from vFense.plugins.patching.rv_db_calls import *
from vFense.utils.common import *
from vFense.core._constants import SortValues, DefaultQueryValues
from vFense.core.agent import AgentKey, AgentCollections

from vFense.operations import AgentOperationKey, AgentOperationIndexes, \
    OperationCollections, OperationPerAgentKey, OperationPerAgentIndexes, \
    OperationPerAppKey, OperationPerAppIndexes

logging.config.fileConfig('/opt/TopPatch/conf/logging.config')
logger = logging.getLogger('rvapi')

class FetchAgentOperations(object):
    """Agent operation database queries"""
    def __init__(
        self, customer_name=None,
        count=DefaultQueryValues.COUNT,
        offset=DefaultQueryValues.OFFSET,
        sort=SortValues.ASC,
        sort_key=AgentOperationKey.CreatedTime
        ):
        """
        Kwargs:
            customer_name (str): Fetch all operations in this customer.
            count (int): The number of results to return.
            offset (int): The next set of results beginning at offset.
            sort (str): asc or desc.
            sort_key (str): The key you are going to sort the results by.
        """

        self.customer_name = customer_name
        self.count = count
        self.offset = offset
        self.sort_key = sort_key

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

        if sort == SortValues.ASC:
            self.sort = r.asc
        else:
            self.sort = r.desc

    @db_create_close
    def fetch_all(self, conn=None):
        count = 0
        data = []
        base_filter = self._set_agent_operation_base_query()
        base_time_merge = self._set_base_time_merge()
        try:
            count = (
                base_filter
                .count()
                .run(conn)
            )

            data = list(
                base_filter
                .pluck(self.pluck_list)
                .order_by(self.sort(self.sort_key))
                .skip(self.offset)
                .limit(self.count)
                .merge(base_time_merge)
                .run(conn)
            )

        except Exception as e:
            logger.exception(e)

        return(count, data)

    @db_create_close
    def fetch_all_by_agentid(self, agent_id, conn=None):
        count = 0
        data = []
        base_time_merge = self._set_base_time_merge()
        try:
            count = (
                r
                .table(OperationCollections.OperationPerAgent)
                .get_all(
                    [agent_id, self.customer_name],
                    index=OperationPerAgentIndexes.AgentIdAndCustomer
                )
                .count()
                .run(conn)
            )

            data = list(
                r
                .table(OperationCollections.OperationPerAgent)
                .get_all(
                    [agent_id, self.customer_name],
                    index=OperationPerAgentIndexes.AgentIdAndCustomer
                )
                .eq_join(
                    AgentOperationKey.OperationId,
                    r.table(OperationCollections.Agent)
                )
                .zip()
                .pluck(self.pluck_list)
                .order_by(self.sort(self.sort_key))
                .skip(self.offset)
                .limit(self.count)
                .merge(base_time_merge)
                .run(conn)
            )

        except Exception as e:
            logger.exception(e)

        return(count, data)


    @db_create_close
    def fetch_all_by_tagid(self, tag_id, conn=None):
        count = 0
        data = []
        base_time_merge = self._set_base_time_merge()
        try:
            count = (
                r
                .table(OperationCollections.Agent)
                .get_all(tag_id, index=AgentOperationKey.TagId)
                .count()
                .run(conn)
            )

            data = list(
                r
                .table(OperationCollections.Agent)
                .get_all(tag_id, index=AgentOperationKey.TagId)
                .pluck(self.pluck_list)
                .order_by(self.sort(self.sort_key))
                .skip(self.offset)
                .limit(self.count)
                .merge(base_time_merge)
                .run(conn)
            )

        except Exception as e:
            logger.exception(e)

        return(count, data)


    @db_create_close
    def fetch_all_by_operation(self, operation, conn=None):
        count = 0
        data = []
        base_time_merge = self._set_base_time_merge()
        try:
            count = (
                r
                .table(OperationCollections.Agent)
                .get_all(
                    [operation, self.customer_name],
                    index=AgentOperationIndexes.OperationAndCustomer
                )
                .count()
                .run(conn)
            )

            data = list(
                r
                .table(OperationCollections.Agent)
                .get_all(
                        [operation, self.customer_name],
                        index=AgentOperationIndexes.OperationAndCustomer
                    )
                    .pluck(self.pluck_list)
                    .order_by(self.sort(self.sort_key))
                    .skip(self.offset)
                    .limit(self.count)
                    .merge(base_time_merge)
                    .run(conn)
                )

        except Exception as e:
            logger.exception(e)

        return(count, data)


    @db_create_close
    def fetch_install_operation_by_id(self, operation_id, conn=None):
        count = 0
        data = []
        merge = self._set_install_operation_merge()
        try:
            data = list(
                r
                .table(OperationCollections.Agent)
                .get_all(
                    operation_id,
                    index=AgentOperationIndexes.OperationId
                )
                .pluck
                .merge(merge)
                .run(conn)
            )
            if data:
                data = data[0]
                count = 1

        except Exception as e:
            logger.exception(e)

        return(count, data)

 
    @db_create_close
    def fetch_operation_by_id(self, operation_id, conn=None):
        count = 0
        data = []
        merge = self._set_operation_per_agent_merge()
        try:
            data = list(
                r
                .table(OperationCollections.Agent)
                .get_all(
                    operation_id,
                    index=AgentOperationIndexes.OperationId
                )
                .merge(merge)
                .run(conn)
            )
            if data:
                data = data[0]
                count = 1

        except Exception as e:
            logger.exception(e)

        return(count, data)


    @db_create_close
    def fetch_install_operation_for_email_alert(self, operation_id, conn=None):
        count = 0
        data = []
        merge = self._set_install_operation_email_alert_merge()
        try:
            data = list(
                r
                .table(OperationsCollection)
                .get_all(
                    operation_id,
                    index=AgentOperationIndexes.OperationId
                )
                .merge(merge)
                .run(conn)
            )
            if data:
                data = data[0]
                count = 1

        except Exception as e:
            logger.exception(e)

        return(count, data)

    @db_create_close
    def fetch_operation_for_email_alert(self, operation_id, conn=None):
        count = 0
        data = []
        merge = self._set_operation_for_email_alert_merge()
        try:
            data = list(
                r
                .table(OperationsCollection)
                .get_all(
                    operation_id,
                    index=AgentOperationIndexes.OperationId
                )
                .merge(merge)
                .run(conn)
            )
            if data:
                data = data[0]
                count = 1

        except Exception as e:
            logger.exception(e)

        return(count, data)


    def _set_operation_for_email_alert_merge(self, oper_id, conn=None):
        agent_pluck = self._set_agent_collection_pluck()
        merge = (
            {
                AgentOperationKey.CreatedTime: r.row[AgentOperationKey.CreatedTime].to_epoch_time(),
                AgentOperationKey.CompletedTime: r.row[AgentOperationKey.CompletedTime].to_epoch_time(),
                OperationSearchValues.AGENTS: (
                    r
                    .table(OperationsPerAgentCollection)
                    .get_all(
                        r.row[AgentOperationKey.OperationId],
                        index=OperationPerAgentIndexes.OperationId
                    )
                    .coerce_to('array')
                    .eq_join(OperationPerAgentKey.AgentId, r.table(AgentCollections.Agents))
                    .zip()
                    .pluck(agent_pluck)
                    .map(lambda x:
                        {
                            OperationPerAgentKey.PickedUpTime: x[OperationPerAgentKey.PickedUpTime].to_epoch_time(),
                            OperationPerAgentKey.CompletedTime: x[OperationPerAgentKey.CompletedTime].to_epoch_time(),
                        }
                    )
                )
            }
        )

        return(merge)

    def _set_base_time_merge(self):
        merge = (
            {
                AgentOperationKey.CreatedTime: (
                    r.row[AgentOperationKey.CreatedTime].to_epoch_time()
                ),
                AgentOperationKey.UpdatedTime: (
                    r.row[AgentOperationKey.UpdatedTime].to_epoch_time()
                ),
                AgentOperationKey.CompletedTime: (
                    r.row[AgentOperationKey.CompletedTime].to_epoch_time()
                ),
            }
        )

        return(merge)


    def _set_install_operation_email_alert_merge(self):
        agent_pluck = self._set_agent_collection_pluck()
        merge = (
            {
                AgentOperationKey.CreatedTime: r.row[AgentOperationKey.CreatedTime].to_iso8601(),
                AgentOperationKey.UpdatedTime: r.row[AgentOperationKey.UpdatedTime].to_iso8601(),
                AgentOperationKey.CompletedTime: r.row[AgentOperationKey.CompletedTime].to_iso8601(),
                OperationSearchValues.AGENTS: (
                    r
                    .table(OperationCollections.OperationPerAgent)
                    .get_all(
                        r.row[AgentOperationKey.OperationId],
                        index=OperationPerAgentIndexes.OperationId
                    )
                    .coerce_to('array')
                    .eq_join(OperationPerAgentKey.AgentId, r.table(AgentCollections.Agents))
                    .zip()
                    .pluck(agent_pluck)
                    .merge(lambda x:
                        {
                            OperationPerAgentKey.PickedUpTime: x[OperationPerAgentKey.PickedUpTime].to_iso8601(),
                            OperationPerAgentKey.CompletedTime: x[OperationPerAgentKey.CompletedTime].to_iso8601(),
                            OperationSearchValues.APPLICATIONS_FAILED: (
                                r
                                .table(OperationCollections.OperationPerApp)
                                .get_all(
                                    [
                                        x[AgentOperationKey.OperationId],
                                        x[OperationPerAgentKey.AgentId]
                                    ],
                                    index=OperationPerAppIndexes.OperationIdAndAgentId
                                )
                                .filter(lambda y: y[OperationPerAppKey.Results] == AgentOperationCodes.ResultsReceivedWithErrors)
                                .coerce_to('array')
                                .merge(lambda y:
                                    {
                                        OperationPerAppKey.ResultsReceivedTime: y[OperationPerAppKey.ResultsReceivedTime].to_iso8601()
                                    }
                                )
                            ),
                            OperationSearchValues.APPLICATIONS_PASSED: (
                                r
                                .table(OperationCollections.OperationPerApp)
                                .get_all(
                                    [
                                        x[AgentOperationKey.OperationId],
                                        x[OperationPerAgentKey.AgentId]
                                    ],
                                    index=OperationPerAppIndexes.OperationIdAndAgentId
                                )
                                .filter(lambda y: y[OperationPerAppKey.Results] == AgentOperationCodes.ResultsReceived)
                                .coerce_to('array')
                                .merge(lambda y:
                                    {
                                        OperationPerAppKey.ResultsReceivedTime: y[OperationPerAppKey.ResultsReceivedTime].to_iso8601()
                                    }
                                )
                            )
                        }
                    )
                )
            }
        )
        return(merge)


    def _set_operation_per_agent_merge(self):
        agent_pluck = self._set_agent_collection_pluck()
        merge = (
            {
                AgentOperationKey.CreatedTime: r.row[AgentOperationKey.CreatedTime].to_epoch_time(),
                AgentOperationKey.UpdatedTime: r.row[AgentOperationKey.UpdatedTime].to_epoch_time(),
                AgentOperationKey.CompletedTime: r.row[AgentOperationKey.CompletedTime].to_epoch_time(),
                OperationSearchValues.AGENTS: (
                    r
                    .table(OperationCollections.OperationPerAgent)
                    .get_all(
                        r.row[AgentOperationKey.OperationId],
                        index=OperationPerAgentIndexes.OperationId
                    )
                    .coerce_to('array')
                    .eq_join(OperationPerAgentKey.AgentId, r.table(AgentCollections.Agents))
                    .zip()
                    .pluck(agent_pluck)
                    .merge(lambda x:
                        {
                            OperationPerAgentKey.PickedUpTime: x[OperationPerAgentKey.PickedUpTime].to_epoch_time(),
                            OperationPerAgentKey.CompletedTime: x[OperationPerAgentKey.CompletedTime].to_epoch_time(),
                            OperationPerAgentKey.ExpiredTime: x[OperationPerAgentKey.ExpiredTime].to_epoch_time(),
                        }
                    )
                )
            }
        )

        return(merge)

    def _set_install_operation_merge(self):
        agent_pluck = self._set_agent_collection_pluck()
        merge = (
            {
                AgentOperationKey.CreatedTime: r.row[AgentOperationKey.CreatedTime].to_epoch_time(),
                AgentOperationKey.UpdatedTime: r.row[AgentOperationKey.UpdatedTime].to_epoch_time(),
                AgentOperationKey.CompletedTime: r.row[AgentOperationKey.CompletedTime].to_epoch_time(),
                OperationSearchValues.AGENTS: (
                    r
                    .table(OperationCollections.OperationPerAgent)
                    .get_all(
                        r.row[AgentOperationKey.OperationId],
                        index=OperationPerAgentIndexes.OperationId
                    )
                    .coerce_to('array')
                    .eq_join(OperationPerAgentKey.AgentId, r.table(AgentCollections.Agents))
                    .zip()
                    .pluck(agent_pluck)
                    .merge(
                        lambda x:
                        {
                            OperationPerAgentKey.PickedUpTime: x[OperationPerAgentKey.PickedUpTime].to_epoch_time(),
                            OperationPerAgentKey.CompletedTime: x[OperationPerAgentKey.CompletedTime].to_epoch_time(),
                            OperationPerAgentKey.ExpiredTime: x[OperationPerAgentKey.ExpiredTime].to_epoch_time(),
                            OperationSearchValues.APPLICATIONS: (
                                r
                                .table(OperationCollections.OperationPerApp)
                                .get_all(
                                    [
                                        x[AgentOperationKey.OperationId],
                                        x[OperationPerAgentKey.AgentId]
                                    ],
                                    index=OperationPerAppIndexes.OperationIdAndAgentId
                                )
                                .coerce_to('array')
                                .merge(lambda y:
                                    {
                                        OperationPerAppKey.ResultsReceivedTime: y[OperationPerAppKey.ResultsReceivedTime].to_epoch_time()
                                    }
                                )
                            )
                        }
                    )
                )
            }
        )

        return(merge)


    def _set_agent_operation_base_query(self):
        base_filter = (
            r
            .table(OperationCollections.Agent)
        )
        if self.customer_name:
            base_filter = (
                r
                .table(OperationCollections.Agent)
                .get_all(
                    self.customer_name,
                    index=AgentOperationIndexes.CustomerName
                )
            )

        return(base_filter)

    def _set_operation_per_agent_base_query(self):
        base_filter = (
            r
            .table(OperationCollections.OperationPerAgent)
        )
        if self.customer_name:
            base_filter = (
                r
                .table(OperationCollections.OperationPerAgent)
                .get_all(
                    self.customer_name,
                    index=OperationPerAgentIndexes.CustomerName
                )
            )

        return(base_filter)
    
    def _set_agent_collection_pluck(self):
        pluck = (
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
                OperationPerAgentKey.ExpiredTime,
                OperationPerAgentKey.Errors,
                OperationPerAgentKey.Status,
                OperationPerAgentKey.AgentId,
                AgentKey.ComputerName,
                AgentKey.DisplayName,
            ]
        )
        return(pluck)
