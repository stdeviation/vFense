from vFense.core.scheduler._db_model import JobKeys
from vFense.core.scheduler.search._db import (
    FetchJobs, FetchAgentJobs, FetchTagJobs
)
from vFense.plugins.patching.scheduler.search._db import FetchAppJobs
from vFense.core.decorators import time_it
from pytz import all_timezones
from vFense.core.scheduler.search.search import RetrieveJobs


class RetrieveAppJobs(RetrieveJobs):
    """Job database queries."""
    def __init__(self, sort_key=JobKeys.NextRunTime, **kwargs):
        super(RetrieveAppJobs, self).__init__(**kwargs)
        self._set_properties()

        if self.sort_key not in self.valid_keys_to_sort_by:
            self.sort_key = JobKeys.NextRunTime

        self.fetch_jobs = (
            FetchAppJobs(
                view_name=self.view_name, count=self.count,
                offset=self.offset, sort=self.sort, sort_key=self.sort_key
            )
        )


