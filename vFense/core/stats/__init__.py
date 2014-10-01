import re
from vFense.core.stats._db_model import (
    CpuStatKeys, AgentStatKeys, MemoryStatKeys
)
from vFense.core.agent._constants import (
    agent_regex
)
from vFense.core._constants import (
    CommonKeys
)
from vFense.core.results import ApiResultKeys
from vFense.core.status_codes import GenericCodes


class Stats(object):
    """Used to represent an instance of an agent."""

    def __init__(self, agent_id=None, stat_type=None):
        """
        Kwargs:
            agent_id (str): The id of the agent.
            stat_type (str): The type of the stat.
        """
        self.agent_id = agent_id
        self.stat_type = stat_type


    def fill_in_defaults(self):
        """Replace all the fields that have None as their value with
        the hardcoded default values.

        Use case(s):
            Useful when adding a new agent instance and only want to fill
            in a few fields, then allow the add agent functions to call this
            method to fill in the rest.
        """

        pass

    def get_invalid_fields(self):
        """Check the agent for any invalid fields.

        """
        invalid_fields = []

        if self.agent_id:
            if not isinstance(self.agent_id, str):
                invalid_fields.append(
                    {
                        AgentStatKeys.AgentId: self.agent_id,
                        CommonKeys.REASON: 'Must be a String',
                        ApiResultKeys.VFENSE_STATUS_CODE: (
                            GenericCodes.InvalidValue
                        )
                    }
                )

            elif not re.search(agent_regex(), self.agent_id):
                invalid_fields.append(
                    {
                        AgentStatKeys.AgentId: self.agent_id,
                        CommonKeys.REASON: 'Not a valid agent id',
                        ApiResultKeys.VFENSE_STATUS_CODE: (
                            GenericCodes.InvalidValue
                        )
                    }
                )

        return invalid_fields

    def to_dict(self):
        """ Turn the fields into a dictionary."""
        data = {
            AgentStatKeys.AgentId: self.agent_id,
            AgentStatKeys.StatType: self.stat_type
        }

        return data

    def to_dict_non_null(self):
        """ Use to get non None fields. Useful when
        filling out just a few fields to update the db.

        Returns:
            (dict): a dictionary with the non None fields of this view.
        """
        agent_dict = self.to_dict()

        return {k:agent_dict[k] for k in agent_dict
                if agent_dict[k] != None}

class CPUStats(Stats):
    def __init__(self, idle=None, user=None, system=None, iowait=None, **kwargs):
        super(CPUStats, self).__init__(**kwargs)
        """
        Kwargs:
            idle (float): Percent of cpu that is idle.
            user (float): Percent of cpu being used by the user.
            system (float): Percent of cpu being used by the system.
            iowait (float): Percent of cpu waiting.
            agent_id (str): The id of the agent.
            stat_type (str): The type of the stat.
        """
        self.agent_id = kwargs.get('agent_id')
        self.stat_type = kwargs.get('stat_type')
        self.idle = kwargs.get('idle')
        self.user = kwargs.get('user')
        self.system = kwargs.get('system')
        self.iowait = kwargs.get('iowait')



    def get_invalid_fields(self):
        """Check the agent for any invalid fields.

        """
        invalid_fields = super(CPUStats, self).get_invalid_fields()

        if self.idle:
            if not isinstance(self.idle, float):
                invalid_fields.append(
                    {
                        CpuStatKeys.Idle: self.idle,
                        CommonKeys.REASON: 'Must be a float',
                        ApiResultKeys.VFENSE_STATUS_CODE: (
                            GenericCodes.InvalidValue
                        )
                    }
                )

        if self.user:
            if not isinstance(self.user, float):
                invalid_fields.append(
                    {
                        CpuStatKeys.User: self.user,
                        CommonKeys.REASON: 'Must be a float',
                        ApiResultKeys.VFENSE_STATUS_CODE: (
                            GenericCodes.InvalidValue
                        )
                    }
                )

        if self.system:
            if not isinstance(self.system, float):
                invalid_fields.append(
                    {
                        CpuStatKeys.System: self.system,
                        CommonKeys.REASON: 'Must be a float',
                        ApiResultKeys.VFENSE_STATUS_CODE: (
                            GenericCodes.InvalidValue
                        )
                    }
                )

        if self.iowait:
            if not isinstance(self.iowait, float):
                invalid_fields.append(
                    {
                        CpuStatKeys.IOWait: self.iowait,
                        CommonKeys.REASON: 'Must be a float',
                        ApiResultKeys.VFENSE_STATUS_CODE: (
                            GenericCodes.InvalidValue
                        )
                    }
                )

        return invalid_fields

    def to_dict(self):
        inherited_data = super(CPUStats, self).to_dict()
        data = {
            CpuStatKeys.Idle: self.idle,
            CpuStatKeys.System: self.system,
            CpuStatKeys.User: self.user,
            CpuStatKeys.IOWait: self.iowait,
        }
        return dict(data.items() + inherited_data.items())

class MemoryStats(Stats):
    def __init__(self, used_percent=None, free_percent=None,
                 used=None, free=None, **kwargs):
        super(MemoryStats, self).__init__(**kwargs)
        """
        Kwargs:
            used_percent (float): Percent of memory being used.
            free_percent (float): Percent of free memory.
            used (float): Kilobytes used.
            free (float): kilobytes free.
        """
        self.used_percent = kwargs.get('used_percent')
        self.free_percent = kwargs.get('free_percent')
        self.used = kwargs.get('used')
        self.free = kwargs.get('free')



    def get_invalid_fields(self):
        """Check the agent for any invalid fields.

        """
        invalid_fields = super(CPUStats, self).get_invalid_fields()

        if self.used_percent:
            if not isinstance(self.used_percent, float):
                invalid_fields.append(
                    {
                        MemoryStatKeys.UsedPercent: self.used_percent,
                        CommonKeys.REASON: 'Must be a float',
                        ApiResultKeys.VFENSE_STATUS_CODE: (
                            GenericCodes.InvalidValue
                        )
                    }
                )

        if self.free_percent:
            if not isinstance(self.free_percent, float):
                invalid_fields.append(
                    {
                        MemoryStatKeys.FreePercent: self.free_percent,
                        CommonKeys.REASON: 'Must be a float',
                        ApiResultKeys.VFENSE_STATUS_CODE: (
                            GenericCodes.InvalidValue
                        )
                    }
                )

        if self.system:
            if not isinstance(self.system, float):
                invalid_fields.append(
                    {
                        CpuStatKeys.System: self.system,
                        CommonKeys.REASON: 'Must be a float',
                        ApiResultKeys.VFENSE_STATUS_CODE: (
                            GenericCodes.InvalidValue
                        )
                    }
                )

        if self.iowait:
            if not isinstance(self.iowait, float):
                invalid_fields.append(
                    {
                        CpuStatKeys.IOWait: self.iowait,
                        CommonKeys.REASON: 'Must be a float',
                        ApiResultKeys.VFENSE_STATUS_CODE: (
                            GenericCodes.InvalidValue
                        )
                    }
                )

        return invalid_fields

    def to_dict(self):
        inherited_data = super(MemoryStats, self).to_dict()
        data = {
            MemoryStatKeys.UsedPercent: self.used_percent,
            MemoryStatKeys.FreePercent: self.free_percent,
            MemoryStatKeys.Used: self.used,
            MemoryStatKeys.Free: self.free,
        }
        return dict(data.items() + inherited_data.items())
