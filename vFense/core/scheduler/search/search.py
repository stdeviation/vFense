from vFense.core.scheduler._db_model import JobKeys
from vFense.core.scheduler.search._db import (
    FetchJobs, FetchAgentJobs, FetchTagJobs
)
from vFense.core.decorators import time_it
from pytz import all_timezones
from vFense.search.base import RetrieveBase


class RetrieveJobs(RetrieveBase):
    """Job database queries."""
    def __init__(self, sort_key=JobKeys.NextRunTime, **kwargs):
        super(RetrieveJobs, self).__init__(**kwargs)
        self._set_properties()


        if self.sort_key not in self.valid_keys_to_sort_by:
            self.sort_key = JobKeys.NextRunTime

        self.fetch_jobs = (
            FetchJobs(
                view_name=self.view_name, count=self.count,
                offset=self.offset, sort=self.sort, sort_key=self.sort_key
            )
        )

    def _set_properties(self):
        self.list_of_valid_keys = [
            JobKeys.Id, JobKeys.Name, JobKeys.ViewName,
            JobKeys.StartDate, JobKeys.EndDate, JobKeys.TimeZone,
            JobKeys.NextRunTime, JobKeys.Trigger, JobKeys.Operation,
            JobKeys.Runs, JobKeys.Kwargs, JobKeys.Args
        ]

        self.valid_keys_to_filter_by = [
            JobKeys.Name, JobKeys.ViewName,
            JobKeys.StartDate, JobKeys.EndDate, JobKeys.TimeZone,
            JobKeys.NextRunTime, JobKeys.Trigger, JobKeys.Operation,
        ]

        self.valid_keys_to_sort_by = [
            JobKeys.Name, JobKeys.ViewName,
            JobKeys.StartDate, JobKeys.EndDate, JobKeys.TimeZone,
            JobKeys.NextRunTime, JobKeys.Trigger, JobKeys.Operation,
            JobKeys.Runs
        ]

        self.valid_triggers = ['cron', 'interval', 'date']

    @time_it
    def by_id(self, job_id):
        """Retrieve job by its primary key.
        Args:
            job_id (str): The 36 character UUID of the job you are retrieving.

        Basic Usage:
            >>> from vFense.core.scheduler.search.search import RetrieveJobs
            >>> view_name = 'global'
            >>> search = RetrieveJobs(view_name='default')
            >>> search.by_id('74b70fcd-9ed5-4cfd-9779-a45d60478aa3')

        Returns:
            List of dictionairies.
        """
        count, data = self.fetch_jobs.by_id(job_id)
        return self._base(count, data)

    @time_it
    def all(self):
        """Retrieve all jobs.
        Basic Usage:
            >>> from vFense.core.scheduler.search.search import RetrieveJobs
            >>> view_name = 'global'
            >>> search = RetrieveJobs(view_name='default')
            >>> search.all()

        Returns:
            List of dictionairies.
        """
        count, data = self.fetch_jobs.all()
        return self._base(count, data)

    @time_it
    def by_trigger(self, trigger):
        """Retrieve all jobs by trigger and its properties.
        Args:
            trigger (str): The type of job. Example (cron, interval, date)

        Basic Usage:
            >>> from vFense.core.scheduler.search.search import RetrieveJobs
            >>> view_name = 'global'
            >>> search = RetrieveJobs(view_name='default')
            >>> search.trigger('cron')

        Returns:
            List of dictionairies.
        """
        if trigger in self.valid_triggers:
            count, data = self.fetch_jobs.by_trigger(trigger)
            return self._base(count, data)

        else:
            return self._set_results_invalid_filter_key(trigger)

    @time_it
    def by_timezone(self, timezone):
        """Retrieve all jobs by time zone and its properties.
        Args:
            time_zone (str): the string representation of a time zone.
                examples (US/Eastern, UTC, EST5EDT)

        Basic Usage:
            >>> from vFense.core.scheduler.search.search import RetrieveJobs
            >>> view_name = 'global'
            >>> search = RetrieveJobs(view_name='default')
            >>> search.timezone('UTC')

        Returns:
            List of dictionairies.
        """
        if timezone in all_timezones:
            count, data = self.fetch_jobs.by_timezone(timezone)
            return self._base(count, data)
        else:
            return self._set_results_invalid_filter_key(timezone)

    @time_it
    def by_name(self, name):
        """Retrieve all jobs by regular expression on the name of the job.
        Args:
            name (str): The regex used to search.

        Basic Usage:
            >>> from vFense.core.scheduler.search.search import RetrieveJobs
            >>> view_name = 'global'
            >>> search = RetrieveJobs(view_name='default')
            >>> search.by_name('install$')

        Returns:
            List of dictionairies.
        """
        count, data = self.fetch_jobs.by_name(name)
        return self._base(count, data)

    @time_it
    def by_operation(self, operation):
        """Retrieve all jobs by operation type.
        Args:
            operation (str): Example (install, reboot, shutdown, uninstall)

        Basic Usage:
            >>> from vFense.core.scheduler.search.search import RetrieveJobs
            >>> view_name = 'global'
            >>> search = RetrieveJobs(view_name='default')
            >>> search.by_operation('install')

        Returns:
            List of dictionairies.
        """
        count, data = self.fetch_jobs.by_operation(operation)
        return self._base(count, data)

    @time_it
    def by_name_and_trigger(self, name, trigger):
        """Retrieve all jobs by regular expression on the name of the job.
        Args:
            name (str): The regex used to search.
            trigger (str): The type of job. Example (cron, interval, date)

        Basic Usage:
            >>> from vFense.core.scheduler.search.search import RetrieveJobs
            >>> view_name = 'global'
            >>> search = RetrieveJobs(view_name='default')
            >>> search.by_name_and_trigger('^install', 'interval')

        Returns:
            List of dictionairies.
        """
        if trigger in self.valid_triggers:
            count, data = self.fetch_jobs.by_name_and_trigger(name, trigger)
            return self._base(count, data)

        else:
            return self._set_results_invalid_filter_key(trigger)

    @time_it
    def by_operation_and_trigger(self, operation, trigger):
        """Retrieve all jobs by operation and trigger.
        Args:
            operation (str): The operation type.
                (install, uninstall, reboot, shutdown)
            trigger (str): The type of job. Example (cron, interval, date)

        Basic Usage:
            >>> from vFense.core.scheduler.search.search import RetrieveJobs
            >>> view_name = 'global'
            >>> search = RetrieveJobs(view_name='default')
            >>> search.by_operation_and_trigger('install', 'interval')

        Returns:
            List of dictionairies.
        """
        if trigger in self.valid_triggers:
            count, data = (
                self.fetch_jobs.by_operation_and_trigger(operation, trigger)
            )
            return self._base(count, data)

        else:
            return self._set_results_invalid_filter_key(trigger)

    @time_it
    def by_name_and_trigger_and_operation(self, name, trigger, operation):
        """Retrieve all jobs by regular expression on the name of the job.
        Args:
            name (str): The regex used to search.
            trigger (str): The type of job. Example (cron, interval, date)
            operation (str): The operation type.
                (install, uninstall, reboot, shutdown)

        Basic Usage:
            >>> from vFense.core.scheduler.search.search import RetrieveJobs
            >>> view_name = 'global'
            >>> search = RetrieveJobs(view_name='default')
            >>> search.by_name_and_trigger_and_operation(
                'install sev patches', 'install', 'interval'
            )

        Returns:
            List of dictionairies.
        """
        if trigger in self.valid_triggers:
            count, data = (
                self.fetch_jobs.by_name_and_trigger_and_operation(
                    name, trigger, operation)
            )
            return self._base(count, data)

        else:
            return self._set_results_invalid_filter_key(trigger)

    @time_it
    def by_agentid(self, agent_id):
        """Retrieve all jobs for an agent.
        Args:
            agent_id (str): The id of the agent you are retrieving
                the jobs for.

        Basic Usage:
            >>> from vFense.core.scheduler.search.search import RetrieveJobs
            >>> view_name = 'global'
            >>> search = RetrieveJobs(view_name='default')
            >>> search.by_agentid('96f02bcf-2ada-465c-b175-0e5163b36e1c')

        Returns:
            List of dictionairies.
        """
        count, data = self.fetch_jobs.by_agentid(agent_id)
        return self._base(count, data)

    @time_it
    def by_tagid(self, tag_id):
        """Retrieve all jobs for an agent.
        Args:
            tag_id (str): The id of the tag you are retrieving
                the jobs for.

        Basic Usage:
            >>> from vFense.core.scheduler.search.search import RetrieveJobs
            >>> view_name = 'global'
            >>> search = RetrieveJobs(view_name='default')
            >>> search.by_tagid('96f02bcf-2ada-465c-b175-0e5163b36e1c')

        Returns:
            List of dictionairies.
        """
        count, data = self.fetch_jobs.by_tagid(tag_id)
        return self._base(count, data)


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

