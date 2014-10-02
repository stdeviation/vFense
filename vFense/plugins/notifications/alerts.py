#!/usr/bin/env python
from time import time
import logging

from vFense import VFENSE_LOGGING_CONFIG
from vFense.core.results import ApiResultKeys
from vFense.core.agent._db import agent_exist
from vFense.core.tag._db import tag_exist
from vFense.plugins.notifications import Notification
from vFense.plugins.notifications._constants import (
    VALID_NOTIFICATION_PLUGINS, VALID_APP_NOTIFICATIONS,
    VALID_STATUSES_TO_ALERT_ON, VALID_MONITORING_NOTIFICATIONS
)
from vFense.core.status_codes import (
    DbCodes, GenericCodes, GenericFailureCodes,
)
from vFense.plugins.status_codes import (
    NotificationCodes, NotificationFailureCodes
)
from vFense.plugins._db import (
    insert_rule, delete_rule, update_rule, fetch_valid_fields
)

logging.config.fileConfig(VFENSE_LOGGING_CONFIG)
logger = logging.getLogger('rvapi')



def get_valid_fields(view_name):
    fields = fetch_valid_fields(view_name)
    fields['plugins'] = VALID_NOTIFICATION_PLUGINS
    fields['app_operation_types'] = VALID_APP_NOTIFICATIONS
    fields['app_thresholds'] = VALID_STATUSES_TO_ALERT_ON
    fields['monitoring_operation_types'] = VALID_MONITORING_NOTIFICATIONS


