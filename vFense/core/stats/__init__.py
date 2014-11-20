import re
from time import time
from vFense import Base
from vFense.core._db_constants import DbTime
from vFense.core.stats._db_model import (
    CpuStatKeys, AgentStatKeys, MemoryStatKeys, FileSystemStatKeys
)
from vFense.core.agent._constants import agent_regex
from vFense.core._constants import CommonKeys
from vFense.core.stats._constants import StatsType
from vFense.core.results import ApiResultKeys
from vFense.core.status_codes import GenericCodes


class Stats(Base):
    """Used to represent an instance of an agent."""

    def __init__(self, agent_id=None, stat_type=None, last_updated=None,
                 id=None, **kwargs):
        """
        Kwargs:
            id (str): The 36 Character UUID of this stat.
            agent_id (str): The id of the agent.
            stat_type (str): The type of the stat.
            last_updated (float): The unixtimestamp
        """
        super(Stats, self).__init__(**kwargs)
        self.id = id
        self.agent_id = agent_id
        self.stat_type = stat_type
        self.last_updated = last_updated


    def fill_in_defaults(self):
        """Replace all the fields that have None as their value with
        the hardcoded default values.

        Use case(s):
            Useful when adding a new agent instance and only want to fill
            in a few fields, then allow the add agent functions to call this
            method to fill in the rest.
        """

        if not self.last_updated:
            self.last_updated = time()

    def get_invalid_fields(self):
        """Check the agent for any invalid fields.

        """
        invalid_fields = []

        if self.agent_id:
            if (not isinstance(self.agent_id, str) and
                    not isinstance(self.agent_id, unicode)):
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
            AgentStatKeys.StatType: self.stat_type,
            AgentStatKeys.LastUpdated: self.last_updated
        }

        return data

    def to_dict_db(self):
        """ Turn the fields into a dictionary, with db related fields.

        Returns:
            (dict): A dictionary with the fields.

        """

        data = {
            AgentStatKeys.LastUpdated: (
                DbTime.epoch_time_to_db_time(self.last_updated)
            )
        }

        combined_data = dict(self.to_dict_non_null().items() + data.items())
        combined_data.pop(AgentStatKeys.Id, None)

        return dict(self.to_dict().items() + data.items())


