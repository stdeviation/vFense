import logging
import logging.config
from vFense._constants import VFENSE_LOGGING_CONFIG

from vFense.core.stats._constants import StatsType
from vFense.core.decorators import time_it
from vFense.core.stats import (
    CPUStats, MemoryStats, FileSystemStats
)
from vFense.core.stats._db import (
    fetch_stats_by_agent_id_and_type, insert_stat,
    update_stat
)
from vFense.core.status_codes import (
    DbCodes, GenericCodes, GenericFailureCodes,
)
from vFense.core.stats.status_codes import (
    StatCodes, StatFailureCodes
)
from vFense.core.results import ApiResults

logging.config.fileConfig(VFENSE_LOGGING_CONFIG)
logger = logging.getLogger('vfense_api')


class StatManager(object):
    def __init__(self, agent_id=None):
        self.agent_id = agent_id

    def stats(self, stat_type=None):
        stats = (
            fetch_stats_by_agent_id_and_type(self.agent_id, stat_type)
        )
        return stats

    @time_it
    def create(self, stat):
        """Add an agent into vFense.
        Args:
            stat (CPUStats|MemoryStats|FileSystemStats): A valid stats instance.

        Basic Usage:
            >>> from vFense.core.stats.manager import StatManager
            >>> from vFense.core.stats import CPUStats
            >>> stat = CPUStats(idle=72.75, system=2.22, user=24.95)
            >>> manager = StatManager('38226b0e-a482-4cb8-b135-0a0057b913f2')
            >>> manager.create(stat)

        Returns:
            Dictionary
            >>>
        """
        results = ApiResults()
        results.fill_in_defaults()
        stat.fill_in_defaults()
        invalid_fields = stat.get_invalid_fields()
        stat.agent_id = self.agent_id
        if not invalid_fields:
            status_code, _, _, generated_ids = (
                insert_stat(stat.to_dict_db())
            )
            if status_code == DbCodes.Inserted:
                stat_id = generated_ids.pop()
                stat.id = stat_id
                msg = 'Stat {0} added successfully'.format(stat.to_dict())
                results.generic_status_code = GenericCodes.ObjectCreated
                results.vfense_status_code = StatCodes.StatCreated
                results.message = msg
                results.data.append(stat.to_dict())
                results.generated_ids.append(stat.id)

            else:
                msg = 'Failed to add stat.'
                results.generic_status_code = (
                    GenericFailureCodes.FailedToCreateObject
                )
                results.vfense_status_code = (
                    StatFailureCodes.FailedToCreateStat
                )
                results.message = msg
                results.data.append(stat.to_dict())

        else:
            msg = 'Failed to add stat, invalid fields were passed'
            results.generic_status_code = (
                GenericFailureCodes.FailedToCreateObject
            )
            results.vfense_status_code = (
                StatFailureCodes.FailedToCreateStat
            )
            results.message = msg
            results.errors = invalid_fields
            results.data.append(stat.to_dict())

        return results

    @time_it
    def update(self, stat):
        """Add an agent into vFense.
        Args:
            stat (CPUStats|MemoryStats|FileSystemStats): A valid stats instance.

        Basic Usage:
            >>> from vFense.core.stats.manager import StatManager
            >>> from vFense.core.stats import CPUStats
            >>> stat = CPUStats(idle=72.75, system=2.22, user=24.95)
            >>> manager = StatManager('38226b0e-a482-4cb8-b135-0a0057b913f2')
            >>> manager.update(stat)

        Returns:
            Dictionary
            >>>
        """
        results = ApiResults()
        results.fill_in_defaults()
        stat.fill_in_defaults()
        invalid_fields = stat.get_invalid_fields()
        stat.agent_id = self.agent_id
        if not invalid_fields:
            status_code, _, _, generated_ids = self._update_stat(stat)
            if (status_code == DbCodes.Replaced or
                    status_code == DbCodes.Unchanged):
                msg = (
                    'Stat {0} updated successfully'
                    .format(stat.to_dict_non_null())
                )
                results.generic_status_code = GenericCodes.ObjectCreated
                results.vfense_status_code = StatCodes.StatUpdated
                results.message = msg
                results.data.append(stat.to_dict_non_null())

            elif status_code == DbCodes.Skipped:
                msg = 'Failed to update stat.'
                results.generic_status_code = GenericFailureCodes.InvalidId
                results.vfense_status_code = StatFailureCodes.InvalidId
                results.message = msg
                results.data.append(stat.to_dict_non_null())

            else:
                msg = 'Failed to update stat.'
                results.generic_status_code = (
                    GenericFailureCodes.FailedToUpdateObject
                )
                results.vfense_status_code = (
                    StatFailureCodes.FailedToUpdateStat
                )
                results.message = msg
                results.data.append(stat.to_dict())

        else:
            msg = 'Failed to update stat, invalid fields were passed'
            results.generic_status_code = (
                GenericFailureCodes.FailedToUpdateObject
            )
            results.vfense_status_code = (
                StatFailureCodes.FailedToUpdateStat
            )
            results.message = msg
            results.errors = invalid_fields
            results.data.append(stat.to_dict())

        return results

    def _update_stat(self, stat):
        results = update_stat(
            stat.agent_id, stat.stat_type, stat.to_dict_db()
        )
        return results


class CPUStatManager(StatManager):
    def __init__(self, **kwargs):
        super(CPUStatManager, self).__init__(**kwargs)
        self.cpu = self.stats()

    def stats(self):
        cpu = super(CPUStatManager, self).stats(StatsType.CPU)
        if cpu:
            cpu = CPUStats(**cpu[0])

        return cpu


class MemoryStatManager(StatManager):
    def __init__(self, **kwargs):
        super(MemoryStatManager, self).__init__(**kwargs)
        self.memory = self.stats()

    def stats(self):
        mem = super(MemoryStatManager, self).stats(StatsType.MEM)
        if mem:
            mem = MemoryStats(**mem[0])

        return mem


class FileSystemStatManager(StatManager):
    def __init__(self, **kwargs):
        super(FileSystemStatManager, self).__init__(**kwargs)
        self.file_systems = self.stats()

    def update(self, stats):
        for stat in stats:
            file_systems = self.stats()
            if file_systems:
                stat.agent_id = self.agent_id
                if stat.name in map(lambda x: x.name, file_systems):
                    results = super(FileSystemStatManager, self).update(stat)
                else:
                    results = super(FileSystemStatManager, self).create(stat)
            else:
                results = super(FileSystemStatManager, self).create(stat)

        return results

    def stats(self):
        filesystems = (
            super(FileSystemStatManager, self).stats(StatsType.FILE_SYSTEM)
        )
        fs_objects = []
        if filesystems:
            for fs in filesystems:
                fs_objects.append(FileSystemStats(**fs))

        return fs_objects

    def _update_stat(self, stat):
        results = update_stat(
            stat.agent_id, stat.stat_type, stat.to_dict_db(), stat.name
        )
        return results
