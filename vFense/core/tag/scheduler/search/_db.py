from vFense.db.client import r
from vFense.core.scheduler._db_model import (
    JobKeys, JobCollections, JobKwargKeys
)
from vFense.core.scheduler.search._db import FetchJobs

class FetchTagJobs(FetchJobs):
    """Job database queries for a tag"""
    def __init__(self, tag_id=None, sort_key=JobKeys.NextRunTime, **kwargs):
        self.tag_id = tag_id
        self.sort_key = sort_key
        super(FetchTagJobs, self).__init__(**kwargs)

    def _set_job_base_query(self):
        base_filter = (
            r
            .table(JobCollections.Jobs)
            .filter(
                lambda x:
                x[JobKeys.Kwargs][JobKwargKeys.Tags].contains(self.tag_id)
            )
        )
        return base_filter
