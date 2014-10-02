#!/usr/bin/env python
from time import time
import logging

from vFense import VFENSE_LOGGING_CONFIG
from vFense.core.operations._db_model import *

from vFense.core.status_codes import (
    DbCodes, GenericCodes, GenericFailureCodes,
)

logging.config.fileConfig(VFENSE_LOGGING_CONFIG)
logger = logging.getLogger('rvapi')



def get_valid_fields(view_name):
    fields = fetch_valid_fields(view_name)
    fields['plugins'] = VALID_NOTIFICATION_PLUGINS
    fields['app_operation_types'] = VALID_APP_NOTIFICATIONS
    fields['app_thresholds'] = VALID_STATUSES_TO_ALERT_ON
    fields['monitoring_operation_types'] = VALID_MONITORING_NOTIFICATIONS


class NotificationManager():

    def __init__(self, username, view_name):

        self.username = username
        self.view_name = view_name
        self.now = time()

    @db_create_close
    def delete(self, rule_id):
        results = {}
        status_code, _, _, generated_ids = (
            delete_notification_rule(rule_id)
        )
        if status_code == DbCodes.Deleted:
            msg = (
                'Notification rule id {0} successfully deleted'.format(rule_id)
                )
            results[ApiResultKeys.GENERIC_STATUS_CODE] = (
                    GenericCodes.ObjectDeleted
            )
            results[ApiResultKeys.VFENSE_STATUS_CODE] = (
                AgentResultCodes.NewAgentSucceeded
            )
            results[ApiResultKeys.MESSAGE] = msg

        else:
            msg = 'Invalid notification id {0}'.format(rule_id)
            results[ApiResultKeys.MESSAGE] = msg
            results[ApiResultKeys.GENERIC_STATUS_CODE] = (
                GenericCodes.InvalidId
            )
            results[ApiResultKeys.VFENSE_STATUS_CODE] = (
                GenericCodes.InvalidId
            )

        return results

    def create_install_alerting_rule(self, **kwargs):
        rule_data = self.__populate_data(kwargs)
        results = self.create_alerting_rule(rule_data)
        return(results)

    def create_uninstall_alerting_rule(self, **kwargs):
        rule_data = self.__populate_data(kwargs)
        results = self.create_alerting_rule(rule_data)
        return(results)

    def create_reboot_alerting_rule(self, **kwargs):
        rule_data = self.__populate_data(kwargs)
        results = self.create_alerting_rule(rule_data)
        return(results)

    def create_shutdown_alerting_rule(self, **kwargs):
        rule_data = self.__populate_data(kwargs)
        results = self.create_alerting_rule(rule_data)
        return(results)

    def create_cpu_alerting_rule(self, **kwargs):
        rule_data = self.__populate_data(kwargs)
        results = self.create_alerting_rule(rule_data)
        return(results)

    def create_mem_alerting_rule(self, **kwargs):
        rule_data = self.__populate_data(kwargs)
        results = self.create_alerting_rule(rule_data)
        return(results)

    def create_filesystem_alerting_rule(self, **kwargs):
        rule_data = self.__populate_data(kwargs)
        results = self.create_alerting_rule(rule_data)
        return(results)

    @db_create_close
    def create_alerting_rule(self, data, conn=None):
        try:
            data_validated = self.__validate_data(data)
            data_validated['data'].pop(NotificationKeys.NotificationId, None)
            if data_validated['http_status'] == 200:
                added = (
                    r
                    .table(NotificationCollections.Notifications)
                    .insert(data_validated['data'])
                    .run(conn)
                )
                if 'inserted' in added:
                    notification_id = added.get('generated_keys')[0]
                    data_validated['data'][NotificationKeys.CreatedTime] = self.now
                    data_validated['data'][NotificationKeys.ModifiedTime] = self.now
                    data_validated['data'][NotificationKeys.NotificationId] = notification_id
                    results = (
                        NotificationResults(
                            self.username, self.uri, self.method
                        ).notification_created(data_validated['data'])
                    )
            else:
                return(data_validated)

        except Exception as e:
            logger.exception(e)
            results = (
                Results(
                    self.username, self.uri, self.method
                ).something_broke(
                    'Failed to create Notification Rule',
                    'Notification', e
                )
            )

        return(results)

    def __validate_data(self, data):
        try:
            if data[NotificationKeys.Agents]:
                is_valid, agent_id = (
                    self.__validate_agent_ids(
                        data[NotificationKeys.Agents]
                        )
                    )

                if not is_valid and agent_id:
                    return(
                        Results(
                            self.username, self.uri, self.method
                        ).invalid_id(agent_id, 'agent_id')
                    )

            if data[NotificationKeys.Tags]:
                is_valid, tag_id = (
                    self.__validate_tag_ids(
                        data[NotificationKeys.Tags]
                        )
                    )

                if not is_valid and tag_id:
                    return(
                        Results(
                            self.username, self.uri, self.method
                        ).invalid_id(tag_id, 'tag_id')
                    )

            if (not data[NotificationKeys.NotificationType] in
                    VALID_NOTIFICATIONS):

                return(
                    NotificationResults(
                        self.username, self.uri, self.method
                    ).invalid_notification_type(
                        data[NotificationKeys.NotificationType]
                    )
                )

            if data[NotificationKeys.AppThreshold]:
                if (not data[NotificationKeys.AppThreshold] in
                        VALID_STATUSES_TO_ALERT_ON):
                    return(
                        NotificationResults(
                            self.username, self.uri, self.method
                        ).invalid_notification_threshold(
                            data[NotificationKeys.AppThreshold]
                        )
                    )
            if data[NotificationKeys.RebootThreshold]:
                if (not data[NotificationKeys.RebootThreshold] in
                        VALID_STATUSES_TO_ALERT_ON):
                    return(
                        NotificationResults(
                            self.username, self.uri, self.method
                        ).invalid_notification_threshold(
                            data[NotificationKeys.RebootThreshold]
                        )
                    )
            if data[NotificationKeys.ShutdownThreshold]:
                if (not data[NotificationKeys.ShutdownThreshold] in
                        VALID_STATUSES_TO_ALERT_ON):
                    return(
                        NotificationResults(
                            self.username, self.uri, self.method
                        ).invalid_notification_threshold(
                            data[NotificationKeys.ShutdownThreshold]
                        )
                    )
            if data[NotificationKeys.CpuThreshold]:
                data[NotificationKeys.CpuThreshold] = (
                    int(data[NotificationKeys.CpuThreshold])
                )

            if data[NotificationKeys.MemThreshold]:
                data[NotificationKeys.MemThreshold] = (
                    int(data[NotificationKeys.MemThreshold])
                )

            if data[NotificationKeys.FileSystemThreshold]:
                data[NotificationKeys.FileSystemThreshold] = (
                    int(data[NotificationKeys.FileSystemThreshold])
                )

            if (not data[NotificationKeys.Plugin] in
                    VALID_NOTIFICATION_PLUGINS):

                return(
                    NotificationResults(
                        self.username, self.uri, self.method
                    ).invalid_notification_plugin(
                        data[NotificationKeys.Plugin]
                    )
                )

        except Exception as e:
            logger.exception(e)
            return(
                Results(
                    self.username, self.uri, self.method
                ).something_broke(
                    'invalid notification data',
                    'notification', e
                )
            )

        return(
            NotificationResults(
                self.username, self.uri, self.method
            ).notification_data_validated(data)
        )

    @db_create_close
    def modify_alerting_rule(self, conn=None, **kwargs):
        try:
            data = self.__populate_data(kwargs)
            data_validated = self.__validate_data(data)
            rule_exists = (
                notification_rule_exists(
                    data_validated['data'][NotificationKeys.NotificationId]
                )
            )
            if rule_exists and data_validated['http_status'] == 200:
                (
                    r
                    .table(NotificationCollections.Notifications)
                    .replace(data_validated['data'])
                    .run(conn)
                )

                data_validated['data'][NotificationKeys.CreatedTime] = self.now
                data_validated['data'][NotificationKeys.ModifiedTime] = self.now
                results = (
                    Results(
                        self.username, self.uri, self.method
                    ).object_updated(
                        data[NotificationKeys.NotificationId],
                        NotificationKeys.NotificationId, data_validated['data']
                    )
                )
            else:
                results = (
                    Results(
                        self.username, self.uri, self.method
                    ).invalid_id(
                        data[NotificationKeys.NotificationId],
                        NotificationKeys.NotificationId
                    )
                )

        except Exception as e:
            logger.exception(e)
            return(
                Results(
                    self.username, self.uri, self.method
                ).something_broke(
                    'Failed to update notification',
                    'notification', e
                )
            )

        return(results)

    @db_create_close
    def __validate_agent_ids(self, agent_ids):
        try:
            for agent_id in agent_ids:
                valid = (
                    r
                    .table(AgentsCollection)
                    .get(x)
                    .pluck(AgentKeys.AgentId)
                    .run(conn)
                )
                if not valid:
                    return(False, agent_id)

        except Exception as e:
            logger.exception(e)

        return(True, None)


    @db_create_close
    def __validate_tag_ids(self, tag_ids):
        try:
            for tag_id in tag_ids:
                valid = (
                    r
                    .table(TagsCollection)
                    .get(x)
                    .pluck(TagKeys.TagId)
                    .run(conn)
                )
                if not valid:
                    return(False, tag_id)

        except Exception as e:
            logger.exception(e)

        return(True, None)

    def __populate_data(self, data):
        keys_in_collection = self.__get_all_keys()
        for key, val in keys_in_collection.items():
            if data.get(key, None):
                keys_in_collection[key] = data[key]

        return(keys_in_collection)

    def __get_all_keys(self):
        return(
            {
                NotificationKeys.NotificationId: None,
                NotificationKeys.NotificationType: None,
                NotificationKeys.RuleName: None,
                NotificationKeys.RuleDescription: None,
                NotificationKeys.CreatedBy: None,
                NotificationKeys.CreatedTime: r.epoch_time(self.now),
                NotificationKeys.ModifiedBy: None,
                NotificationKeys.ModifiedTime: r.epoch_time(self.now),
                NotificationKeys.Plugin: None,
                NotificationKeys.User: None,
                NotificationKeys.Group: None,
                NotificationKeys.AllAgents: 'false',
                NotificationKeys.Agents: [],
                NotificationKeys.Tags: [],
                NotificationKeys.ViewName: None,
                NotificationKeys.AppThreshold: None,
                NotificationKeys.RebootThreshold: None,
                NotificationKeys.ShutdownThreshold: None,
                NotificationKeys.CpuThreshold: None,
                NotificationKeys.MemThreshold: None,
                NotificationKeys.FileSystemThreshold: None,
                NotificationKeys.FileSystem: None,
            }
        )