class CPUStats(Stats):
    def __init__(self, idle=None, user=None, system=None,
                 iowait=None, total=None, **kwargs):
        super(CPUStats, self).__init__(**kwargs)
        """
        Kwargs:
            idle (float): Percent of cpu that is idle.
            user (float): Percent of cpu being used by the user.
            system (float): Percent of cpu being used by the system.
            iowait (float): Percent of cpu waiting.
            total (float): Size in kilobytes.
            agent_id (str): The id of the agent.
            stat_type (str): The type of the stat.
        """
        self.idle = idle
        self.user = user
        self.system = system
        self.iowait = iowait
        self.total = total
        self.stat_type = StatsType.CPU

    def fill_in_defaults(self):
        super(CPUStats, self).fill_in_defaults()
        if not self.idle:
            self.idle = 0.0
        else:
            if not isinstance(self.idle, float):
                self.idle = float(self.idle)

        if not self.system:
            self.system = 0.0
        else:
            if not isinstance(self.system, float):
                self.system = float(self.system)

        if not self.user:
            self.user = 0.0
        else:
            if not isinstance(self.user, float):
                self.user = float(self.user)

        if not self.iowait:
            self.iowait = 0.0
        else:
            if not isinstance(self.iowait, float):
                self.iowait = float(self.iowait)

        if not self.total:
            self.total = 0.0
        else:
            if not isinstance(self.total, float):
                self.total = float(self.total)

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

        if self.total:
            if not isinstance(self.total, float):
                invalid_fields.append(
                    {
                        CpuStatKeys.Total: self.total,
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
            CpuStatKeys.Total: self.total,
        }
        return dict(data.items() + inherited_data.items())

class MemoryStats(Stats):
    def __init__(self, used_percent=None, free_percent=None,
                 used=None, free=None, total=None, **kwargs):
        super(MemoryStats, self).__init__(**kwargs)
        """
        Kwargs:
            used_percent (float): Percent of memory being used.
            free_percent (float): Percent of free memory.
            used (float): Kilobytes used.
            free (float): kilobytes free.
            total (float): Size in kilobytes.
            agent_id (str): The id of the agent.
            stat_type (str): The type of the stat.
        """
        self.used_percent = used_percent
        self.free_percent = free_percent
        self.used = used
        self.free = free
        self.total = total
        self.stat_type = StatsType.MEM

    def fill_in_defaults(self):
        super(MemoryStats, self).fill_in_defaults()
        if not self.used_percent:
            self.used_percent = 0.0
        else:
            if not isinstance(self.used_percent, float):
                self.used_percent = float(self.used_percent)

        if not self.free_percent:
            self.free_percent = 0.0
        else:
            if not isinstance(self.free_percent, float):
                self.free_percent = float(self.free_percent)

        if not self.used:
            self.used = 0.0
        else:
            if not isinstance(self.used, float):
                self.used = float(self.used)

        if not self.free:
            self.free = 0.0
        else:
            if not isinstance(self.free, float):
                self.free = float(self.free)

        if not self.total:
            self.total = 0.0
        else:
            if not isinstance(self.total, float):
                self.total = float(self.total)

    def get_invalid_fields(self):
        """Check the agent for any invalid fields.

        """
        invalid_fields = super(MemoryStats, self).get_invalid_fields()

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

        if self.used:
            if not isinstance(self.used, float):
                invalid_fields.append(
                    {
                        MemoryStatKeys.Used: self.used,
                        CommonKeys.REASON: 'Must be a float',
                        ApiResultKeys.VFENSE_STATUS_CODE: (
                            GenericCodes.InvalidValue
                        )
                    }
                )

        if self.free:
            if not isinstance(self.free, float):
                invalid_fields.append(
                    {
                        MemoryStatKeys.Free: self.free,
                        CommonKeys.REASON: 'Must be a float',
                        ApiResultKeys.VFENSE_STATUS_CODE: (
                            GenericCodes.InvalidValue
                        )
                    }
                )

        if self.total:
            if not isinstance(self.total, float):
                invalid_fields.append(
                    {
                        MemoryStatKeys.Total: self.total,
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
            MemoryStatKeys.Total: self.total,
        }
        return dict(data.items() + inherited_data.items())


class FileSystemStats(MemoryStats):
    def __init__(self, mount=None, name=None, **kwargs):
        """
        Kwargs:
            used_percent (float): Percent of memory being used.
            free_percent (float): Percent of free memory.
            used (float): Kilobytes used.
            free (float): kilobytes free.
            mount (str): The full path of this mount.
            name (str): The name of this disk aka the device path.
            agent_id (str): The id of the agent.
            stat_type (str): The type of the stat.
        """
        super(FileSystemStats, self).__init__(**kwargs)
        self.name = name
        self.mount = mount
        self.stat_type = StatsType.FILE_SYSTEM

    def get_invalid_fields(self):
        """Check the agent for any invalid fields.

        """
        invalid_fields = super(FileSystemStats, self).get_invalid_fields()

        if self.name:
            if (not isinstance(self.name, str) and
                    not isinstance(self.name, unicode)):
                invalid_fields.append(
                    {
                        FileSystemStatKeys.Name: self.name,
                        CommonKeys.REASON: 'Must be a string',
                        ApiResultKeys.VFENSE_STATUS_CODE: (
                            GenericCodes.InvalidValue
                        )
                    }
                )

        if self.mount:
            if (not isinstance(self.mount, str) and
                    not isinstance(self.mount, unicode)):
                invalid_fields.append(
                    {
                        FileSystemStatKeys.Mount: self.mount,
                        CommonKeys.REASON: 'Must be a string',
                        ApiResultKeys.VFENSE_STATUS_CODE: (
                            GenericCodes.InvalidValue
                        )
                    }
                )


        return invalid_fields

    def to_dict(self):
        inherited_data = super(FileSystemStats, self).to_dict()
        data = {
            FileSystemStatKeys.Name: self.name,
            FileSystemStatKeys.Mount: self.mount,
        }
        return dict(data.items() + inherited_data.items())
