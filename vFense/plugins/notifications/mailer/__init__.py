from time import time
from vFense import Base
from vFense.core._db_constants import DbTime
from vFense.plugins.notifications._db_model import (
    NotificationPluginKeys
)
from vFense.core._constants import (
    CommonKeys
)
from vFense.core.results import ApiResultKeys
from vFense.core.status_codes import GenericCodes



class NotificationPlugin(Base):
    """Used to represent an instance of a notification plugin."""

    def __init__(self, id=None, view_name=None, plugin_name=None,
                 created_by=None, created_time=None, modified_by=None,
                 modified_time=None, username=None, password=None,
                 server=None, port=None, is_tls=False, is_ssl=False,
                 from_email=None, to_email=None
                 ):
        """
        Kwargs:
            id (str): The id of this notification plugin.
            view_name (str): The view this notification plugin belongs too.
            plugin_name (str): The name of this plugin.
            created_by (str): The user who created this plugin.
            created_time (float): The time this plugin was created.
            modified_by (str): The user who modified this plugin.
            modified_time (float): The time this plugin was modified.
            username (str): The user you wish to authenticate with.
            password (str): The password to be used in conjunction with the
                username.
            server (str): The ip address or host name of the email server.
            port (int): The port that will be used while sending an email.
            is_tls (bool): Use tls. default=False
            is_ssl (bool): Use ssl. default=False
            from_email (str): The email address this email is coming from.
                default=None
            to_email (str): The default sending email address to use.
                default=None
        """
        self.id = id
        self.view_name = view_name
        self.plugin_name = plugin_name
        self.created_by = created_by
        self.created_time = created_time
        self.modified_by = modified_by
        self.modified_time = modified_time
        self.username = username
        self.password = password
        self.server = server
        self.port = port
        self.is_tls = is_tls
        self.is_ssl = is_ssl
        self.from_email = from_email
        self.to_email = to_email


    def fill_in_defaults(self):
        """Replace all the fields that have None as their value with
        the hardcoded default values.

        Use case(s):
            Useful when adding a new instance and only want to fill
            in a few fields, then allow the add notifcation functions to call this
            method to fill in the rest.
        """
        now = time()

        if not self.created_time:
            self.created_time = now

        if not self.modified_time:
            self.modified_time = now


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

        if self.is_tls:
            if not isinstance(self.is_tls, bool):
                invalid_fields.append(
                    {
                        NotificationPluginKeys.IsTls: self.is_tls,
                        CommonKeys.REASON: 'Must be a bool',
                        ApiResultKeys.VFENSE_STATUS_CODE: (
                            GenericCodes.InvalidValue
                        )
                    }
                )

        if self.is_ssl:
            if not isinstance(self.is_ssl, bool):
                invalid_fields.append(
                    {
                        NotificationPluginKeys.IsSsl: self.is_ssl,
                        CommonKeys.REASON: 'Must be a bool',
                        ApiResultKeys.VFENSE_STATUS_CODE: (
                            GenericCodes.InvalidValue
                        )
                    }
                )

        if self.created_time:
            if not isinstance(self.created_time, float):
                invalid_fields.append(
                    {
                        NotificationHistoryKeys.CreatedTime: (
                            self.created_time
                        ),
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
                        NotificationHistoryKeys.ModifiedTime: (
                            self.modified_time
                        ),
                        CommonKeys.REASON: 'Must be a float',
                        ApiResultKeys.VFENSE_STATUS_CODE: (
                            GenericCodes.InvalidValue
                        )
                    }
                )

        if self.port:
            if not isinstance(self.port, int):
                invalid_fields.append(
                    {
                        NotificationHistoryKeys.Port: (
                            self.port
                        ),
                        CommonKeys.REASON: 'Must be a int',
                        ApiResultKeys.VFENSE_STATUS_CODE: (
                            GenericCodes.InvalidValue
                        )
                    }
                )

        return invalid_fields

    def to_dict(self):
        """ Turn the view fields into a dictionary."""

        return {
            NotificationPluginKeys.Id: self.id,
            NotificationPluginKeys.ViewName: self.view_name,
            NotificationPluginKeys.PluginName: self.plugin_name,
            NotificationPluginKeys.CreatedTime: self.created_time,
            NotificationPluginKeys.CreatedBy: self.created_by,
            NotificationPluginKeys.ModifiedTime: self.modified_time,
            NotificationPluginKeys.ModifiedBy: self.modified_by,
            NotificationPluginKeys.UserName: self.username,
            NotificationPluginKeys.Password: self.password,
            NotificationPluginKeys.Server: self.server,
            NotificationPluginKeys.Port: self.port,
            NotificationPluginKeys.IsTls: self.is_tls,
            NotificationPluginKeys.IsSsl: self.is_ssl,
            NotificationPluginKeys.FromEmail: self.from_email,
            NotificationPluginKeys.ToEmail: self.to_email,
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

        combined_data = dict(self.to_dict_non_null().items() + data.items())
        combined_data.pop(NotificationPluginKeys.Id)

        return dict(self.to_dict().items() + data.items())

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
        combined_data.pop(NotificationPluginKeys.Id)

        return dict(self.to_dict().items() + data.items())
