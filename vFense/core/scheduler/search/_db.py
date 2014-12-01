from vFense.db.client import db_create_close, r
from vFense.core.agent._db_model import AgentCollections, AgentKeys
from vFense.core.decorators import catch_it, time_it
from vFense.core.scheduler._db_model import (
    JobKeys, JobCollections, JobKwargKeys
)
from vFense.search._db_base import FetchBase

class FetchJobs(FetchBase):
    """Job database queries."""
    def __init__(self, sort_key=JobKeys.NextRunTime, **kwargs):
        super(FetchJobs, self).__init__(**kwargs)
        self.sort_key = sort_key
        self.keys_to_pluck = [
            JobKeys.Id, JobKeys.Name, JobKeys.ViewName,
            JobKeys.StartDate, JobKeys.TimeZone, JobKeys.EndDate,
            JobKeys.NextRunTime, JobKeys.Trigger, JobKeys.Operation,
            JobKeys.Runs
        ]
        self.base_filter = self._set_job_base_query()
        self.merge_query = self._set_merge_query()

    @time_it
    @catch_it((0, []))
    @db_create_close
    def by_id(self, job_id, conn=None):
        """Retrieve a job by its id and all of its properties.

        Basic Usage:
            >>> from vFense.job.search._db import FetchJobs
            >>> search = FetchJobs()
            >>> search.by_id('96f02bcf-2ada-465c-b175-0e5163b36e1c')

        Returns:
            Tuple
            (count, job_data)
        >>>
        """
        agent_merge = self._set_agent_merge_query()
        count = 0
        data = []
        count = (
            self.base_filter
            .get_all(job_id)
            .count()
            .run(conn)
        )

        data = (
            self.base_filter
            .get(job_id)
            .merge(self.merge_query)
            .merge(agent_merge)
            .run(conn)
        )

        return(count, data)

    @time_it
    @catch_it((0, []))
    @db_create_close
    def all(self, conn=None):
        """Retrieve all jobs and its properties.

        Basic Usage:
            >>> from vFense.job.search._db import FetchJobs
            >>> search = FetchJobs()
            >>> search.all()

        Returns:
            Tuple
            (count, job_data)
        >>>
        """
        count = 0
        data = []
        count = (
            self.base_filter
            .count()
            .run(conn)
        )

        data = (
            self.base_filter
            .order_by(self.sort(self.sort_key))
            .skip(self.offset)
            .limit(self.count)
            .merge(self.merge_query)
            .pluck(self.keys_to_pluck)
            .run(conn)
        )

        return(count, data)

    @time_it
    @catch_it((0, []))
    @db_create_close
    def by_trigger(self, trigger, conn=None):
        """Retrieve all jobs by trigger and its properties.
        Args:
            trigger (str): The type of job. Example (cron, interval, date)

        Basic Usage:
            >>> from vFense.job.search._db import FetchJobs
            >>> search = FetchJobs()
            >>> search.by_trigger('cron')

        Returns:
            Tuple
            (count, job_data)
        >>>
        """
        count = 0
        data = []
        count = (
            self.base_filter
            .filter({JobKeys.Trigger: trigger})
            .count()
            .run(conn)
        )

        data = (
            self.base_filter
            .filter({JobKeys.Trigger: trigger})
            .order_by(self.sort(self.sort_key))
            .skip(self.offset)
            .limit(self.count)
            .merge(self.merge_query)
            .pluck(self.keys_to_pluck)
            .run(conn)
        )

        return(count, data)

    @time_it
    @catch_it((0, []))
    @db_create_close
    def by_timezone(self, time_zone, conn=None):
        """Retrieve all jobs by time zone and its properties.
        Args:
            time_zone (str): the string representation of a time zone.
                examples (US/Eastern, UTC, EST5EDT)

        Basic Usage:
            >>> from vFense.job.search._db import FetchJobs
            >>> search = FetchJobs()
            >>> search.by_timezone('US/Eastern')

        Returns:
            Tuple
            (count, job_data)
        >>>
        """
        count = 0
        data = []
        count = (
            self.base_filter
            .filter({JobKeys.TimeZone: time_zone})
            .count()
            .run(conn)
        )

        data = (
            self.base_filter
            .filter({JobKeys.TimeZone: time_zone})
            .order_by(self.sort(self.sort_key))
            .skip(self.offset)
            .limit(self.count)
            .merge(self.merge_query)
            .pluck(self.keys_to_pluck)
            .run(conn)
        )

        return(count, data)

    @time_it
    @catch_it((0, []))
    @db_create_close
    def by_name(self, name, conn=None):
        """Retrieve all jobs by regular expression on the name of the job.
        Args:
            name (str): The regex used to search.

        Basic Usage:
            >>> from vFense.job.search._db import FetchJobs
            >>> search = FetchJobs()
            >>> search.by_name('^install')

        Returns:
            Tuple
            (count, job_data)
        >>>
        """
        count = 0
        data = []
        count = (
            self.base_filter
            .filter(lambda x: x[JobKeys.Name].match(name))
            .count()
            .run(conn)
        )

        data = (
            self.base_filter
            .filter(lambda x: x[JobKeys.Name].match(name))
            .order_by(self.sort(self.sort_key))
            .skip(self.offset)
            .limit(self.count)
            .merge(self.merge_query)
            .pluck(self.keys_to_pluck)
            .run(conn)
        )

        return(count, data)

    @time_it
    @catch_it((0, []))
    @db_create_close
    def by_operation(self, operation, conn=None):
        """Retrieve all jobs by the operation type
        Args:
            operation (str): Example (install, reboot, shutdown, uninstall)

        Basic Usage:
            >>> from vFense.job.search._db import FetchJobs
            >>> search = FetchJobs()
            >>> search.by_operation('install')

        Returns:
            Tuple
            (count, job_data)
        >>>
        """
        count = 0
        data = []
        count = (
            self.base_filter
            .filter({JobKeys.Operation: operation})
            .count()
            .run(conn)
        )

        data = (
            self.base_filter
            .filter({JobKeys.Operation: operation})
            .order_by(self.sort(self.sort_key))
            .skip(self.offset)
            .limit(self.count)
            .merge(self.merge_query)
            .pluck(self.keys_to_pluck)
            .run(conn)
        )

        return(count, data)

    @time_it
    @catch_it((0, []))
    @db_create_close
    def by_agentid(self, agent_id, conn=None):
        """Retrieve all jobs for an agent.
        Args:
            agent_id (str): The id of the agent.

        Basic Usage:
            >>> from vFense.job.search._db import FetchJobs
            >>> search = FetchJobs()
            >>> search.by_agentid('96f02bcf-2ada-465c-b175-0e5163b36e1c')

        Returns:
            Tuple
            (count, job_data)
        >>>
        """
        count = 0
        data = []
        count = (
            self.base_filter
            .filter(
                lambda x:
                x[JobKeys.Kwargs][JobKwargKeys.Agents].contains(agent_id)
            )
            .count()
            .run(conn)
        )

        data = (
            self.base_filter
            .filter(
                lambda x:
                x[JobKeys.Kwargs][JobKwargKeys.Agents].contains(agent_id)
            )
            .order_by(self.sort(self.sort_key))
            .skip(self.offset)
            .limit(self.count)
            .merge(self.merge_query)
            .pluck(self.keys_to_pluck)
            .run(conn)
        )

        return(count, data)

    @time_it
    @catch_it((0, []))
    @db_create_close
    def by_tagid(self, tag_id, conn=None):
        """Retrieve all jobs for a tag.
        Args:
            tag_id (str): The id of the tag.

        Basic Usage:
            >>> from vFense.job.search._db import FetchJobs
            >>> search = FetchJobs()
            >>> search.by_tagid('96f02bcf-2ada-465c-b175-0e5163b36e1c')

        Returns:
            Tuple
            (count, job_data)
        >>>
        """
        count = 0
        data = []
        count = (
            self.base_filter
            .filter(
                lambda x:
                x[JobKeys.Kwargs][JobKwargKeys.Tags].contains(tag_id)
            )
            .count()
            .run(conn)
        )

        data = (
            self.base_filter
            .filter(
                lambda x:
                x[JobKeys.Kwargs][JobKwargKeys.Tags].contains(tag_id)
            )
            .order_by(self.sort(self.sort_key))
            .skip(self.offset)
            .limit(self.count)
            .merge(self.merge_query)
            .pluck(self.keys_to_pluck)
            .run(conn)
        )

        return(count, data)

    @time_it
    @catch_it((0, []))
    @db_create_close
    def by_name_and_trigger(self, name, trigger, conn=None):
        """Retrieve all jobs by regular expression on the name of the job.
        Args:
            name (str): The regex used to search.
            trigger (str): The type of job. Example (cron, interval, date)

        Basic Usage:
            >>> from vFense.job.search._db import FetchJobs
            >>> search = FetchJobs()
            >>> search.by_name_and_trigger('^install', 'interval')

        Returns:
            Tuple
            (count, job_data)
        >>>
        """
        count = 0
        data = []
        count = (
            self.base_filter
            .filter({JobKeys.Trigger: trigger})
            .filter(lambda x: x[JobKeys.Name].match(name))
            .count()
            .run(conn)
        )

        data = (
            self.base_filter
            .filter({JobKeys.Trigger: trigger})
            .filter(lambda x: x[JobKeys.Name].match(name))
            .order_by(self.sort(self.sort_key))
            .skip(self.offset)
            .limit(self.count)
            .merge(self.merge_query)
            .pluck(self.keys_to_pluck)
            .run(conn)
        )

        return(count, data)

    @time_it
    @catch_it((0, []))
    @db_create_close
    def by_operation_and_trigger(self, operation, trigger, conn=None):
        """Retrieve all jobs by operation and trigger.
        Args:
            operation (str): The operation type.
                (install, uninstall, reboot, shutdown)
            trigger (str): The type of job. Example (cron, interval, date)

        Basic Usage:
            >>> from vFense.job.search._db import FetchJobs
            >>> search = FetchJobs()
            >>> search.by_operation_and_trigger('install', 'interval')

        Returns:
            Tuple
            (count, job_data)
        >>>
        """
        count = 0
        data = []
        count = (
            self.base_filter
            .filter(
                {
                    JobKeys.Trigger: trigger,
                    JobKeys.Operation: operation,
                }
            )
            .count()
            .run(conn)
        )

        data = (
            self.base_filter
            .filter(
                {
                    JobKeys.Trigger: trigger,
                    JobKeys.Operation: operation,
                }
            )
            .order_by(self.sort(self.sort_key))
            .skip(self.offset)
            .limit(self.count)
            .merge(self.merge_query)
            .pluck(self.keys_to_pluck)
            .run(conn)
        )

        return(count, data)

    @time_it
    @catch_it((0, []))
    @db_create_close
    def by_name_and_trigger_and_operation(self, name, trigger,
                                          operation, conn=None):
        """Retrieve all jobs by regular expression on the name of the job.
        Args:
            name (str): The regex used to search.
            trigger (str): The type of job. Example (cron, interval, date)
            operation (str): The operation type.
                (install, uninstall, reboot, shutdown)

        Basic Usage:
            >>> from vFense.job.search._db import FetchJobs
            >>> search = FetchJobs()
            >>> search.by_name_and_trigger_and_operation(
                    'install critical apps', 'interval', 'install'
                )

        Returns:
            Tuple
            (count, job_data)
        >>>
        """
        count = 0
        data = []
        count = (
            self.base_filter
            .filter(
                {
                    JobKeys.Trigger: trigger,
                    JobKeys.Operation: operation,
                }
            )
            .filter(lambda x: x[JobKeys.Name].match(name))
            .count()
            .run(conn)
        )

        data = (
            self.base_filter
            .filter(
                {
                    JobKeys.Trigger: trigger,
                    JobKeys.Operation: operation,
                }
            )
            .filter(lambda x: x[JobKeys.Name].match(name))
            .order_by(self.sort(self.sort_key))
            .skip(self.offset)
            .limit(self.count)
            .merge(self.merge_query)
            .pluck(self.keys_to_pluck)
            .run(conn)
        )

        return(count, data)

    def _set_job_base_query(self):
        base_filter = (
            r
            .table(JobCollections.Jobs)
        )
        if self.view_name:
            base_filter = (
                r
                .table(JobCollections.Jobs)
                .get_all(
                    self.view_name,
                    index=JobKeys.ViewName
                )
            )

        return base_filter

    def _set_merge_query(self):
        merge = (
            lambda job:
            {
                JobKeys.NextRunTime: job[JobKeys.NextRunTime].to_epoch_time(),
                JobKeys.StartDate: job[JobKeys.StartDate].to_epoch_time(),
                JobKeys.CreatedTime: job[JobKeys.CreatedTime].to_epoch_time(),
                JobKeys.EndDate: (
                    r
                    .branch(
                        job.has_fields(JobKeys.EndDate),
                        job[JobKeys.EndDate].to_epoch_time(),
                        job[JobKeys.StartDate].to_epoch_time()
                    )
                )
            }
        )

        return merge

    def _set_agent_merge_query(self):
        merge = (
            lambda job:
            {
                JobKwargKeys.Agents: (
                    job[JobKeys.Kwargs]['agent_ids'].do(
                        lambda agent_id:
                            r
                            .table(AgentCollections.Agents)
                            .get(agent_id)
                            .pluck(
                                AgentKeys.ComputerName,
                                AgentKeys.AgentId,
                                AgentKeys.DisplayName
                            )
                    )
                )
            }
        )

        return merge


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
