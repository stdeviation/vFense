from time import time
from vFense.core.agent._db_model import AgentKeys
from vFense.core.agent._constants import (
    AgentDefaults
)
from vFense.core._db_constants import DbTime
from vFense.core._constants import (
    CommonKeys
)
from vFense.result._constants import ApiResultKeys
from vFense.core.status_codes import GenericCodes


class Agent(object):
    """Used to represent an instance of an agent."""

    def __init__(self, computer_name=None, display_name=None,
                 os_code=None, os_string=None, views=None,
                 needs_reboot=None, agent_status=None,
                 environment=None, machine_type=None,
                 rebooted=None, hardware=None, bit_type=None,
                 version=None, date_added=None, last_agent_update=None,
                 token=None, assign_new_token=False
                 ):
        """
        Kwargs:
            computer_name (str): The computer_name or host_name of the agent.
            display_name (str): The name displayed in the vFense web UI.
            os_code (str): linux, darwin, or windows
            os_string (str): The full name of the os..
                example Ubuntu 12.0.4
            views (list): List of views, this agent is a part of.
            needs_reboot (boolean): Does this agent require a reboot?
            agent_status (str): Is this agent up or down?
                valid_values: ( up, down )
            environment (str): user defined environment.
            machine_type (str): Is this machine physical or virtual?
                valid_values: ( physical, virtual )
            rebooted (bool): Was this agent rebooted?
            hardware (dict): Dictionary of installed devices in the agent.
            bit_type (str): 64 or 32
            version (str): The version of the os_string.
            date_added (epoch_time): time in epoch.
            last_agent_update (epoch_time): time in epoch.
            token (str): Base64 encoded string.
            assign_new_token (bool): Assign this agent a new token.
        """
        self.computer_name = computer_name
        self.display_name = display_name
        self.os_code = os_code
        self.os_string = os_string
        self.views = views
        self.needs_reboot = needs_reboot
        self.agent_status = agent_status
        self.environment = environment
        self.machine_type = machine_type
        self.rebooted = rebooted
        self.hardware = hardware
        self.version = version
        self.bit_type = bit_type
        self.date_added = date_added
        self.last_agent_update = last_agent_update
        self.token = token
        self.assign_new_token = assign_new_token


    def fill_in_defaults(self):
        """Replace all the fields that have None as their value with
        the hardcoded default values.

        Use case(s):
            Useful when adding a new agent instance and only want to fill
            in a few fields, then allow the add agent functions to call this
            method to fill in the rest.
        """

        if not self.needs_reboot:
            self.needs_reboot = AgentDefaults.NEEDS_REBOOT

        if not self.environment:
            self.environment = AgentDefaults.ENVIRONMENT

        if not self.agent_status:
            self.agent_status = AgentDefaults.AGENT_STATUS

        if not self.rebooted:
            self.rebooted = AgentDefaults.REBOOTED

        if not self.views:
            self.views = AgentDefaults.VIEWS

        if not self.display_name:
            self.display_name = AgentDefaults.DISPLAY_NAME

        if not self.date_added:
            self.date_added = time()

        if not self.last_agent_update:
            self.last_agent_update = time()

    def get_invalid_fields(self):
        """Check the agent for any invalid fields.

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

        if self.needs_reboot:
            if not isinstance(self.needs_reboot, bool):
                invalid_fields.append(
                    {
                        AgentKeys.NeedsReboot: self.needs_reboot,
                        CommonKeys.REASON: 'Must be a boolean value',
                        ApiResultKeys.VFENSE_STATUS_CODE: (
                            GenericCodes.InvalidValue
                        )
                    }
                )

        if self.rebooted:
            if not isinstance(self.rebooted, bool):
                invalid_fields.append(
                    {
                        AgentKeys.Rebooted: self.rebooted,
                        CommonKeys.REASON: 'Must be a boolean value',
                        ApiResultKeys.VFENSE_STATUS_CODE: (
                            GenericCodes.InvalidValue
                        )
                    }
                )

        if self.assign_new_token:
            if not isinstance(self.assign_new_token, bool):
                invalid_fields.append(
                    {
                        AgentKeys.AssignNewToken: self.assign_new_token,
                        CommonKeys.REASON: 'Must be a boolean value',
                        ApiResultKeys.VFENSE_STATUS_CODE: (
                            GenericCodes.InvalidValue
                        )
                    }
                )

        if self.last_agent_update:
            if (not isinstance(self.last_agent_update, int) and
                    not isinstance(self.last_agent_update, float)):

                invalid_fields.append(
                    {
                        AgentKeys.LastAgentUpdate: self.last_agent_update,
                        CommonKeys.REASON: (
                            'Must be a integer or a float value'
                        ),
                        ApiResultKeys.VFENSE_STATUS_CODE: (
                            GenericCodes.InvalidValue
                        )
                    }
                )


        return invalid_fields

    def to_dict(self):
        """ Turn the view fields into a dictionary.

        Returns:
            (dict): A dictionary with the fields corresponding to the
                view.

                Ex:
                {
                    "rebooted": true,
                    "hardware": {
                        "nic": [
                            {
                                "mac": "3085A925BFD6",
                                "ip_address": "10.0.0.2",
                                "name": "Local Area Connection"
                            },
                            {
                                "mac": "005056C00001",
                                "ip_address": "192.168.110.1",
                                "name": "VMware Network Adapter VMnet1"
                            },
                            {
                                "mac": "005056C00008",
                                "ip_address": "192.168.252.1",
                                "name": "VMware Network Adapter VMnet8"
                            }
                        ],
                        "display": [
                            {
                                "speed_mhz": "GeForce GTX 660M",
                                "name": "NVIDIA GeForce GTX 660M  ",
                                "ram_kb": 0
                            }
                        ],
                        "storage": [
                            {
                                "free_size_kb": 155600024,
                                "name": "C:",
                                "size_kb": 499872764,
                                "file_system": "NTFS"
                            }
                        ],
                        "cpu": [
                            {
                                "speed_mhz": 2401,
                                "name": "Intel(R) Core(TM) i7-3630QM CPU @ 2.40GHz",
                                "cpu_id": 1,
                                "bit_type": 64,
                                "cache_kb": 1024,
                                "cores": 4
                            }
                        ],
                        "memory": 25165824
                    },
                    "display_name": null,
                    "environment": "Production",
                    "views": [
                        "global"
                    ],
                    "date_added": 1403881567.891592,
                    "last_agent_update": 1403881567.891593,
                    "os_code": "windows",
                    "agent_status": "up",
                    "token": null,
                    "version": "6.1.7601",
                    "bit_type": "64",
                    "computer_name": "DISCIPLINE-1",
                    "os_string": "Windows 7 Professional N",
                    "needs_reboot": false,
                    "assign_new_token": false
                }
        """

        return {
            AgentKeys.ComputerName: self.computer_name,
            AgentKeys.DisplayName: self.display_name,
            AgentKeys.Views: self.views,
            AgentKeys.OsCode: self.os_code,
            AgentKeys.OsString: self.os_string,
            AgentKeys.NeedsReboot: self.needs_reboot,
            AgentKeys.AgentStatus: self.agent_status,
            AgentKeys.Environment: self.environment,
            AgentKeys.Rebooted: self.rebooted,
            AgentKeys.Hardware: self.hardware,
            AgentKeys.BitType: self.bit_type,
            AgentKeys.Version: self.version,
            AgentKeys.DateAdded: self.date_added,
            AgentKeys.LastAgentUpdate: self.last_agent_update,
            AgentKeys.Token: self.token,
            AgentKeys.AssignNewToken: self.assign_new_token,
        }

    def to_dict_non_null(self):
        """ Use to get non None fields of view. Useful when
        filling out just a few fields to update the view in the db.

        Returns:
            (dict): a dictionary with the non None fields of this view.
        """
        agent_dict = self.to_dict()

        return {k:agent_dict[k] for k in agent_dict
                if agent_dict[k] != None}
