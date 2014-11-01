import re
import logging
from time import time
from vFense import Base
from vFense._constants import VFENSE_LOGGING_CONFIG
from vFense.core._db_constants import DbTime

from vFense.core._constants import (
    CPUThrottleValues, DefaultStringLength, RegexPattern, CommonKeys
)

from vFense.core.view._db_model import ViewKeys
from vFense.core.view._constants import ViewDefaults
from vFense.core.results import ApiResultKeys

from vFense.core.view.status_codes import ViewFailureCodes
from pytz import all_timezones

logging.config.fileConfig(VFENSE_LOGGING_CONFIG)
logger = logging.getLogger('rvapi')


class View(Base):
    """Used to represent an instance of a view."""

    def __init__(
        self, view_name=None, parent=None, ancestors=None, children=None,
        users=None, net_throttle=None, cpu_throttle=None,
        server_queue_ttl=None, agent_queue_ttl=None,
        package_download_url_base=None, token=None, previous_tokens=None,
        time_zone=None, date_added=None, date_modified=None, **kwargs
    ):
        """
        Kwargs:
            view_name (str): The name of this view.
            parent (str): The parent of this view.
            ancestors (list): The ancestors of this view in
                the correct order.
            children (list): The child views of this view in
                the correct order.
            users (list): List of users that have access to this view.
            net_throttle (int): The default net throttling for downloading
                packages for agents in this view, in KB/s.
            cpu_throttle (str): The default cpu throttling for operations
                in this view. Has to be a valid cpu throttling keyword.
                    valid: ['idle', 'below_normal', 'normal', 'above_normal', 'high']
            server_queue_ttl (int): The default time an operation will sit
                on the server queue, in minutes. Must be above 0.
            agent_queue_ttl (int): The default time an operation will sit
                on the agent queue, in minutes. Must be above 0.
            package_download_url_base (str): The base url used to construct the
                urls where the packages will be downloaded from.
                    Ex:
                        'https://192.168.1.1/packages/'
            token (str): Base64 encoded string.
            previous_tokens (list): List of previous base64 encoded strings.
            time_zone (str): The timezone you want your scheduler to run as.
            date_added (epoch_time): time in epoch.
            date_modified (epoch_time): time in epoch.
        """
        super(View, self).__init__(**kwargs)
        self.view_name = view_name
        self.parent = parent
        self.ancestors = ancestors
        self.children = children
        self.users = users
        self.net_throttle = net_throttle
        self.cpu_throttle = cpu_throttle
        self.server_queue_ttl = server_queue_ttl
        self.agent_queue_ttl = agent_queue_ttl
        self.package_download_url_base = package_download_url_base
        self.token = token
        self.previous_tokens = previous_tokens
        self.time_zone = time_zone
        self.date_added = date_added
        self.date_modified = date_modified

    def fill_in_defaults(self):
        """Replace all the fields that have None as their value with
        the hardcoded default values.
        """
        now = time()

        if not self.parent:
            self.parent = ViewDefaults.PARENT

        if not self.ancestors:
            self.ancestors = ViewDefaults.ANCESTORS

        if not self.children:
            self.children = ViewDefaults.CHILDREN

        if not self.users:
            self.users = ViewDefaults.USERS

        if not self.net_throttle:
            self.net_throttle = ViewDefaults.NET_THROTTLE

        if not self.cpu_throttle:
            self.cpu_throttle = ViewDefaults.CPU_THROTTLE

        if not self.server_queue_ttl:
            self.server_queue_ttl = ViewDefaults.SERVER_QUEUE_TTL

        if not self.agent_queue_ttl:
            self.agent_queue_ttl = ViewDefaults.AGENT_QUEUE_TTL

        if not self.token:
            self.token = ViewDefaults.TOKEN

        if not self.previous_tokens:
            self.previous_tokens = ViewDefaults.PREVIOUS_TOKENS

        if not self.time_zone:
            self.time_zone = ViewDefaults.TIME_ZONE

        if not self.date_added:
            self.date_added = now

        if not self.date_modified:
            self.date_modified = now

    def get_invalid_fields(self):
        """Check for invalid fields.
        """
        invalid_fields = []

        if isinstance(self.view_name, basestring):
            valid_symbols = re.search(
               RegexPattern.VIEW_NAME, self.view_name
            )
            valid_length = len(self.view_name) <= DefaultStringLength.VIEW_NAME

            if not valid_symbols and valid_length:
                invalid_fields.append(
                    {
                        ViewKeys.ViewName: self.view_name,
                        CommonKeys.REASON: (
                            'View name contains invalid special characters.'
                        ),
                        ApiResultKeys.VFENSE_STATUS_CODE: (
                            ViewFailureCodes.InvalidViewName
                        )
                    }
                )

            elif valid_symbols and not valid_length:
                invalid_fields.append(
                    {
                        ViewKeys.ViewName: self.view_name,
                        CommonKeys.REASON: (
                            'View name is too long.'
                        ),
                        ApiResultKeys.VFENSE_STATUS_CODE: (
                            ViewFailureCodes.InvalidViewName
                        )
                    }
                )
            elif not valid_symbols and not valid_length:
                invalid_fields.append(
                    {
                        ViewKeys.ViewName: self.view_name,
                        CommonKeys.REASON: (
                            'View name contains invalid special characters ' +
                            'and the name is too long'
                        ),
                        ApiResultKeys.VFENSE_STATUS_CODE: (
                            ViewFailureCodes.InvalidViewName
                        )
                    }
                )
        else:
            invalid_fields.append(
                {
                    ViewKeys.ViewName: self.view_name,
                    CommonKeys.REASON: 'View name is not a valid string',
                    ApiResultKeys.VFENSE_STATUS_CODE: (
                        ViewFailureCodes.InvalidViewName
                    )
                }
            )

        if self.net_throttle:
            if isinstance(self.net_throttle, int):
                if self.net_throttle < 0:
                    invalid_fields.append(
                        {
                            ViewKeys.NetThrottle: self.net_throttle,
                            CommonKeys.REASON: 'Value is below 0',
                            ApiResultKeys.VFENSE_STATUS_CODE: (
                                ViewFailureCodes.InvalidNetworkThrottle
                            )
                        }
                    )
            else:
                try:
                    self.net_throttle = int(self.net_throttle)

                except Exception as e:
                    logger.exception(e)
                    invalid_fields.append(
                        {
                            ViewKeys.NetThrottle: self.net_throttle,
                            CommonKeys.REASON: 'Invalid value',
                            ApiResultKeys.VFENSE_STATUS_CODE: (
                                ViewFailureCodes.InvalidNetworkThrottle
                            )
                        }
                    )

        if self.cpu_throttle:
            if self.cpu_throttle not in CPUThrottleValues.VALID_VALUES:
                invalid_fields.append(
                    {
                        ViewKeys.CpuThrottle: self.cpu_throttle,
                        CommonKeys.REASON: 'Invalid value',
                        ApiResultKeys.VFENSE_STATUS_CODE: (
                            ViewFailureCodes.InvalidCpuThrottle
                        )
                    }
                )

        if self.server_queue_ttl:
            if isinstance(self.server_queue_ttl, int):
                if self.server_queue_ttl <= 0:
                    invalid_fields.append(
                        {
                            ViewKeys.ServerQueueTTL: self.server_queue_ttl,
                            CommonKeys.REASON: 'Value is less than 1',
                            ApiResultKeys.VFENSE_STATUS_CODE: (
                                ViewFailureCodes.InvalidServerQueueThrottle
                            )
                        }
                    )
            else:
                try:
                    self.server_queue_ttl = int(self.server_queue_ttl)

                except Exception as e:
                    logger.exception(e)
                    invalid_fields.append(
                        {
                            ViewKeys.ServerQueueTTL: self.server_queue_ttl,
                            CommonKeys.REASON: 'Invalid value',
                            ApiResultKeys.VFENSE_STATUS_CODE: (
                                ViewFailureCodes.InvalidServerQueueThrottle
                            )
                        }
                    )

        if self.agent_queue_ttl:
            if isinstance(self.agent_queue_ttl, int):
                if self.agent_queue_ttl <= 0:
                    invalid_fields.append(
                        {
                            ViewKeys.AgentQueueTTL: self.agent_queue_ttl,
                            CommonKeys.REASON: 'Value is less than 1',
                            ApiResultKeys.VFENSE_STATUS_CODE: (
                                ViewFailureCodes.InvalidAgentQueueThrottle
                            )
                        }
                    )
            else:
                try:
                    self.agent_queue_ttl = int(self.agent_queue_ttl)

                except Exception as e:
                    logger.exception(e)
                    invalid_fields.append(
                        {
                            ViewKeys.AgentQueueTTL: self.agent_queue_ttl,
                            CommonKeys.REASON: 'Invalid value',
                            ApiResultKeys.VFENSE_STATUS_CODE: (
                                ViewFailureCodes.InvalidAgentQueueThrottle
                            )
                        }
                    )

        if self.time_zone:
            if self.time_zone not in all_timezones:
                invalid_fields.append(
                    {
                        ViewKeys.TimeZone: self.time_zone,
                        CommonKeys.REASON: 'Invalid value',
                        ApiResultKeys.VFENSE_STATUS_CODE: (
                            ViewFailureCodes.InvalidTimeZone
                        )
                    }
                )


        # TODO: check for invalid package url

        return invalid_fields

    def to_dict(self):
        """ Turn the view fields into a dictionary.

        Returns:
            (dict): A dictionary with the fields.

        """

        return {
            ViewKeys.ViewName: self.view_name,
            ViewKeys.Parent: self.parent,
            ViewKeys.Ancestors: self.ancestors,
            ViewKeys.Children: self.children,
            ViewKeys.NetThrottle: self.net_throttle,
            ViewKeys.CpuThrottle: self.cpu_throttle,
            ViewKeys.ServerQueueTTL: self.server_queue_ttl,
            ViewKeys.AgentQueueTTL: self.agent_queue_ttl,
            ViewKeys.Users: self.users,
            ViewKeys.PackageUrl: self.package_download_url_base,
            ViewKeys.Token: self.token,
            ViewKeys.PreviousTokens: self.previous_tokens,
            ViewKeys.TimeZone: self.time_zone,
            ViewKeys.DateAdded: self.date_added,
            ViewKeys.DateModified: self.date_modified,
        }

    def to_dict_db(self):
        """ Turn the fields into a dictionary, with db related fields.

        Returns:
            (dict): A dictionary with the fields.

        """

        data = {
            ViewKeys.DateAdded: (
                DbTime.epoch_time_to_db_time(self.date_added)
            ),
            ViewKeys.DateModified: (
                DbTime.epoch_time_to_db_time(self.date_modified)
            ),
        }

        combined_data = dict(self.to_dict_non_null().items() + data.items())
        return combined_data

    def to_dict_db_update(self):
        """ Turn the fields into a dictionary, with db related fields.

        Returns:
            (dict): A dictionary with the fields.

        """
        if not self.date_modified:
            self.date_modified = time()

        data = {
            ViewKeys.DateModified: (
                DbTime.epoch_time_to_db_time(self.date_modified)
            ),
        }

        combined_data = dict(self.to_dict_non_null().items() + data.items())
        combined_data.pop(ViewKeys.ViewName, None)
        return combined_data
