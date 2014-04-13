#!/usr/bin/env python

import logging
import logging.config
from datetime import datetime
from time import mktime
from vFense.db.client import db_create_close, r, db_connect
from vFense.operations import *
from vFense.operations._constants import vFenseObjects
from vFense.operations._db import fetch_agent_operation, \
    operation_with_agentid_exists, operation_with_agentid_and_appid_exists, \
    insert_into_agent_operations

from vFense.errorz.error_messages import GenericResults, OperationResults

from vFense.errorz.status_codes import DbCodes, GenericCodes,\
    AgentCodes, AgentFailureCodes, GenericFailureCodes, OperationCodes

from vFense.plugins import ra

logging.config.fileConfig('/opt/TopPatch/conf/logging.config')
logger = logging.getLogger('rvapi')


def get_agent_operation(operation_id):
    """Get an operation by id and all of it's information
    Args:
        operation_id (str): 36 character UUID

    Basic Usage:
        >>> from vFense.operations.agent_operations import get_agent_operation
        >>> operation_id = '8fed3dc7-33d4-4278-9bd4-398a68bf7f22'
        >>> get_agent_operation(operation_id)

    Results:
        Dictionary
        {
            "agents_expired_count": 0, 
            "cpu_throttle": "normal", 
            "agents_total_count": 1, 
            "plugin": "rv", 
            "tag_id": null, 
            "agents_completed_with_errors_count": 0, 
            "created_by": "admin", 
            "agents_pending_pickup_count": 0, 
            "completed_time": 1397246851, 
            "operation_status": 6006, 
            "agents_completed_count": 1, 
            "operation_id": "8fed3dc7-33d4-4278-9bd4-398a68bf7f22", 
            "created_time": 1397246674, 
            "agents_pending_results_count": 0, 
            "operation": "install_os_apps", 
            "updated_time": 1397246851, 
            "net_throttle": 0,
            "agents_failed_count": 0, 
            "restart": "none", 
            "customer_name": "default"
        }
    """
    return(fetch_agent_operation(operation_id))


def operation_for_agent_exist(operation_id, agent_id):
    """Verify if the operation exists by operation id and agent id.
    Args:
        operation_id (str): 36 character UUID
        agent_id (str): 36 character UUID

    Basic Usage:
        >>> from vFense.operations.agent_operations import operation_for_agent_exist
        >>> operation_id = '8fed3dc7-33d4-4278-9bd4-398a68bf7f22'
        >>> agent_id = 'db6bf07-c5da-4494-93bb-109db205ca64'
        >>> operation_with_agentid_exists(operation_id, agent_id)

    Results:
        Boolean True or False
    """

    return(operation_with_agentid_exists(operation_id, agent_id))


def operation_for_agent_and_app_exist(oper_id, agent_id, app_id):
    """Verify if the operation exists by operation id, agent id and app id.
    Args:
        operation_id (str): 36 character UUID
        agent_id (str): 36 character UUID
        app_id (str): 36 character UUID

    Basic Usage:
        >>> from vFense.operations._db import operation_for_agent_and_app_exist
        >>> operation_id = '8fed3dc7-33d4-4278-9bd4-398a68bf7f22'
        >>> agent_id = 'db6bf07-c5da-4494-93bb-109db205ca64'
        >>> app_id = '70d462913faad1ecaa85eda4c448a607164fe39414c8be44405e7ab4f7f8467c'
        >>> operation_for_agent_and_app_exist(operation_id, agent_id, app_id)

    Results:
        Boolean True or False
    """
    return(
        operation_with_agentid_and_appid_exists(
            operation_id, agent_id, app_id
        )
    )


