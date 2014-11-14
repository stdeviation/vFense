from vFense.core.decorators import time_it
from vFense.core._constants import SortValues
from vFense.plugins.vuln.windows.search._db import FetchWindowsVulns
from vFense.plugins.vuln.windows._db_model import WindowsVulnerabilityKeys
from vFense.search.base import RetrieveBase

class RetrieveWindowVulns(RetrieveBase):
    def __init__(
        self,sort=SortValues.DESC,
        sort_key=WindowsVulnerabilityKeys.DatePosted, **kwargs
        ):

        self.valid_keys_to_filter_by = (
            [
                WindowsVulnerabilityKeys.VulnerabilityId,
                WindowsVulnerabilityKeys.DatePosted,
            ]
        )

        valid_keys_to_sort_by = (
            [
                WindowsVulnerabilityKeys.VulnerabilityId,
                WindowsVulnerabilityKeys.DatePosted,
            ]
        )

        if sort_key not in valid_keys_to_sort_by:
            self.sort_key = WindowsVulnerabilityKeys.VulnerabilityId

        self.fetch_vulns = (
            FetchWindowsVulns(
                count=self.count, offset=self.offset,
                sort=self.sort, sort_key=self.sort_key
            )
        )

    @time_it
    def by_id(self, bulletin_id):
        """Retrieve vulnerability by id.
        Args:
            bulletin_id (str): The Windows MS bulletin id.
                Example: 'MS14-036'

        Basic Usage:
            >>> from vFense.plugins.vuln.ubuntu.search.search import RetrieveWindowVulns
            >>> search = RetrieveWindowVulns()
            >>> search.by_id('MS14-036')

        Returns:
            List of dictionairies.
        """
        count, data = self.fetch_vulns.by_id(bulletin_id)
        return self._base(count, data)
