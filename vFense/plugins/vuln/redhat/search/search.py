from vFense.core.decorators import time_it
from vFense.core._constants import SortValues
from vFense.plugins.vuln.redhat._db_model import RedhatVulnerabilityKeys
from vFense.plugins.vuln.redhat.search._db import FetchRedhatVulns
from vFense.search.base import RetrieveBase

class RetrieveRedhatVulns(RetrieveBase):
    def __init__(
        self, sort=SortValues.DESC,
        sort_key=RedhatVulnerabilityKeys.DatePosted, **kwargs
        ):

        self.valid_keys_to_filter_by = (
            [
                RedhatVulnerabilityKeys.VulnerabilityId,
                RedhatVulnerabilityKeys.DatePosted,
            ]
        )

        valid_keys_to_sort_by = (
            [
                RedhatVulnerabilityKeys.VulnerabilityId,
                RedhatVulnerabilityKeys.DatePosted,
            ]
        )

        if sort_key not in valid_keys_to_sort_by:
            self.sort_key = RedhatVulnerabilityKeys.VulnerabilityId

        self.fetch_vulns = (
            FetchRedhatVulns(
                count=self.count, offset=self.offset,
                sort=self.sort, sort_key=self.sort_key
            )
        )

    @time_it
    def by_id(self, bulletin_id):
        """Retrieve vulnerability by id.
        Args:
            bulletin_id (str): The redhat USN bulletin id.
                Example: 'USN-2250-1'

        Basic Usage:
            >>> from vFense.plugins.vuln.redhat.search.search import RetrieveredhatVulns
            >>> search = RetrieveredhatVulns()
            >>> search.by_id('USN-2250-1')

        Returns:
            List of dictionairies.
        """
        count, data = self.fetch_vulns.by_id(bulletin_id)
        return self._base(count, data)
