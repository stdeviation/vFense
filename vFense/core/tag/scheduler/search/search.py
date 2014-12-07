from vFense.core.scheduler._db_model import JobKeys
from vFense.core.tag.scheduler.search._db import FetchTagJobs
from vFense.core.scheduler.search.search import RetrieveJobs

class RetrieveTagJobs(RetrieveJobs):
    """Job queries for a tag."""
    def __init__(self, tag_id=None, sort_key=JobKeys.NextRunTime, **kwargs):
        super(RetrieveTagJobs, self).__init__(**kwargs)
        self.tag_id = tag_id
        self._set_properties()

        if self.sort_key not in self.valid_keys_to_sort_by:
            self.sort_key = JobKeys.NextRunTime

        self.fetch_jobs = (
            FetchTagJobs(
                tag_id=self.tag_id, count=self.count, offset=self.offset,
                sort=self.sort, sort_key=self.sort_key
            )
        )

