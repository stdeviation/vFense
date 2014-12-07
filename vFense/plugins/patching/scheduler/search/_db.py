from vFense.db.client import db_create_close, r
from vFense.core.agent._db_model import AgentCollections, AgentKeys
from vFense.core.decorators import catch_it, time_it
from vFense.core.scheduler._db_model import (
    JobKeys, JobCollections
)
from vFense.core.scheduler.search._db import FetchJobs
from vFense.plugins.patching._db_model import AppCollections, AppsKey
from vFense.plugins.patching.scheduler.search._db_model import JobAppKeys

class FetchAppJobs(FetchJobs):
    def __init__(self, sort_key=JobKeys.NextRunTime, **kwargs):
        super(FetchAppJobs, self).__init__(**kwargs)
        self.sort_key = sort_key

    def by_id(self, job_id):
        results = super(FetchAppJobs, self).by_id(job_id)
        self.agent_merge = self._set_agent_and_app_merge_query()
        return results


    def _set_agent_and_app_merge_query(self):
        merge = (
            lambda job:
            {
                JobAppKeys.Agents: (
                    r
                    .expr(
                        job[JobKeys.Kwargs]['agent_ids']
                    )
                    .map(
                        lambda agent_id:
                            r
                            .table(AgentCollections.Agents)
                            .get(agent_id)
                            .pluck(
                                AgentKeys.ComputerName,
                                AgentKeys.AgentId,
                                AgentKeys.DisplayName
                            )
                            .merge(
                                {
                                    JobAppKeys.Applications: (
                                        r
                                        .expr(
                                            job[JobKeys.Kwargs]['app_ids']
                                        )
                                        .map(
                                            lambda app_id:
                                                r
                                                .table(
                                                    AppCollections.UniqueApplications
                                                )
                                                .get(app_id)
                                                .pluck(
                                                    AppsKey.AppId,
                                                    AppsKey.Name,
                                                    AppsKey.Version,
                                                    AppsKey.vFenseSeverity
                                                )
                                        )
                                    )
                                }
                            )
                    )
                )
            }
        )

        return merge