class NotificationManager(object):
    def __init__(self, view_name):

        self.view_name = view_name
        self.now = time()

    def delete(self, rule_id):
        results = {}
        status_code, _, _, generated_ids = (
            delete_rule(rule_id)
        )
        if status_code == DbCodes.Deleted:
            msg = (
                'Notification rule id {0} successfully deleted'.format(rule_id)
                )
            results[ApiResultKeys.GENERIC_STATUS_CODE] = (
                GenericCodes.ObjectDeleted
            )
            results[ApiResultKeys.VFENSE_STATUS_CODE] = (
                NotificationFailureCodes.NotificationDeleted
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

    def create(self, rule):
        results = {}
        if isinstance(rule, Notification):
            rule.fill_in_defaults()
            data_validated = self.__validate_data(rule)
            invalid_fields = rule.get_invalid_fields()
            if data_validated and not invalid_fields:
                status_code, _, _, generated_ids = (
                    insert_rule(rule.to_dict_db())
                )
                if status_code == DbCodes.Inserted:
                    rule.notification_id = generated_ids.pop()
                    msg = (
                        'Notification rule {0} created'.format(rule.rule_name)
                    )
                    results[ApiResultKeys.GENERIC_STATUS_CODE] = (
                        GenericCodes.ObjectCreated
                    )
                    results[ApiResultKeys.VFENSE_STATUS_CODE] = (
                        NotificationCodes.NotificationCreated
                    )
                    results[ApiResultKeys.MESSAGE] = msg
                    results[ApiResultKeys.DATA] = rule.to_dict()
                    results[ApiResultKeys.GENERATED_IDS] = rule.notification_id

                else:
                    msg = (
                        'Failed to add notification rule {0}.'.format(rule.rule_name)
                    )
                    results[ApiResultKeys.GENERIC_STATUS_CODE] = (
                        GenericFailureCodes.FailedToCreateObject
                    )
                    results[ApiResultKeys.VFENSE_STATUS_CODE] = (
                        NotificationFailureCodes.FailedToCreateNotification
                    )
                    results[ApiResultKeys.MESSAGE] = msg
                    results[ApiResultKeys.DATA] = rule.to_dict()

            elif invalid_fields:
                msg = (
                    'Failed to add notification rule {0}.'.format(rule.rule_name)
                )
                results[ApiResultKeys.GENERIC_STATUS_CODE] = (
                    GenericFailureCodes.InvalidFields
                )
                results[ApiResultKeys.VFENSE_STATUS_CODE] = (
                    NotificationFailureCodes.InvalidFields
                )
                results[ApiResultKeys.MESSAGE] = msg
                results[ApiResultKeys.DATA] = invalid_fields

            else:
                msg = (
                    'Failed to add notification rule {0}.'.format(rule.rule_name)
                )
                results[ApiResultKeys.GENERIC_STATUS_CODE] = (
                    GenericFailureCodes.InvalidId
                )
                results[ApiResultKeys.VFENSE_STATUS_CODE] = (
                    NotificationFailureCodes.InvalidId
                )
                results[ApiResultKeys.MESSAGE] = msg
                results[ApiResultKeys.DATA] = rule.agents + rule.tags

        else:
            msg = (
                'Failed to add notification rule'
            )
            results[ApiResultKeys.GENERIC_STATUS_CODE] = (
                GenericFailureCodes.InvalidInstanceType
            )
            results[ApiResultKeys.VFENSE_STATUS_CODE] = (
                NotificationFailureCodes.InvalidInstanceType
            )
            results[ApiResultKeys.MESSAGE] = msg
            results[ApiResultKeys.DATA] = rule.agents + rule.tags

        return(results)

    def update(self, rule):
        results = {}
        if isinstance(rule, Notification):
            data_validated = self.__validate_data(rule)
            invalid_fields = rule.get_invalid_fields()
            if data_validated and not invalid_fields:
                status_code, _, _, generated_ids = (
                    update_rule(rule.to_dict_db_update())
                )
                if status_code == DbCodes.Replaced or status_code == DbCodes.Unchanged:
                    msg = (
                        'Notification rule {0} updated'.format(rule.rule_name)
                    )
                    results[ApiResultKeys.GENERIC_STATUS_CODE] = (
                        GenericCodes.ObjectUpdated
                    )
                    results[ApiResultKeys.VFENSE_STATUS_CODE] = (
                        NotificationCodes.NotificationUpdated
                    )
                    results[ApiResultKeys.MESSAGE] = msg
                    results[ApiResultKeys.DATA] = rule.to_dict_non_null()
                    results[ApiResultKeys.GENERATED_IDS] = rule.notification_id

                if status_code == DbCodes.Skipped:
                    msg = (
                        'Notification rule {0} id does not exist'
                        .format(rule.notification_id)
                    )
                    results[ApiResultKeys.GENERIC_STATUS_CODE] = (
                        GenericCodes.InvalidId
                    )
                    results[ApiResultKeys.VFENSE_STATUS_CODE] = (
                        GenericCodes.InvalidId
                    )
                    results[ApiResultKeys.MESSAGE] = msg
                    results[ApiResultKeys.DATA] = rule.to_dict_non_null()
                    results[ApiResultKeys.GENERATED_IDS] = rule.notification_id

                else:
                    msg = (
                        'Failed to update notification rule {0}.'
                        .format(rule.rule_name)
                    )
                    results[ApiResultKeys.GENERIC_STATUS_CODE] = (
                        GenericFailureCodes.FailedToUpdateObject
                    )
                    results[ApiResultKeys.VFENSE_STATUS_CODE] = (
                        NotificationFailureCodes.FailedToUpdateNotification
                    )
                    results[ApiResultKeys.MESSAGE] = msg
                    results[ApiResultKeys.DATA] = rule.to_dict_non_null()

            elif invalid_fields:
                msg = (
                    'Failed to update notification rule {0}.'
                    .format(rule.rule_name)
                )
                results[ApiResultKeys.GENERIC_STATUS_CODE] = (
                    GenericFailureCodes.InvalidFields
                )
                results[ApiResultKeys.VFENSE_STATUS_CODE] = (
                    NotificationFailureCodes.InvalidFields
                )
                results[ApiResultKeys.MESSAGE] = msg
                results[ApiResultKeys.DATA] = invalid_fields

            else:
                msg = (
                    'Failed to update notification rule {0}.'
                    .format(rule.rule_name)
                )
                results[ApiResultKeys.GENERIC_STATUS_CODE] = (
                    GenericFailureCodes.InvalidId
                )
                results[ApiResultKeys.VFENSE_STATUS_CODE] = (
                    NotificationFailureCodes.InvalidId
                )
                results[ApiResultKeys.MESSAGE] = msg
                results[ApiResultKeys.DATA] = rule.agents + rule.tags

        else:
            msg = (
                'Failed to update notification rule'
            )
            results[ApiResultKeys.GENERIC_STATUS_CODE] = (
                GenericFailureCodes.InvalidInstanceType
            )
            results[ApiResultKeys.VFENSE_STATUS_CODE] = (
                NotificationFailureCodes.InvalidInstanceType
            )
            results[ApiResultKeys.MESSAGE] = msg
            results[ApiResultKeys.DATA] = rule.agents + rule.tags

        return(results)


    def validate_data(self, rule):
        if isinstance(rule, Notification):
            if rule.agents:
                is_valid, agent_id = self.validate_agent_ids(rule.agents)

                if not is_valid and agent_id:
                    return(False, agent_id)

            if rule.tags:
                is_valid, tag_id = self.validate_tag_ids(rule.tags)

                if not is_valid and tag_id:
                    return(False, tag_id)

        return(True, None)


    def validate_agent_ids(self, agent_ids):
        try:
            for agent_id in agent_ids:
                valid = agent_exist(agent_id)
                if not valid:
                    return(False, agent_id)

        except Exception as e:
            logger.exception(e)
            return(False, agent_ids)

        return(True, None)


    def validate_tag_ids(self, tag_ids):
        try:
            for tag_id in tag_ids:
                valid = tag_exist(tag_id)
                if not valid:
                    return(False, tag_id)

        except Exception as e:
            logger.exception(e)
            return(False, tag_ids)

        return(True, None)
