from vFense.plugins.patching._constants import (
    InstallDefaults
)

from vFense.plugins.patching.operations._constants import (
    InstallKeys
)
from vFense.core.operations._db_model import AgentOperationKey
from vFense.core._constants import (
    CommonKeys, RebootValues, CPUThrottleValues
)

from vFense.core.results import ApiResultKeys
from vFense.core.status_codes import GenericCodes

class Install(object):
    """Used to represent an instance of an agent."""

    def __init__(self, app_ids=None, agent_ids=None, tag_id=None,
                 user_name=None, view_name=None, restart=None,
                 net_throttle=None, cpu_throttle=None):
        """
        Kwargs:
            app_ids (list): List of application ids.
            agent_ids (list): List of agent ids.
            user_name (str): Name of the user who initiated the install.
            view_name (str): The current view, this install was initiated on.
            tag_id (str): The tag id of the tag you want to install
                applications on.
            restart (str): After installing the application, do you want
                the agent to reboot the host.
                Valid values: none, needed, and force.
                default=none
            cpu_throttle (str): Set the CPU affinity for the install process.
                Valid values: idle, below_normal, normal, above_normal, high.
                default=normal
            net_throttle (str): The amount of traffic in KB to use.
                default=0 (unlimitted)
        """
        self.app_ids = app_ids
        self.agent_ids = agent_ids
        self.tag_id = tag_id
        self.user_name = user_name
        self.view_name = view_name
        self.restart = restart
        self.net_throttle = net_throttle
        self.cpu_throttle = cpu_throttle

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
