from vFense.core.agent._constants import AgentCommonKeys
from vFense.core.agent._db_model import (
    AgentKeys, AgentCollections, HardwarePerAgentKeys
)
from vFense.core.stats._db_model import (
    StatsCollections, CpuStatKeys, MemoryStatKeys, FileSystemStatKeys,
    StatsPerAgentIndexes, AgentStatKeys
)
from vFense.core.decorators import time_it, catch_it
from vFense.db.client import db_create_close, r
from vFense.search._db_base import FetchBase

class  FetchStats(FetchBase):
    def __init__(self, agent_id=None, **kwargs):
        """Search agents based on an ip address.
        Args:
            agent_id (str): 36 character UUID of the agent.
        """
        super(FetchStats, self).__init__(**kwargs)
        self.agent_id = None

    @time_it
    @catch_it((0, []))
    @db_create_close
    def by_stat(self, stat, conn=None):
        """Search agents based on an ip address.
        Args:
            stat (str): The stat type you want to retrieve stats for.
                example.. cpu, memory, filesystem

        Basic Usage:
            >>> from vFense.core.stat.search._db import FetchStats
            >>> agent_id = '96f02bcf-2ada-465c-b175-0e5163b36e1c'
            >>> fetch = FetchStats(agent_id=agent_id)
            >>> fetch.by_stat('cpu')

        Returns:
            List of dictionairies.
        """
        base_count, base_filter = self._set_base_query()
        query_merge = self._set_merge_query()
        count = (
            base_count
            .filter({AgentStatKeys.StatType: stat})
            .distinct()
            .count()
            .run(conn)
        )

        data = list(
            base_filter
            .filter({AgentStatKeys.StatType: stat})
            .merge(query_merge)
            .distinct()
            .order_by(self.sort(self.sort_key))
            .skip(self.offset)
            .limit(self.count)
            .run(conn)
        )

        return(count, data)

    def _set_base_query(self):
        base_filter = (
            r
            .table(StatsCollections.AgentStats)
            .get_all(self.agent_id, index=StatsPerAgentIndexes.AgentId)
        )
        base_count = base_filter

        return(base_count, base_filter)

    def _set_merge_query(self):
        merge_query = (
            lambda x:
            {
                AgentStatKeys.LastUpdated: (
                    x[AgentStatKeys.LastUpdated].to_epoch_time()
                )
            }
        )

        return merge_query


