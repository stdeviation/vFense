import logging, logging.config
from vFense import VFENSE_LOGGING_CONFIG
from vFense.db.client import db_create_close, r
from vFense.plugins.patching._db_model import (
    DbCommonAppIndexes, DbCommonAppKeys, DbCommonAppPerAgentKeys,
    DbCommonAppPerAgentIndexes, AppCollections, FileCollections,
    FilesIndexes, FilesKey
)
from vFense.core._db import (
    retrieve_collections, create_collection, retrieve_indexes
)

from vFense.plugins.patching.status_codes import (
    PackageCodes, PackageFailureCodes
)

logging.config.fileConfig(VFENSE_LOGGING_CONFIG)
logger = logging.getLogger('rvapi')

class Apps(object):
    """Used to represent an instance of an app."""

    def __init__(self, name=None, version=None, md5=None, arch=None,
                 app_id=None, size=None, kb=None, support_url=None,
                 severity=None, os_code=None, os_string=None, vendor=None,
                 description=None, cli_options=None, release_date=None,
                 reboot_required=None):
        """
        Kwargs:
            name (str): Name of the application.
            version (str): Current version of the application.
            md5 (str): The md5sum of this application.
            arch (int): 64 or 32.
            app_id (str): The primary key of this application.
            size (int): The size of the application in kb.
            support_url (str): The vendor supplied url.
            severity (str): Optional, Recommended, or Critical
            os_code (str): windows, linux, or darwin
            os_string (str): CentOS 6.5, Ubuntu 12.0.4, etc...
            vendor (str): The vendor, this application belongs too.
            description (str): The description of this application.
            cli_options (str): Options to be passed while installing this
                application.
            release_date (float): The Unix timestamp aka epoch time.
            reboot_required (str): possible, required, none
        """
        self.name = name
        self.version = version
        self.md5 = md5
        self.arch = arch
        self.app_id = app_id
        self.size = size
        self.kb = kb
        self.support_url = support_url
        self.severity = severity
        self.os_code = os_code
        self.os_string = os_string
        self.vendor = vendor
        self.description = description
        self.cli_options = cli_options
        self.release_date = release_date
        self.reboot_required = reboot_required

    def fill_in_defaults(self):
        """Replace all the fields that have None as their value with
        the hardcoded default values.

        Use case(s):
            Useful when you want to create an install instance and only
            want to fill in a few fields, then allow the install
            functions to call this method to fill in the rest.
        """

        if not self.restart:
            self.restart = InstallDefaults.REBOOT

        if not self.cpu_throttle:
            self.cpu_throttle= InstallDefaults.CPU_THROTTLE

        if not self.net_throttle:
            self.net_throttle = InstallDefaults.NET_THROTTLE


    def get_invalid_fields(self):
        """Check the install for any invalid fields.

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

        if self.restart:
            if self.restart not in RebootValues().VALID_VALUES:
                invalid_fields.append(
                    {
                        AgentOperationKey.Restart: self.restart,
                        CommonKeys.REASON: (
                            '{0} not a valid reboot value'
                            .format(self.restart)
                        ),
                        ApiResultKeys.VFENSE_STATUS_CODE: (
                            GenericCodes.InvalidValue
                        )
                    }
                )

        if self.cpu_throttle:
            if self.cpu_throttle not in CPUThrottleValues.VALID_VALUES:
                invalid_fields.append(
                    {
                        AgentOperationKey.CpuThrottle: self.cpu_throttle,
                        CommonKeys.REASON: (
                            '{0} not a valid cpu throttle'
                            .format(self.cpu_throttle)
                        ),
                        ApiResultKeys.VFENSE_STATUS_CODE: (
                            GenericCodes.InvalidValue
                        )
                    }
                )

        if self.net_throttle:
            if not isinstance(self.net_throttle, int):
                invalid_fields.append(
                    {
                        AgentOperationKey.NetThrottle: self.net_throttle,
                        CommonKeys.REASON: 'Must be a integer value',
                        ApiResultKeys.VFENSE_STATUS_CODE: (
                            GenericCodes.InvalidValue
                        )
                    }
                )

        if self.agent_ids:
            if not isinstance(self.agent_ids, list):
                invalid_fields.append(
                    {
                        AgentOperationKey.agent_ids: self.agent_ids,
                        CommonKeys.REASON: (
                            'Must be a list of agent ids'
                        ),
                        ApiResultKeys.VFENSE_STATUS_CODE: (
                            GenericCodes.InvalidValue
                        )
                    }
                )

        if self.app_ids:
            if not isinstance(self.app_ids, list):
                invalid_fields.append(
                    {
                        AgentOperationKey.app_ids: self.app_ids,
                        CommonKeys.REASON: (
                            'Must be a list of app ids'
                        ),
                        ApiResultKeys.VFENSE_STATUS_CODE: (
                            GenericCodes.InvalidValue
                        )
                    }
                )


        if self.tag_id:
            if not isinstance(self.tag_id, basestring):
                invalid_fields.append(
                    {
                        AgentOperationKey.tag_id: self.tag_id,
                        CommonKeys.REASON: (
                            'Must be a string'
                        ),
                        ApiResultKeys.VFENSE_STATUS_CODE: (
                            GenericCodes.InvalidValue
                        )
                    }
                )

        return invalid_fields

    def args_to_dict(self):
        """ Turn the view fields into a dictionary.

        Returns:
            (dict): A dictionary with the fields corresponding to the
                install operation.

        """

        return {
            InstallKeys.AGENT_IDS: self.agent_ids,
            InstallKeys.APP_IDS: self.app_ids,
            InstallKeys.NET_THROTTLE: self.net_throttle,
            InstallKeys.CPU_THROTTLE: self.cpu_throttle,
            InstallKeys.RESTART: self.cpu_throttle,
        }


    def to_dict(self):
        """ Turn the view fields into a dictionary.

        Returns:
            (dict): A dictionary with the fields corresponding to the
                install operation.

        """

        return {
            InstallKeys.AGENT_IDS: self.agent_ids,
            InstallKeys.APP_IDS: self.app_ids,
            InstallKeys.NET_THROTTLE: self.net_throttle,
            InstallKeys.CPU_THROTTLE: self.cpu_throttle,
            InstallKeys.RESTART: self.cpu_throttle,
            InstallKeys.USER_NAME: self.user_name,
            InstallKeys.VIEW_NAME: self.view_name
        }

    def to_dict_non_null(self):
        """ Use to get non None fields of an install. Useful when
        filling out just a few fields to perform an install.

        Returns:
            (dict): a dictionary with the non None fields of this install.
        """
        install_dict = self.to_dict()

        return {k:install_dict[k] for k in install_dict
                if install_dict[k] != None}
