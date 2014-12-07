from vFense.db.client import r
from vFense.core.scheduler._db_model import (
    JobKeys, JobCollections, JobKwargKeys
)
from vFense.core.scheduler.search._db import FetchJobs

class FetchAgentJobs(FetchJobs):
    """Job database queries for an agent"""
    def __init__(self, agent_id=None, sort_key=JobKeys.NextRunTime, **kwargs):
        self.agent_id = agent_id
        self.sort_key = sort_key
        super(FetchAgentJobs, self).__init__(**kwargs)

    def _set_job_base_query(self):
        base_filter = (
            r
            .table(JobCollections.Jobs)
            .filter(
                lambda x:
                x[JobKeys.Kwargs][JobKwargKeys.Agents].contains(self.agent_id)
            )
        )
        return base_filter
