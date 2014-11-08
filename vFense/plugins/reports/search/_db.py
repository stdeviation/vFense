import logging

from vFense._constants import VFENSE_LOGGING_CONFIG
from vFense.db.client import db_create_close, r
from vFense.core._constants import SortValues, DefaultQueryValues
from vFense.core.agent._db_model import (
    AgentKeys, AgentCollections, AgentIndexes,
    HardwarePerAgentIndexes, HardwarePerAgentKeys
)
from vFense.core.decorators import time_it, catch_it

logging.config.fileConfig(VFENSE_LOGGING_CONFIG)
logger = logging.getLogger('rvapi')


class FetchHardware(object):
    """Agent database queries"""
    def __init__(
        self, view_name=None,
        count=DefaultQueryValues.COUNT,
        offset=DefaultQueryValues.OFFSET,
        sort=SortValues.ASC,
        sort_key=AgentKeys.ComputerName
        ):
        """
        Kwargs:
            view_name (str): Fetch all agents in this view.
            count (int): The number of results to return.
            offset (int): The next set of results beginning at offset.
            sort (str): asc or desc.
            sort_key (str): The key you are going to sort the results by.
        """
        self.view_name = view_name
        self.count = count
        self.offset = offset
        self.sort_key = sort_key

        self.keys_to_pluck = [
            AgentKeys.ComputerName, AgentKeys.HostName, AgentKeys.DisplayName,
            AgentKeys.OsCode, AgentKeys.OsString, AgentKeys.AgentId,
            AgentKeys.AgentStatus, AgentKeys.MachineType, AgentKeys.BitType
        ]
        self.valid_types = self.get_types()

        if sort == SortValues.ASC:
            self.sort = r.asc
        else:
            self.sort = r.desc

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
        return self._by_type('memory')

    def nic(self):
        return self._by_type('nic')

    def cpu(self):
        return self._by_type('cpu')

    def display(self):
        return self._by_type('display')

    def storage(self):
        return self._by_type('storage')

    @time_it
    @catch_it((0, []))
    @db_create_close
    def _by_type(self, htype=None, conn=None):
        base_count, base_filter = self._set_base_query_by_type(htype)
        count = (
            base_count
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

    @time_it
    @catch_it((0, []))
    @db_create_close
    def _by_type_and_query(self, key, query, htype=None, conn=None):
        base_count, base_filter = self._set_base_query_by_type(htype)
        count = (
            base_count
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
