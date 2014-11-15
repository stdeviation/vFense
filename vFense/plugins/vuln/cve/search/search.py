from vFense.core.decorators import time_it
from vFense.core._constants import (
    SortValues, DefaultQueryValues
)
from vFense.plugins.vuln.cve._db_model import CveKeys
from vFense.plugins.vuln.cve.search._db import FetchCves
from vFense.search.base import RetrieveBase

class RetrieveCVEs(RetrieveBase):
    def __init__(
        self, count=DefaultQueryValues.COUNT,
        offset=DefaultQueryValues.OFFSET, sort=SortValues.DESC,
        sort_key=CveKeys.DatePosted, **kwargs
        ):
        super(RetrieveCVEs, self).__init__(**kwargs)

        self.valid_keys_to_filter_by = (
            [
                CveKeys.CveId,
                CveKeys.Score,
                CveKeys.BaseScore,
                CveKeys.ExploitScore,
                CveKeys.Categories,
            ]
        )

        valid_keys_to_sort_by = (
            [
                CveKeys.CveId,
                CveKeys.Score,
                CveKeys.BaseScore,
                CveKeys.ExploitScore,
                CveKeys.DateModified,
                CveKeys.DatePosted,
            ]
        )

        if self.sort_key not in valid_keys_to_sort_by:
            self.sort_key = CveKeys.DatePosted

        self.fetch = (
            FetchCves(self.count, self.offset, self.sort, self.sort_key)
        )

    @time_it
    def by_id(self, cve_id):
        """Retrieve cve by id.
        Args:
            cve_id (str): The cve_id.
                Example: 'CVE-2014-1817'

        Basic Usage:
            >>> from vFense.plugins.vuln.cve.search.search import RetrieveCVEs
            >>> search_cves = RetrieveCVEs()
            >>> search_cves.by_id('CVE-2014-1817')

        Returns:
            List of dictionairies.
        """
        count, data = self.fetch.by_id(cve_id)
        return self._base(count, data)

    @time_it
    def by_base_score(self, score, logic=None):
        """Retrieve cve data by cve base score.
        Args:
            score (float): Number from 0.0 to 10
                Example: 9.3
            logic (str): valid filters == ( ==, <=, >=, !=, >, < )

        Basic Usage:
            >>> from vFense.plugins.vuln.cve.search.search import RetrieveCVEs
            >>> search_cves = RetrieveCVEs()
            >>> search_cves.by_base_score(5, '>')

        Returns:
            List of dictionairies.
        """
        count, data = (
            self.fetch.by_score(CveKeys.BaseScore, score, logic)
        )
        return self._base(count, data)

    @time_it
    def by_score(self, score, logic=None):
        """Retrieve cve data by cve score.
        Args:
            score (float): Number from 0.0 to 10
                Example: 9.3
            logic (str): valid filters == ( ==, <=, >=, !=, >, < )

        Basic Usage:
            >>> from vFense.plugins.vuln.cve.search.search import RetrieveCVEs
            >>> search_cves = RetrieveCVEs()
            >>> search_cves.by_base_score(5, '>')

        Returns:
            List of dictionairies.
        """
        count, data = (
            self.fetch.by_score(CveKeys.Score, score, logic)
        )
        return self._base(count, data)

    @time_it
    def by_exploit_sub_score(self, score, logic=None):
        """Retrieve cve data by cve score.
        Args:
            score (float): Number from 0.0 to 10
                Example: 9.3
            logic (str): valid filters == ( ==, <=, >=, !=, >, < )

        Basic Usage:
            >>> from vFense.plugins.vuln.cve.search.search import RetrieveCVEs
            >>> search_cves = RetrieveCVEs()
            >>> search_cves.by_base_score(5, '>')

        Returns:
            List of dictionairies.
        """
        count, data = (
            self.fetch.by_score(
                CveKeys.ExploitScore, score, logic
            )
        )
        return self._base(count, data)
