from vFense.db.client import db_create_close, r
from vFense.core.agent._db_model import (
    AgentKeys, AgentCollections, AgentIndexes,
    HardwarePerAgentIndexes, HardwarePerAgentKeys
)
from vFense.core.decorators import time_it, catch_it
from vFense.search._db_base import FetchBase
from vFense.core.stats._db_model import (
    StatsCollections, MemoryStatKeys, CpuStatKeys, AgentStatKeys,
    FileSystemStatKeys, StatsPerAgentIndexes
)


class FetchHardware(FetchBase):
    """Hardware database queries"""
    def __init__(self, **kwargs):
        super(FetchHardware, self).__init__(**kwargs)

        self.keys_to_pluck = [
            AgentKeys.ComputerName, AgentKeys.HostName, AgentKeys.DisplayName,
            AgentKeys.OsCode, AgentKeys.OsString, AgentKeys.AgentId,
            AgentKeys.AgentStatus, AgentKeys.MachineType, AgentKeys.BitType
        ]
        self.valid_types = self.get_types()

    @time_it
    @catch_it((0, []))
    @db_create_close
    def all(self, conn=None):
        base_filter = self._set_agent_base_query()
        count = (
            base_filter
            .count()
            .run(conn)
        )

        data = (
            base_filter
            .distinct()
            .order_by(self.sort(self.sort_key))
            .skip(self.offset)
            .limit(self.count)
            .run(conn)
        )
        return(count, data)

    def memory(self):
        merge = self._set_memory_merge_query()
        return self._by_type('memory', data_merge=merge)

    def nic(self):
        return self._by_type('nic')

    def cpu(self):
        merge = self._set_cpu_merge_query()
        return self._by_type('cpu', data_merge=merge)

    def display(self):
        return self._by_type('display')

    def storage(self):
        return self._by_type('storage')

    def memory_by_regex(self, query_key, regex):
        return self._by_type('memory', query_key, regex)

    def nic_by_regex(self, query_key, regex):
        return self._by_type('nic', query_key, regex)

    def cpu_by_regex(self, query_key, regex):
        return self._by_type('cpu', query_key, regex)

    def display_by_regex(self, query_key, regex):
        return self._by_type('display', query_key, regex)

    def storage_by_regex(self, query_key, regex):
        return self._by_type_and_query('storage', query_key, regex)

    def nic_by_os_string_and_by_regex(self, os_string, query_key, regex):
        return self._by_type_and_filter_by_key_and_by_query(
            'nic', 'os_string', os_string, query_key, regex
        )

    def nic_by_os_code_and_by_regex(self, os_code, query_key, regex):
        return self._by_type_and_filter_by_key_and_by_query(
            'nic', 'os_code', os_code, query_key, regex
        )

    def nic_by_arch_and_by_regex(self, bit_type, query_key, regex):
        return self._by_type_and_filter_by_key_and_by_query(
            'nic', 'bit_type', bit_type, query_key, regex
        )

    def cpu_by_os_string_and_by_regex(self, os_string, query_key, regex):
        return self._by_type_and_filter_by_key_and_by_query(
            'cpu', 'os_string', os_string, query_key, regex
        )

    def cpu_by_os_code_and_by_regex(self, os_code, query_key, regex):
        return self._by_type_and_filter_by_key_and_by_query(
            'cpu', 'os_code', os_code, query_key, regex
        )

    def cpu_by_arch_and_by_regex(self, bit_type, query_key, regex):
        return self._by_type_and_filter_by_key_and_by_query(
            'cpu', 'bit_type', bit_type, query_key, regex
        )

    def display_by_os_string_and_by_regex(self, os_string, query_key, regex):
        return self._by_type_and_filter_by_key_and_by_query(
            'display', 'os_string', os_string, query_key, regex
        )

    def display_by_os_code_and_by_regex(self, os_code, query_key, regex):
        return self._by_type_and_filter_by_key_and_by_query(
            'display', 'os_code', os_code, query_key, regex
        )

    def display_by_arch_and_by_regex(self, bit_type, query_key, regex):
        return self._by_type_and_filter_by_key_and_by_query(
            'display', 'bit_type', bit_type, query_key, regex
        )

    def storage_by_os_string_and_by_regex(self, os_string, query_key, regex):
        return self._by_type_and_filter_by_key_and_by_query(
            'storage', 'os_string', os_string, query_key, regex
        )

    def storage_by_os_code_and_by_regex(self, os_code, query_key, regex):
        return self._by_type_and_filter_by_key_and_by_query(
            'storage', 'os_code', os_code, query_key, regex
        )

    def storage_by_arch_and_by_regex(self, bit_type, query_key, regex):
        return self._by_type_and_filter_by_key_and_by_query(
            'storage', 'bit_type', bit_type, query_key, regex
        )

    def memory_by_os_string_and_by_regex(self, os_string, query_key, regex):
        return self._by_type_and_filter_by_key_and_by_query(
            'memory', 'os_string', os_string, query_key, regex
        )

    def memory_by_os_code_and_by_regex(self, os_code, query_key, regex):
        return self._by_type_and_filter_by_key_and_by_query(
            'memory', 'os_code', os_code, query_key, regex
        )

    def memory_by_arch_and_by_regex(self, bit_type, query_key, regex):
        return self._by_type_and_filter_by_key_and_by_query(
            'storage', 'bit_type', bit_type, query_key, regex
        )

    @time_it
    @catch_it((0, []))
    @db_create_close
    def _by_type(self, htype=None, data_merge=None, conn=None):
        base_count, base_filter = self._set_base_query_by_type(htype)
        count = (
            base_count
            .count()
            .run(conn)
        )
        if data_merge:
            base_filter = base_filter.merge(data_merge)

        data = (
            base_filter
            .distinct()
            .order_by(self.sort(self.sort_key))
            .skip(self.offset)
            .limit(self.count)
            .run(conn)
        )
        return(count, data)

    @time_it
    @catch_it((0, []))
    @db_create_close
    def _by_type_and_query(self, htype, key, query, conn=None):
        base_count, base_filter = self._set_base_query_by_type(htype)
        count = (
            base_count
            .filter(lambda x: x[key].match(query))
            .count()
            .run(conn)
        )

        data = (
            base_filter
            .filter(lambda x: x[key].match(query))
            .distinct()
            .order_by(self.sort(self.sort_key))
            .skip(self.offset)
            .limit(self.count)
            .run(conn)
        )
        return(count, data)

    @time_it
    @catch_it((0, []))
    @db_create_close
    def _by_type_and_filter_by_key_and_by_query(
        self, htype, filter_key, filter_query, key, query, conn=None
    ):
        base_count, base_filter = self._set_base_query_by_type(htype)
        count = (
            base_count
            .filter(lambda x: x[filter_key].match(filter_query))
            .filter(lambda x: x[key].match(query))
            .count()
            .run(conn)
        )

        data = (
            base_filter
            .filter(lambda x: x[filter_key].match(filter_query))
            .filter(lambda x: x[key].match(query))
            .distinct()
            .order_by(self.sort(self.sort_key))
            .skip(self.offset)
            .limit(self.count)
            .run(conn)
        )
        return(count, data)

    def _set_agent_base_query(self):
        if self.view_name:
            base_filter = (
                r
                .table(AgentCollections.Agents)
                .get_all(
                    self.view_name,
                    index=AgentKeys.Views
                )
                .pluck(self.keys_to_pluck)
                .eq_join(
                    lambda x:
                        x[AgentKeys.AgentId],
                        r.table(AgentCollections.Hardware),
                        index=HardwarePerAgentIndexes.AgentId
                )
                .zip()
            )
        else:
            base_filter = (
                r
                .table(AgentCollections.Agents)
                .pluck(self.keys_to_pluck)
                .eq_join(
                    lambda x:
                        x[AgentKeys.AgentId],
                        r.table(AgentCollections.Hardware),
                        index=HardwarePerAgentIndexes.AgentId
                )
                .zip()
            )

        return base_filter

    def _set_base_query_by_type(self, htype=None):
        if htype in self.get_types():
            valid_type = htype
        else:
            valid_type = HardwarePerAgentKeys.Nic

        if self.view_name:
            base_count = (
                r
                .table(AgentCollections.Agents)
                .get_all(self.view_name, index=AgentIndexes.Views)
                .pluck(self.keys_to_pluck)
                .eq_join(
                    lambda x: [
                        x[AgentKeys.AgentId],
                        valid_type
                    ],
                    r.table(AgentCollections.Hardware),
                    index=HardwarePerAgentIndexes.AgentIdAndType
                )
                .zip()
            )

            base_filter = (
                r
                .table(AgentCollections.Agents)
                .get_all(self.view_name, index=AgentIndexes.Views)
                .pluck(self.keys_to_pluck)
                .eq_join(
                    lambda x: [
                        x[AgentKeys.AgentId],
                        valid_type
                    ],
                    r.table(AgentCollections.Hardware),
                    index=HardwarePerAgentIndexes.AgentIdAndType
                )
                .zip()
            )
        else:
            base_filter = (
                r
                .table(AgentCollections.Agents)
                .pluck(self.keys_to_pluck)
                .eq_join(
                    lambda x: [
                        x[AgentKeys.AgentId],
                        valid_type
                    ],
                    r.table(AgentCollections.Hardware),
                    index=HardwarePerAgentIndexes.AgentIdAndType
                )
                .zip()
            )
            base_count = (
                r
                .table(AgentCollections.Agents)
                .pluck(self.keys_to_pluck)
                .eq_join(
                    lambda x: [
                        x[AgentKeys.AgentId],
                        valid_type
                    ],
                    r.table(AgentCollections.Hardware),
                    index=HardwarePerAgentIndexes.AgentIdAndType
                )
                .zip()
            )

        return(base_count, base_filter)

    @catch_it([])
    @db_create_close
    def get_types(self, conn=None):
        types = (
            r
            .table(AgentCollections.Hardware)
            .map(lambda x: x[HardwarePerAgentKeys.Type])
            .distinct()
            .run(conn)
        )
        return types

    @catch_it([])
    @db_create_close
    def get_valid_keys_for_type(self, htype, conn=None):
        hrow = list(
            r
            .table(AgentCollections.Hardware)
            .get_all(htype, index=HardwarePerAgentIndexes.Type)
            .limit(1)
            .run(conn)
        )
        if hrow:
            keys = list(set(hrow[0].keys()).union(self.keys_to_pluck))
        else:
            keys = []
        return keys

    def _set_memory_merge_query(self):
        merge_query = (
            lambda x:
            {
                'stats': (
                    r
                    .table(StatsCollections.AgentStats)
                    .get_all(
                        [x[MemoryStatKeys.AgentId], 'memory'],
                        index=StatsPerAgentIndexes.AgentIdAndStatType
                    )
                    .pluck(
                        MemoryStatKeys.Free, MemoryStatKeys.Used,
                        MemoryStatKeys.Total, MemoryStatKeys.UsedPercent,
                        MemoryStatKeys.FreePercent, MemoryStatKeys.LastUpdated
                    )
                    .merge(
                        lambda y: {
                            MemoryStatKeys.LastUpdated: (
                                y[MemoryStatKeys.LastUpdated].to_epoch_time()
                            )
                        }
                    )
                    .coerce_to('array')
                )
            }
        )
        return merge_query

    def _set_cpu_merge_query(self):
        merge_query = (
            lambda x:
            {
                'stats': (
                    r
                    .table(StatsCollections.AgentStats)
                    .get_all(
                        [x[MemoryStatKeys.AgentId], 'cpu'],
                        index=StatsPerAgentIndexes.AgentIdAndStatType
                    )
                    .pluck(
                        CpuStatKeys.Idle, CpuStatKeys.System,
                        CpuStatKeys.User, CpuStatKeys.Total,
                        CpuStatKeys.IOWait, CpuStatKeys.LastUpdated
                    )
                    .merge(
                        lambda y: {
                            CpuStatKeys.LastUpdated: (
                                y[CpuStatKeys.LastUpdated].to_epoch_time()
                            )
                        }
                    )
                    .coerce_to('array')
                )
            }
        )
        return merge_query
