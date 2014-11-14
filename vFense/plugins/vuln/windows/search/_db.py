from vFense.db.client import db_create_close
from vFense.core.decorators import catch_it, time_it
from vFense.plugins.vuln.search._db_vuln_base import FetchVulnBase
from vFense.plugins.vuln.windows._db_model import (
    WindowsVulnerabilityCollections, WindowsVulnerabilityIndexes
)


class FetchWindowsVulns(FetchVulnBase):
    def __init__(self, **kwargs):
        self.collection = WindowsVulnerabilityCollections.Vulnerabilities
        super(FetchWindowsVulns, self).__init__(self.collection, **kwargs)

    @time_it
    @catch_it((0, []))
    @db_create_close
    def by_component_kb(self, kb, conn=None):
        count = 0
        data = []
        base_filter = self._set_base_query()
        merge_hash = self._set_merge_hash()
        count = (
            base_filter
            .get_all(kb, index=WindowsVulnerabilityIndexes.ComponentKb)
            .count()
            .run(conn)
        )

        data = list(
            base_filter
            .get_all(kb, index=WindowsVulnerabilityIndexes.ComponentKb)
            .order_by(self.sort(self.sort_key))
            .skip(self.offset)
            .limit(self.count)
            .merge(merge_hash)
            .run(conn)
        )

        return(count, data)
