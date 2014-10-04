from vFense import Base
from vFense.core._db_constants import DbTime
from vFense.plugins.notifications._db_model import (
    NotificationKeys, NotificationHistoryKeys,
    NotificationPluginKeys
)
from vFense.plugins.notifications._constants import (
    NotifDefaults
)
from vFense.core._constants import (
    CommonKeys
)
from vFense.core.results import ApiResultKeys
from vFense.core.status_codes import GenericCodes


class Notification(Base):
    """Used to represent an instance of an agent."""

    def __init__(self, notification_id=None, notification_type=None,
                 rule_name=None, rule_description=None, created_by=None,
                 created_time=None, modified_by=None, modified_time=None,
                 plugin=None, user=None, group=None, all_agents=False,
                 agents=None, tags=None, view_name=None, threshold=None,
                 file_system=None
                 ):
        """
        Kwargs:
            notification_id (str): The id of the notification rule.
            notification_type (str): The type of notification.
                example..install, uninstall, reboot, shutdown
            rule_name (str): The name of this notifcation rule.
            rule_description (str): Why this rule was created.
            created_by (str): The user who created this rule.
            created_time (float): The time this rule was created.
            modified_by (str): The user who modified this rule.
            modified_time (float): The time this rule was modified.
            plugin (str): Which plugin this is being created for...
                example.. patching, core, vuln.
            user (str): The user that will be notified by this rule.
            group (str): The group that will be notified by this rule.
            all_agents (bool): if this rule applies to all agents.
                default=False
            agents (list): List of agent ids, this rule applies too.
                default=[]
            tags (list): List of tag ids, this rule applies too.
                default=[]
            view_name (str): The name of the view this notification
                rule belongs too.
            threshold (float): the threshold this rule will alert on.
                default=None
            file_system (str): The file_system this rule applies too.
                default=None
        """
        self.notification_id = notification_id
        self.notification_type = notification_type
        self.rule_name = rule_name
        self.rule_description = rule_description
        self.created_by = created_by
        self.created_time = created_time
        self.modified_by = modified_by
        self.modified_time = modified_time
        self.plugin = plugin
        self.user = user
        self.group = group
        self.all_agents = all_agents
        self.agents = agents
        self.tags = tags
        self.view_name = view_name
        self.threshold = threshold
        self.file_system = file_system


    def fill_in_defaults(self):
        """Replace all the fields that have None as their value with
        the hardcoded default values.

        Use case(s):
            Useful when adding a new instance and only want to fill
            in a few fields, then allow the add notifcation functions to call this
            method to fill in the rest.
        """

        if not self.all_agents:
            self.all_agents = NotifDefaults.all_agents()

        if not self.agents:
            self.agents = NotifDefaults.agents()

        if not self.tags:
            self.tags = NotifDefaults.tags()

        if not self.user:
            self.user = NotifDefaults.user()

        if not self.group:
            self.group = NotifDefaults.group()

        if not self.file_system:
            self.file_system = NotifDefaults.file_system()


    def get_invalid_fields(self):
        """Check for any invalid fields.

        Returns:
            (list): List of key/value pair dictionaries corresponding
                to the invalid fields.

                Ex:
                    [
                        {'view_name': 'the invalid name in question'},
                        {'net_throttle': -10}
                    ]
        """
        invalid_fields = []

        if self.agents:
            if not isinstance(self.agents, list):
                invalid_fields.append(
                    {
                        NotificationKeys.Agents: self.agents,
                        CommonKeys.REASON: 'Must be a list',
                        ApiResultKeys.VFENSE_STATUS_CODE: (
                            GenericCodes.InvalidValue
                        )
                    }
                )

        if self.tags:
            if not isinstance(self.tags, list):
                invalid_fields.append(
                    {
                        NotificationKeys.Tags: self.tags,
                        CommonKeys.REASON: 'Must be a list',
                        ApiResultKeys.VFENSE_STATUS_CODE: (
                            GenericCodes.InvalidValue
                        )
                    }
                )

        if not isinstance(self.all_agents, bool):
            invalid_fields.append(
                {
                    NotificationKeys.AllAgents: self.all_agents,
                    CommonKeys.REASON: 'Must be a Bool value',
                    ApiResultKeys.VFENSE_STATUS_CODE: (
                            GenericCodes.InvalidValue
                    )
                }
            )

        if self.created_time:
            if not isinstance(self.created_time, float):
                invalid_fields.append(
                    {
                        NotificationKeys.CreatedTime: self.created_time,
                        CommonKeys.REASON: 'Must be a float',
                        ApiResultKeys.VFENSE_STATUS_CODE: (
                            GenericCodes.InvalidValue
                        )
                    }
                )

        if self.modified_time:
            if not isinstance(self.modified_time, float):
                invalid_fields.append(
                    {
                        NotificationKeys.ModifiedTime: self.modified_time,
                        CommonKeys.REASON: 'Must be a float',
                        ApiResultKeys.VFENSE_STATUS_CODE: (
                            GenericCodes.InvalidValue
                        )
                    }
                )

        if self.threshold:
            if not isinstance(self.threshold, float):
                invalid_fields.append(
                    {
                        NotificationKeys.Threshold: self.Threshold,
                        CommonKeys.REASON: 'Must be a float',
                        ApiResultKeys.VFENSE_STATUS_CODE: (
                            GenericCodes.InvalidValue
                        )
                    }
                )

        return invalid_fields

    def to_dict(self):
        """ Turn the view fields into a dictionary."""

        return {
            NotificationKeys.NotificationId: self.notification_id,
            NotificationKeys.NotificationType: self.notification_type,
            NotificationKeys.RuleName: self.rule_name,
            NotificationKeys.RuleDescription: self.rule_description,
            NotificationKeys.CreatedBy: self.created_by,
            NotificationKeys.CreatedTime: self.created_time,
            NotificationKeys.ModifiedBy: self.modified_by,
            NotificationKeys.ModifiedTime: self.modified_time,
            NotificationKeys.Plugin: self.plugin,
            NotificationKeys.User: self.user,
            NotificationKeys.Group: self.group,
            NotificationKeys.AllAgents: self.all_agents,
            NotificationKeys.Agents: self.agents,
            NotificationKeys.Tags: self.tags,
            NotificationKeys.ViewName: self.view_name,
            NotificationKeys.Threshold: self.threshold,
            NotificationKeys.FileSystem: self.file_system,
        }


    def to_dict_db(self):
        """ Turn the fields into a dictionary, with db related fields.

        Returns:
            (dict): A dictionary with the fields.

        """

        data = {
            NotificationPluginKeys.CreatedTime: (
                DbTime.epoch_time_to_db_time(self.created_time)
            ),
            NotificationPluginKeys.ModifiedTime: (
                DbTime.epoch_time_to_db_time(self.modified_time)
            ),
        }

        combined_data = dict(self.to_dict().items() + data.items())
        combined_data.pop(NotificationKeys.NotificationId)
        return combined_data

    def to_dict_db_update(self):
        """ Turn the fields into a dictionary, with db related fields.

        Returns:
            (dict): A dictionary with the fields.

        """

        data = {
            NotificationPluginKeys.ModifiedTime: (
                DbTime.epoch_time_to_db_time(self.modified_time)
            ),
        }

        combined_data = dict(self.to_dict_non_null().items() + data.items())
        combined_data.pop(NotificationKeys.NotificationId)
        return combined_data


