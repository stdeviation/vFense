from vFense.core.decorators import time_it
from vFense.core._constants import SortValues
from vFense.plugins.vuln.ubuntu._db_model import UbuntuVulnerabilityKeys
from vFense.plugins.vuln.ubuntu.search._db import FetchUbuntuVulns
from vFense.search.base import RetrieveBase


class RetrieveUbuntuVulns(RetrieveBase):
    def __init__(
        self, sort=SortValues.DESC,
        sort_key=UbuntuVulnerabilityKeys.DatePosted, **kwargs
        ):
        super(RetrieveUbuntuVulns, self).__init__(**kwargs)

        self.valid_keys_to_filter_by = (
            [
                UbuntuVulnerabilityKeys.VulnerabilityId,
                UbuntuVulnerabilityKeys.DatePosted,
            ]
        )

        valid_keys_to_sort_by = (
            [
                UbuntuVulnerabilityKeys.VulnerabilityId,
                UbuntuVulnerabilityKeys.DatePosted,
            ]
        )

        if sort_key not in valid_keys_to_sort_by:
            self.sort_key = UbuntuVulnerabilityKeys.VulnerabilityId

        self.fetch_vulns = (
            FetchUbuntuVulns(
                count=self.count, offset=self.offset,
                sort=self.sort, sort_key=self.sort_key
            )
        )

    @time_it
    def by_id(self, bulletin_id):
        """Retrieve vulnerability by id.
        Args:
            bulletin_id (str): The Ubuntu USN bulletin id.
                Example: 'USN-2250-1'

        Basic Usage:
            >>> from vFense.plugins.vuln.ubuntu.search.search import RetrieveUbuntuVulns
            >>> search = RetrieveUbuntuVulns()
            >>> search.by_id('USN-2250-1')

        Returns:
            List of dictionairies.
        """
        count, data = self.fetch_vulns.by_id(bulletin_id)
        return self._base(count, data)