class AgentOperation(object):
    def __init__(self, username, customer_name, uri, method):
        self.username = username
        self.customer_name = customer_name
        self.uri = uri
        self.method = method
        self.now = mktime(datetime.now().timetuple())
        self.db_time = r.epoch_time(self.now)
        self.INIT_COUNT = 0

    def create_operation(self, operation, plugin, agent_ids,
                         tag_id, cpu_throttle=None, net_throttle=None,
                         restart=None, performed_on=vFenseObjects.AGENT,
                         conn=None):

        number_of_agents = len(agent_ids)
        keys_to_insert = (
            {
                OperationKey.Plugin: plugin,
                OperationKey.Operation: operation,
                OperationKey.OperationStatus: OperationCodes.ResultsIncomplete,
                OperationKey.CustomerName: self.customer_name,
                OperationKey.CreatedBy: self.username,
                OperationKey.ActionPerformedOn: performed_on,
                OperationKey.TagId: tag_id,
                OperationKey.AgentsTotalCount: number_of_agents,
                OperationKey.AgentsExpiredCount: self.INIT_COUNT,
                OperationKey.AgentsPendingResultsCount: self.INIT_COUNT,
                OperationKey.AgentsPendingPickUpCount: number_of_agents,
                OperationKey.AgentsFailedCount: self.INIT_COUNT,
                OperationKey.AgentsCompletedCount: self.INIT_COUNT,
                OperationKey.AgentsCompletedWithErrorsCount: self.INIT_COUNT,
                OperationKey.CreatedTime: self.db_time,
                OperationKey.UpdatedTime: self.db_time,
                OperationKey.CompletedTime: r.epoch_time(0.0),
                OperationKey.Restart: restart,
                OperationKey.CpuThrottle: cpu_throttle,
                OperationKey.NetThrottle: net_throttle,
            }
        )
        status_code, count, errors, generated_ids = (
            insert_into_agent_operations(keys_to_insert)
        )
        if status_code == DbCodes.Inserted:
            operation_id = generated_ids[0]

        else:
            operation_id = None

        return(operation_id)

    @db_create_close
    def add_agent_to_operation(self, agent_id, operation_id, conn=None):
        try:
            (
                r
                .table(OperationsPerAgentCollection)
                .insert(
                    {
                        OperationPerAgentKey.AgentId: agent_id,
                        OperationPerAgentKey.OperationId: operation_id,
                        OperationPerAgentKey.CustomerName: self.customer_name,
                        OperationPerAgentKey.Status: PENDINGPICKUP,
                        OperationPerAgentKey.PickedUpTime: r.epoch_time(0.0),
                        OperationPerAgentKey.ExpiredTime: r.epoch_time(0.0),
                        OperationPerAgentKey.CompletedTime: r.epoch_time(0.0),
                        OperationPerAgentKey.Errors: None
                    }
                )
                .run(conn)
            )

        except Exception as e:
            results = (
                GenericResults(
                    self.username, self.uri, self.method
                ).something_broke(operation_id, 'add agent to reboot operation', e)
            )
            logger.exception(results)

    @db_create_close
    def add_agent_to_install_operation(self, agent_id, operation_id,
                                       applications, conn=None):
        try:
            (
                r
                .table(OperationsPerAgentCollection)
                .insert(
                    {
                        OperationPerAgentKey.AgentId: agent_id,
                        OperationPerAgentKey.OperationId: operation_id,
                        OperationPerAgentKey.CustomerName: self.customer_name,
                        OperationPerAgentKey.Status: PENDINGPICKUP,
                        OperationPerAgentKey.PickedUpTime: r.epoch_time(0.0),
                        OperationPerAgentKey.ExpiredTime: r.epoch_time(0.0),
                        OperationPerAgentKey.CompletedTime: r.epoch_time(0.0),
                        OperationPerAgentKey.AppsTotalCount: len(applications),
                        OperationPerAgentKey.AppsPendingCount: len(applications),
                        OperationPerAgentKey.AppsFailedCount: self.INIT_COUNT,
                        OperationPerAgentKey.AppsCompletedCount: self.INIT_COUNT,
                        OperationPerAgentKey.Errors: None
                    }
                )
                .run(conn)
            )
            for app in applications:
                (
                    r
                    .table(OperationsPerAppCollection)
                    .insert(
                        {
                            OperationPerAppKey.AgentId: agent_id,
                            OperationPerAppKey.OperationId: operation_id,
                            OperationPerAppKey.CustomerName: self.customer_name,
                            OperationPerAppKey.Results: OperationCodes.ResultsPending,
                            OperationPerAppKey.ResultsReceivedTime: r.epoch_time(0.0),
                            OperationPerAppKey.AppId: app[OperationPerAppKey.AppId],
                            OperationPerAppKey.AppName: app[OperationPerAppKey.AppName],
                            OperationPerAppKey.Errors: None
                        }
                    )
                    .run(conn)
                )

        except Exception as e:
            results = (
                GenericResults(
                    self.username, self.uri, self.method
                ).something_broke(operation_id, 'add agent to install operation', e)
            )
            logger.exception(results)

    @db_create_close
    def create_ra_operation(
        self,
        operation,
        agent_id,
        data,
        conn=None
    ):

        keys_to_insert = (
            {
                OperationKey.Plugin: ra.PluginName,
                OperationKey.Operation: operation,
                OperationKey.OperationStatus: OperationCodes.ResultsIncomplete,
                OperationKey.CustomerName: self.customer_name,
                OperationKey.CreatedBy: self.username,
                OperationKey.CreatedTime: self.db_time,
                #OperationKey.NumberOfAgents: 1,
            }
        )
        try:
            added = (
                r
                .table(OperationsCollection)
                .insert(keys_to_insert)
                .run(conn)
            )
            if 'inserted' in added:
                operation_id = added.get('generated_keys')[0]
                (
                    r
                    .table(OperationsPerAgentCollection)
                    .insert(
                        {
                            OperationPerAgentKey.AgentId: agent_id,
                            OperationPerAgentKey.OperationId: operation_id,
                            OperationPerAgentKey.CustomerName: self.customer_name,
                            OperationPerAgentKey.Status: PENDINGPICKUP,
                            OperationPerAgentKey.PickedUpTime: r.epoch_time(0.0),
                            OperationPerAgentKey.ExpiredTime: r.epoch_time(0.0),
                            OperationPerAgentKey.CompletedTime: r.epoch_time(0.0),
                        }
                    )
                    .run(conn)
                )

                data[OperationKey.OperationId] = operation_id
                results = (
                    OperationResults(
                        self.username, self.uri, self.method
                    ).operation_created(
                        operation_id,
                        operation,
                        data
                    )
                )

                logger.info(results)

        except Exception as e:
            results = (
                GenericResults(
                    self.username, self.uri, self.method
                ).something_broke(operation_id, operation, e)
            )
            logger.exception(results)

        return(results)

    @db_create_close
    def update_operation_expire_time(self, operation_id, agent_id,
                                     operation, conn=None):
        keys_to_update = (
            {
                OperationPerAgentKey.Status: OPERATION_EXPIRED,
                OperationPerAgentKey.ExpiredTime: self.db_time,
                OperationPerAgentKey.CompletedTime: self.db_time,
                OperationPerAgentKey.Errors: OPERATION_EXPIRED,
            }
        )
        try:
            (
                r
                .table(OperationsPerAgentCollection)
                .get_all(
                    [operation_id, agent_id],
                    index=OperationPerAgentIndexes.OperationIdAndAgentId
                )
                .update(keys_to_update)
                .run(conn)
            )

            (
                r
                .table(OperationsCollection)
                .get(operation_id)
                .update(
                    {
                        OperationKey.AgentsPendingPickUpCount: (
                            r.branch(
                                r.row[OperationKey.AgentsPendingPickUpCount] > 0,
                                r.row[OperationKey.AgentsPendingPickUpCount] - 1,
                                r.row[OperationKey.AgentsPendingPickUpCount],
                            )
                        ),
                        OperationKey.AgentsExpiredCount: (
                            r.branch(
                                r.row[OperationKey.AgentsExpiredCount] < r.row[OperationKey.AgentsTotalCount],
                                r.row[OperationKey.AgentsExpiredCount] + 1,
                                r.row[OperationKey.AgentsExpiredCount]
                            )
                        ),
                        OperationKey.UpdatedTime: self.db_time
                    }
                )
                .run(conn)
            )

            results = (
                OperationResults(
                    self.username, self.uri, self.method
                ).operation_updated(operation_id)
            )

            logger.info(results)

        except Exception as e:
            results = (
                GenericResults(
                    self.username, self.uri, self.method
                ).something_broke(operation_id, operation, e)
            )
            logger.exception(results)

        return(results)

    @db_create_close
    def update_operation_pickup_time(self, operation_id, agent_id,
                                     operation, conn=None):
        keys_to_update = (
            {
                OperationPerAgentKey.Status: PICKEDUP,
                OperationPerAgentKey.PickedUpTime: self.db_time,
            }
        )
        try:
            (
                r
                .table(OperationsPerAgentCollection)
                .get_all(
                    [operation_id, agent_id],
                    index=OperationPerAgentIndexes.OperationIdAndAgentId
                )
                .update(keys_to_update)
                .run(conn)
            )

            (
                r
                .table(OperationsCollection)
                .get(operation_id)
                .update(
                    {
                        OperationKey.AgentsPendingPickUpCount: (
                            r.branch(
                                r.row[OperationKey.AgentsPendingPickUpCount] > 0,
                                r.row[OperationKey.AgentsPendingPickUpCount] - 1,
                                r.row[OperationKey.AgentsPendingPickUpCount],
                            )
                        ),
                        OperationKey.AgentsPendingResultsCount: (
                            r.branch(
                                r.row[OperationKey.AgentsPendingResultsCount] < r.row[OperationKey.AgentsTotalCount],
                                r.row[OperationKey.AgentsPendingResultsCount] + 1,
                                r.row[OperationKey.AgentsPendingResultsCount]
                            )
                        ),
                        OperationKey.UpdatedTime: self.db_time
                    }
                )
                .run(conn)
            )

            results = (
                OperationResults(
                    self.username, self.uri, self.method
                ).operation_updated(operation_id)
            )

            logger.info(results)

        except Exception as e:
            results = (
                GenericResults(
                    self.username, self.uri, self.method
                ).something_broke(operation_id, operation, e)
            )
            logger.exception(results)

        return(results)

    @db_create_close
    def update_operation_results(self, operation_id, agent_id,
                                 status, operation, errors=None,
                                 conn=None):
        keys_to_update = (
            {
                OperationPerAgentKey.Status: status,
                OperationPerAgentKey.CompletedTime: self.db_time,
                OperationPerAgentKey.Errors: errors
            }
        )
        try:
            (
                r
                .table(OperationsPerAgentCollection)
                .get_all(
                    [operation_id, agent_id],
                    index=OperationPerAgentIndexes.OperationIdAndAgentId
                )
                .update(keys_to_update)
                .run(conn)
            )

            self._update_agent_stats(operation_id, agent_id)
            self._update_operation_status_code(operation_id)

            results = (
                OperationResults(
                    self.username, self.uri, self.method
                ).operation_updated(operation_id)
            )

        except Exception as e:
            results = (
                GenericResults(
                    self.username, self.uri, self.method
                ).something_broke(operation_id, operation, e)
            )
            logger.exception(results)

        return(results)

    @db_create_close
    def update_app_results(self, operation_id, agent_id, app_id,
                           results=OperationCodes.ResultsReceived,
                           errors=None, conn=None):
        keys_to_update = (
            {
                OperationPerAppKey.Results: results,
                OperationPerAppKey.ResultsReceivedTime: self.db_time,
                OperationPerAppKey.Errors: errors
            }
        )
        try:
            (
                r
                .table(OperationsPerAppCollection)
                .get_all(
                    [operation_id, agent_id, app_id],
                    index=OperationPerAppIndexes.OperationIdAndAgentIdAndAppId
                )
                .update(keys_to_update)
                .run(conn)
            )

            self._update_app_stats(operation_id, agent_id, app_id, results)

            results = (
                OperationResults(
                    self.username, self.uri, self.method
                ).operation_updated(operation_id)
            )

        except Exception as e:
            results = (
                GenericResults(
                    self.username, self.uri, self.method
                ).something_broke(operation_id, 'update_app_results', e)
            )
            logger.exception(results)

        return(results)

    @db_create_close
    def _update_app_stats(self, operation_id, agent_id,
                          app_id, results, conn=None):
        completed = True
        try:
            pending_count = 0
            completed_count = 0
            failed_count = 0
            app_stats_count = (
                r
                .table(OperationsPerAppCollection)
                .get_all(
                    [operation_id, agent_id],
                    index=OperationPerAppIndexes.OperationIdAndAgentId
                )
                .group(OperationPerAppKey.Results)
                .count()
                .ungroup()
                .run(conn)
            )

            for i in app_stats_count:
                if i['group'] == OperationCodes.ResultsPending:
                    pending_count = i['reduction']

                elif i['group'] == OperationCodes.ResultsReceived:
                    completed_count = i['reduction']

                elif i['group'] == OperationCodes.ResultsReceivedWithErrors:
                    failed_count = i['reduction']

            (
                r
                .table(OperationsPerAgentCollection)
                .get_all(
                    [operation_id, agent_id],
                    index=OperationPerAgentIndexes.OperationIdAndAgentId
                )
                .update(
                    {
                        OperationPerAgentKey.AppsCompletedCount: completed_count,
                        OperationPerAgentKey.AppsFailedCount: failed_count,
                        OperationPerAgentKey.AppsPendingCount: pending_count,
                    }
                )
                .run(conn)
            )
            self._update_agent_stats_by_app_stats(
                operation_id, agent_id, completed_count,
                failed_count, pending_count
            )

        except Exception as e:
            results = (
                GenericResults(
                    self.username, self.uri, self.method
                ).something_broke(operation_id, agent_id, e)
            )
            logger.exception(results)
            completed = False

        return(completed)

    @db_create_close
    def _update_agent_stats_by_app_stats(self, operation_id, agent_id,
                                         completed_count, failed_count,
                                         pending_count, conn=None):
        completed = True
        try:
            total_count = completed_count + failed_count + pending_count
            if total_count == completed_count:
                (
                    r
                    .table(OperationsCollection)
                    .get(operation_id)
                    .update(
                        {
                            OperationKey.AgentsCompletedCount: r.branch(
                                r.row[OperationKey.AgentsCompletedCount] < r.row[OperationKey.AgentsTotalCount],
                                r.row[OperationKey.AgentsCompletedCount] + 1,
                                r.row[OperationKey.AgentsCompletedCount]
                            ),
                            OperationKey.AgentsPendingResultsCount: r.branch(
                                r.row[OperationKey.AgentsPendingResultsCount] > 0,
                                r.row[OperationKey.AgentsPendingResultsCount] - 1,
                                r.row[OperationKey.AgentsPendingResultsCount]
                            ),
                            OperationKey.UpdatedTime: self.db_time,
                            OperationKey.CompletedTime: self.db_time
                        }
                    )
                    .run(conn)
                )
                self._update_completed_time_on_agents(operation_id, agent_id)
                self._update_operation_status_code(operation_id)

            elif total_count == failed_count:

                (
                    r
                    .table(OperationsCollection)
                    .get(operation_id)
                    .update(
                        {
                            OperationKey.AgentsFailedCount: r.branch(
                                r.row[OperationKey.AgentsFailedCount] < r.row[OperationKey.AgentsTotalCount],
                                r.row[OperationKey.AgentsFailedCount] + 1,
                                r.row[OperationKey.AgentsFailedCount]
                                ),
                            OperationKey.AgentsPendingResultsCount: r.branch(
                                r.row[OperationKey.AgentsPendingResultsCount] > 0,
                                r.row[OperationKey.AgentsPendingResultsCount] - 1,
                                r.row[OperationKey.AgentsPendingResultsCount]
                                ),
                            OperationKey.UpdatedTime: self.db_time,
                            OperationKey.CompletedTime: self.db_time
                        }
                    )
                    .run(conn)
                )
                self._update_completed_time_on_agents(operation_id, agent_id)
                self._update_operation_status_code(operation_id)

            elif total_count == (failed_count + completed_count):
                (
                    r
                    .table(OperationsCollection)
                    .get(operation_id)
                    .update(
                        {
                            OperationKey.AgentsCompletedWithErrorsCount: r.branch(
                                r.row[OperationKey.AgentsCompletedWithErrorsCount] < r.row[OperationKey.AgentsTotalCount],
                                r.row[OperationKey.AgentsCompletedWithErrorsCount] + 1,
                                r.row[OperationKey.AgentsCompletedWithErrorsCount]
                                ),
                            OperationKey.AgentsPendingResultsCount: r.branch(
                                r.row[OperationKey.AgentsPendingResultsCount] > 0,
                                r.row[OperationKey.AgentsPendingResultsCount] - 1,
                                r.row[OperationKey.AgentsPendingResultsCount]
                                ),
                            OperationKey.UpdatedTime: self.db_time,
                            OperationKey.CompletedTime: self.db_time
                        }
                    )
                    .run(conn)
                )
                self._update_completed_time_on_agents(operation_id, agent_id)
                self._update_operation_status_code(operation_id)

        except Exception as e:
            results = (
                GenericResults(
                    self.username, self.uri, self.method
                ).something_broke(operation_id, agent_id, e)
            )
            logger.exception(results)
            completed = False

        return(completed)

    @db_create_close
    def _update_agent_stats(self, operation_id, agent_id, conn=None):
        completed = True
        try:
            agent_operation = (
                r
                .table(OperationsPerAgentCollection)
                .get_all(
                    [operation_id, agent_id],
                    index=OperationPerAgentIndexes.OperationIdAndAgentId
                )
                .run(conn)
            )
            if agent_operation:
                for oper in agent_operation:
                    if (oper[OperationPerAgentKey.Status] ==
                            OperationCodes.ResultsReceived):

                        (
                            r
                            .table(OperationsCollection)
                            .get(operation_id)
                            .update(
                                {
                                    OperationKey.AgentsCompletedCount: r.branch(
                                        r.row[OperationKey.AgentsCompletedCount] < r.row[OperationKey.AgentsTotalCount],
                                        r.row[OperationKey.AgentsCompletedCount] + 1,
                                        r.row[OperationKey.AgentsCompletedCount]
                                        ),

                                    OperationKey.AgentsPendingResultsCount: r.branch(
                                        r.row[OperationKey.AgentsPendingResultsCount] > 0,
                                        r.row[OperationKey.AgentsPendingResultsCount] - 1,
                                        r.row[OperationKey.AgentsPendingResultsCount]
                                        ),
                                    OperationKey.UpdatedTime: self.db_time,
                                    OperationKey.CompletedTime: self.db_time
                                }
                            )
                            .run(conn)
                        )

                    elif (oper[OperationPerAgentKey.Status] ==
                            OperationCodes.ResultsReceivedWithErrors):

                        (
                            r
                            .table(OperationsCollection)
                            .get(operation_id)
                            .update(
                                {
                                    OperationKey.AgentsFailedCount: r.branch(
                                        r.row[OperationKey.AgentsFailedCount] < r.row[OperationKey.AgentsTotalCount],
                                        r.row[OperationKey.AgentsFailedCount] + 1,
                                        r.row[OperationKey.AgentsFailedCount]
                                        ),
                                    OperationKey.AgentsPendingResultsCount: r.branch(
                                        r.row[OperationKey.AgentsPendingResultsCount] > 0,
                                        r.row[OperationKey.AgentsPendingResultsCount] - 1,
                                        r.row[OperationKey.AgentsPendingResultsCount]
                                        ),
                                    OperationKey.UpdatedTime: self.db_time,
                                    OperationKey.CompletedTime: self.db_time
                                }
                            )
                            .run(conn)
                        )

        except Exception as e:
            results = (
                GenericResults(
                    self.username, self.uri, self.method
                ).something_broke(operation_id, agent_id, e)
            )
            logger.exception(results)
            completed = False

        return(completed)


    def _update_completed_time_on_agents(self, oper_id, agent_id):
        try:
            conn = db_connect()
            (
                r
                .table(OperationsPerAgentCollection)
                .get_all(
                    [oper_id, agent_id],
                    index=OperationPerAgentIndexes.OperationIdAndAgentId
                )
                .update({OperationPerAgentKey.CompletedTime: self.db_time})
                .run(conn)
            )
            conn.close()
        except Exception as e:
            logger.exception(e)

    def _update_operation_status_code(self, operation_id):
        try:
            conn = db_connect()
            operation = (
                r
                .table(OperationsCollection)
                .get(operation_id)
                .run(conn)
            )
            if (operation[OperationKey.AgentsTotalCount] == 
                    operation[OperationKey.AgentsCompletedCount]):
                (
                    r
                    .table(OperationsCollection)
                    .get(operation_id)
                    .update(
                        {
                            OperationKey.OperationStatus: OperationCodes.ResultsCompleted,
                            OperationKey.CompletedTime: self.db_time
                        }
                    )
                    .run(conn)
                )

            elif (operation[OperationKey.AgentsTotalCount] == 
                    operation[OperationKey.AgentsFailedCount]):
                (
                    r
                    .table(OperationsCollection)
                    .get(operation_id)
                    .update(
                        {
                            OperationKey.OperationStatus: OperationCodes.ResultsCompletedFailed,
                            OperationKey.CompletedTime: self.db_time
                        }
                    )
                    .run(conn)
                )

            elif (operation[OperationKey.AgentsTotalCount] == 
                    (
                        operation[OperationKey.AgentsFailedCount] +
                        operation[OperationKey.AgentsExpiredCount]
                    )):
                (
                    r
                    .table(OperationsCollection)
                    .get(operation_id)
                    .update(
                        {
                            OperationKey.OperationStatus: OperationCodes.ResultsCompletedFailed,
                            OperationKey.CompletedTime: self.db_time
                        }
                    )
                    .run(conn)
                )

            elif (operation[OperationKey.AgentsTotalCount] == 
                    operation[OperationKey.AgentsExpiredCount]):
                (
                    r
                    .table(OperationsCollection)
                    .get(operation_id)
                    .update(
                        {
                            OperationKey.OperationStatus: OperationCodes.ResultsCompletedFailed,
                            OperationKey.CompletedTime: self.db_time
                        }
                    )
                    .run(conn)
                )

            elif (operation[OperationKey.AgentsTotalCount] == 
                    (
                        operation[OperationKey.AgentsFailedCount] +
                        operation[OperationKey.AgentsCompletedWithErrorsCount]
                    )):
                (
                    r
                    .table(OperationsCollection)
                    .get(operation_id)
                    .update(
                        {
                            OperationKey.OperationStatus: OperationCodes.ResultsCompletedWithErrors,
                            OperationKey.CompletedTime: self.db_time
                        }
                    )
                    .run(conn)
                )

            elif (operation[OperationKey.AgentsTotalCount] == 
                    (
                        operation[OperationKey.AgentsCompletedWithErrorsCount] +
                        operation[OperationKey.AgentsExpiredCount]
                    )):
                (
                    r
                    .table(OperationsCollection)
                    .get(operation_id)
                    .update(
                        {
                            OperationKey.OperationStatus: OperationCodes.ResultsCompletedWithErrors,
                            OperationKey.CompletedTime: self.db_time
                        }
                    )
                    .run(conn)
                )


            elif (operation[OperationKey.AgentsTotalCount] == 
                    (
                        operation[OperationKey.AgentsFailedCount] +
                        operation[OperationKey.AgentsCompletedWithErrorsCount] +
                        operation[OperationKey.AgentsExpiredCount]
                    )):
                (
                    r
                    .table(OperationsCollection)
                    .get(operation_id)
                    .update(
                        {
                            OperationKey.OperationStatus: OperationCodes.ResultsCompletedWithErrors,
                            OperationKey.CompletedTime: self.db_time
                        }
                    )
                    .run(conn)
                )

            else:
                (
                    r
                    .table(OperationsCollection)
                    .get(operation_id)
                    .update(
                        {
                            OperationKey.OperationStatus: OperationCodes.ResultsIncomplete
                        }
                    )
                    .run(conn)
                )
            conn.close()

        except Exception as e:
            logger.exception(e)