class NotificationHistory(Base):
    """Used to represent an instance of an agent."""

    def __init__(self, notification_id=None, id=None, alert_sent=None,
                 alert_sent_time=None
                 ):
        """
        Kwargs:
            id (str): The id of this historical notification trigger.
            notification_id (str): The id of the notification rule.
            alert_sent (bool): If this alert was sent: True or False
            alert_sent_time (float): The unix timestamp of when this alert
                was sent. defaut = 0.0
        """
        self.id = id
        self.notification_id = notification_id
        self.alert_sent = alert_sent
        self.alert_sent_time = alert_sent_time


    def fill_in_defaults(self):
        """Replace all the fields that have None as their value with
        the hardcoded default values.

        Use case(s):
            Useful when adding a new instance and only want to fill
            in a few fields, then allow the add notifcation functions to call this
            method to fill in the rest.
        """

        pass


    def get_invalid_fields(self):
        """Check for any invalid fields.

        Returns:
            (list): List of key/value pair dictionaries corresponding
                to the invalid fields.

                Ex:
                    [
                        {'view_name': 'the invalid name in question'},
                        {'net_throttle': -10}
                    ]
        """
        invalid_fields = []

        if self.alert_sent:
            if not isinstance(self.alert_sent, bool):
                invalid_fields.append(
                    {
                        NotificationHistoryKeys.AlertSent: self.alert_sent,
                        CommonKeys.REASON: 'Must be a bool',
                        ApiResultKeys.VFENSE_STATUS_CODE: (
                            GenericCodes.InvalidValue
                        )
                    }
                )

        if self.alert_sent_time:
            if not isinstance(self.alert_sent_time, float):
                invalid_fields.append(
                    {
                        NotificationHistoryKeys.AlertSentTime: (
                            self.alert_sent_time
                        ),
                        CommonKeys.REASON: 'Must be a float',
                        ApiResultKeys.VFENSE_STATUS_CODE: (
                            GenericCodes.InvalidValue
                        )
                    }
                )

        return invalid_fields

    def to_dict(self):
        """ Turn the view fields into a dictionary."""

        return {
            NotificationHistoryKeys.Id: self.id,
            NotificationHistoryKeys.NotificationId: self.notification_id,
            NotificationHistoryKeys.AlertSent: self.alert_sent,
            NotificationHistoryKeys.AlertSentTime: self.alert_sent_time,
        }

    def to_dict_db(self):
        """ Turn the fields into a dictionary, with db related fields.

        Returns:
            (dict): A dictionary with the fields.

        """

        data = {
            NotificationHistoryKeys.AlertSentTime: (
                DbTime.epoch_time_to_db_time(self.alert_sent_time)
            ),
        }

        combined_data = dict(self.to_dict_non_null().items() + data.items())
        combined_data.pop(NotificationHistoryKeys.Id)

        return dict(self.to_dict().items() + data.items())

