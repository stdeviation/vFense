from vFense.core.stats._db import valid_stat_types
from vFense.core.stats.search._db import FetchStats
from vFense.core.decorators import time_it
from vFense.search.base import RetrieveBase

class RetrieveStats(RetrieveBase):
    def __init__(self, agent_id=None, **kwargs):
        super(RetrieveStats, self).__init__(**kwargs)
        self.agent_id = agent_id

        self.fetch = (
            FetchStats(
                agent_id=self.agent_id, count=self.count,
                offset=self.offset, sort=self.sort, sort_key=self.sort_key
            )
        )

    @time_it
    def by_stat(self, stat_type):
        """Query stats by stat type
        Args:
            stat_type (str): The stat type. Example.. cpu, memory,
                and fila_esystem.

        Basic Usage:
            >>> from vFense.core.stats.search.stats import RetrieveStats
            >>> agent_id = '96f02bcf-2ada-465c-b175-0e5163b36e1c'
            >>> stat_type = 'cpu'
            >>> search = RetrieveStats(agent_id=agent_id)
            >>> search.by_stat(stat_type)
    """
        if stat_type in valid_stat_types():
            count, data = self.fetch.by_stat(stat_type)
            return self._base(count, data)
        else:
            return self._set_results_invalid_filter_key(stat_type)
