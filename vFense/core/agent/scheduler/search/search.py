from vFense.core.scheduler._db_model import JobKeys
from vFense.core.agent.scheduler.search._db import FetchAgentJobs
from vFense.core.scheduler.search.search import RetrieveJobs

class RetrieveAgentJobs(RetrieveJobs):
    """Job queries for an agent."""
    def __init__(
        self, agent_id=None, sort_key=JobKeys.NextRunTime, **kwargs
    ):
        super(RetrieveAgentJobs, self).__init__(**kwargs)
        self.agent_id = agent_id
        self._set_properties()

        if self.sort_key not in self.valid_keys_to_sort_by:
            self.sort_key = JobKeys.NextRunTime

        self.fetch_jobs = (
            FetchAgentJobs(
                agent_id=self.agent_id, count=self.count,
                offset=self.offset, sort=self.sort, sort_key=self.sort_key
            )
        )
