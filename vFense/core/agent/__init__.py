from time import time
from vFense import Base
from vFense.core._db_constants import DbTime
from vFense.core.agent._db_model import AgentKeys
from vFense.core.agent._constants import (
    AgentDefaults
)
from vFense.core._constants import (
    CommonKeys
)
from vFense.core.results import ApiResultKeys
from vFense.core.status_codes import GenericCodes


class Agent(Base):
    """Used to represent an instance of an agent."""

    def __init__(self, agent_id=None, computer_name=None, display_name=None,
                 os_code=None, os_string=None, views=None,
                 needs_reboot=None, agent_status=None,
                 environment=None, machine_type=None,
                 rebooted=None, hardware=None, bit_type=None,
                 version=None, date_added=None, last_agent_update=None,
                 token=None, assign_new_token=False, tags=None, enabled=True,
                 **kwargs
                 ):
        """
        Kwargs:
            agent_id (str): The id of the agent.
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
            tags (list): List of tags, this agent is a part of.
            enabled (bool): True or False
        """
        super(Agent, self).__init__(**kwargs)
        self.agent_id = agent_id
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
        self.tags = tags
        self.enabled = enabled


    def fill_in_defaults(self):
        """Replace all the fields that have None as their value with
        the hardcoded default values.
        """
        now = time()

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

        if not self.tags:
            self.tags = AgentDefaults.TAGS

        if not self.display_name:
            self.display_name = AgentDefaults.DISPLAY_NAME

        if not self.date_added:
            self.date_added = now

        if not self.last_agent_update:
            self.last_agent_update = now

        if not self.enabled:
            self.enabled = True

    def get_invalid_fields(self):
        """Check for any invalid fields.
        Returns:
            (list): List of invalid fields
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
        """ Turn the fields into a dictionary.

        Returns:
            (dict): A dictionary with the fields.
        """

        return {
            AgentKeys.ComputerName: self.computer_name,
            AgentKeys.DisplayName: self.display_name,
            AgentKeys.Views: self.views,
            AgentKeys.Tags: self.tags,
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

    def to_dict_db(self):
        """ Turn the fields into a dictionary, with db related fields.

        Returns:
            (dict): A dictionary with the fields.

        """

        data = {
            AgentKeys.DateAdded: (
                DbTime.epoch_time_to_db_time(self.date_added)
            ),
            AgentKeys.LastAgentUpdate: (
                DbTime.epoch_time_to_db_time(self.last_agent_update)
            ),
        }

        combined_data = dict(self.to_dict_non_null().items() + data.items())
        combined_data.pop(AgentKeys.AgentId, None)
        return combined_data

    def to_dict_db_update(self):
        """ Turn the fields into a dictionary, with db related fields.

        Returns:
            (dict): A dictionary with the fields.

        """

        data = {
            AgentKeys.LastAgentUpdate: (
                DbTime.epoch_time_to_db_time(self.last_agent_update)
            ),
        }

        combined_data = dict(self.to_dict_non_null().items() + data.items())
        combined_data.pop(AgentKeys.AgentId, None)
        return combined_data
