#!/usr/bin/env python
from time import time
import logging

from vFense._constants import VFENSE_LOGGING_CONFIG
from vFense.core.results import ApiResults
from vFense.core.status_codes import (
    DbCodes, GenericCodes, GenericFailureCodes,
)
from vFense.plugins.notifications.mailer.status_codes import (
    EmailCodes, EmailFailureCodes
)
from vFense.plugins.notifications.mailer import NotificationPlugin
from vFense.plugins.notifications.mailer._db import (
    fetch_email_config, insert_email, update_email, delete_email
)

logging.config.fileConfig(VFENSE_LOGGING_CONFIG)
logger = logging.getLogger('rvapi')


class MailManager(object):
    def __init__(self, view_name=None):
        self.__view_name = view_name
        self.config = self.get_config()

    def get_config(self):
        config = fetch_email_config(self.view_name)
        if config:
            config = NotificationPlugin(**config)
        else:
            config = NotificationPlugin()

        return config

    def create(self, config):
        if isinstance(config, NotificationPlugin):
            results = ApiResults()
            results.fill_in_defaults()
            if (config.username and config.password and config.server and
                    config.port and config.from_email):
                config.fill_in_defaults()
                invalid_fields = config.get_invalid_fields()
                if not invalid_fields():
                    status_code, _, _, generated_ids = (
                        insert_email(config.to_dict_db())
                    )
                    if status_code == DbCodes.Inserted:
                        config.id = generated_ids.pop()
                        msg = 'Email settings created'
                        results.generic_status_code = (
                            GenericCodes.ObjectCreated
                        )
                        results.vfense_status_code = (
                            EmailCodes.EmailSettingsCreated
                        )
                        results.message = msg
                        results.data.append(config.to_dict())
                        results.generated_ids.append(config.id)

                    else:
                        msg = 'Failed to create email settings.'
                        results.generic_status_code = (
                            GenericFailureCodes.FailedToCreateObject
                        )
                        results.vfense_status_code = (
                            EmailFailureCodes.FailedToCreateEmailSettings
                        )
                        results.message = msg
                        results.data.append(config.to_dict())

                else:
                    msg = (
                        'Failed to create email settings,' +
                        ' invalid fields were passed'
                    )
                    results.generic_status_code = (
                        GenericFailureCodes.FailedToCreateObject
                    )
                    results.vfense_status_code = (
                        EmailFailureCodes.FailedToCreateEmailSettings
                    )
                    results.message = msg
                    results.errors = invalid_fields
                    results.data.append(config.to_dict())

            else:
                msg = (
                    'Failed to create email settings, not all of the' +
                    ' required fields were passed.'
                )
                results.generic_status_code = (
                    GenericFailureCodes.FailedToCreateObject
                )
                results.vfense_status_code = (
                    EmailFailureCodes.FailedToCreateEmailSettings
                )
                results.message = msg
                results.errors = invalid_fields
                results.data.append(config.to_dict())

        else:
            msg = (
                'Pass a valid NotificationPlugins instance and not a {0}'
                .format(type(config))
            )
            results.generic_status_code = (
                GenericFailureCodes.InvalidInstanceType
            )
            results.vfense_status_code = (
                EmailFailureCodes.FailedToCreateEmailSettings
            )
            results.message = msg
            results.errors = invalid_fields
            results.data.append(config.to_dict())

        return results

    def update(self, config):
        if isinstance(config, NotificationPlugin):
            results = ApiResults()
            results.fill_in_defaults()
            invalid_fields = config.get_invalid_fields()
            if not invalid_fields() and config.id:
                config.modified_time = time()
                status_code, _, _, generated_ids = (
                    update_email(config.id, config.to_dict_db_update())
                )
                if status_code == DbCodes.Replaced or status_code == DbCodes.Unchanged:
                    msg = 'Email settings updated'
                    results.generic_status_code = (
                        GenericCodes.ObjectUpdated
                    )
                    results.vfense_status_code = (
                        EmailCodes.EmailSettingsUpdated
                    )
                    results.message = msg
                    results.data.append(config.to_dict_non_null())

                elif status_code == DbCodes.Skipped:
                    msg = (
                        'Failed to update email settings,' +
                        ' invalid email id passed {0}'.format(config.id)
                    )
                    results.generic_status_code = (
                        GenericFailureCodes.FailedToUpdateObject
                    )
                    results.vfense_status_code = (
                        EmailFailureCodes.FailedToUpdateEmailSettings
                    )
                    results.message = msg
                    results.data.append(config.to_dict())

                else:
                    msg = 'Failed to create email settings.'
                    results.generic_status_code = (
                        GenericFailureCodes.FailedToUpdateObject
                    )
                    results.vfense_status_code = (
                        EmailFailureCodes.FailedToUpdateEmailSettings
                    )
                    results.message = msg
                    results.data.append(config.to_dict_non_null())

            elif not config.id:
                msg = (
                    'Failed to update email settings,' +
                    ' invalid id was passed {0}'
                )
                results.generic_status_code = (
                    GenericFailureCodes.FailedToUpdateObject
                )
                results.vfense_status_code = (
                    EmailFailureCodes.FailedToUpdateEmailSettings
                )
                results.message = msg
                results.errors = invalid_fields
                results.data.append(config.to_dict_non_null())

            else:
                msg = (
                    'Failed to update email settings,' +
                    ' invalid fields were passed'
                )
                results.generic_status_code = (
                    GenericFailureCodes.FailedToCreateObject
                )
                results.vfense_status_code = (
                    EmailFailureCodes.FailedToCreateEmailSettings
                )
                results.message = msg
                results.errors = invalid_fields
                results.data.append(config.to_dict())

        else:
            msg = (
                'Pass a valid NotificationPlugins instance and not a {0}'
                .format(type(config))
            )
            results.generic_status_code = (
                GenericFailureCodes.InvalidInstanceType
            )
            results.vfense_status_code = (
                EmailFailureCodes.FailedToUpdateEmailSettings
            )
            results.message = msg
            results.errors = invalid_fields
            results.data.append(config.to_dict())

        return results


    def delete(self, config_id):
        results = ApiResults()
        results.fill_in_defaults()
        status_code, _, _, generated_ids = (
            delete_email(config_id)
        )
        if status_code == DbCodes.Deleted:
            msg = 'Email settings updated'
            results.generic_status_code = GenericCodes.ObjectDeleted
            results.vfense_status_code = EmailCodes.EmailSettingsDeleted
            results.message = msg

        else:
            msg = (
                'Failed to delete email settings,' +
                ' invalid email id passed {0}'.format(config_id)
            )
            results.generic_status_code = (
                GenericFailureCodes.InvalidId
            )
            results.vfense_status_code = (
                EmailFailureCodes.FailedToDeleteEmailSettings
            )
            results.message = msg

        return results
