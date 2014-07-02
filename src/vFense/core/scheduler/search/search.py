import logging

from vFense import VFENSE_LOGGING_CONFIG
from vFense.core._constants import SortValues, DefaultQueryValues
from vFense.result._constants import ApiResultKeys

from vFense.core.view._constants import DefaultViews
from vFense.core.agent._constants import AgentCommonKeys
from vFense.core.scheduler._db_model import JobKeys

from vFense.core.scheduler.search._db import FetchJobs
from vFense.core.decorators import time_it
from vFense.result.status_codes import GenericCodes, GenericFailureCodes
from pytz import all_timezones

logging.config.fileConfig(VFENSE_LOGGING_CONFIG)
logger = logging.getLogger('rvapi')


class RetrieveJobs(object):
    def __init__(
        self, view_name=None,
        count=DefaultQueryValues.COUNT,
        offset=DefaultQueryValues.OFFSET,
        sort=SortValues.ASC,
        sort_key=JobKeys.NextRunTime
        ):

        self.view_name = view_name
        self.count = count
        self.offset = offset
        self.sort = sort

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

        valid_keys_to_sort_by = [
            JobKeys.Name, JobKeys.ViewName,
            JobKeys.StartDate, JobKeys.EndDate, JobKeys.TimeZone,
            JobKeys.NextRunTime, JobKeys.Trigger, JobKeys.Operation,
            JobKeys.Runs
        ]

        self.valid_triggers = ['cron', 'interval', 'date']

        if sort_key in valid_keys_to_sort_by:
            self.sort_key = sort_key
        else:
            self.sort_key = JobKeys.NextRunTime

        if self.view_name == DefaultViews.GLOBAL:
            self.view_name = None

        self.fetch_jobs = (
            FetchJobs(
                self.view_name, self.count, self.offset,
                self.sort, self.sort_key
            )
        )

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
        generic_status_code = GenericCodes.InformationRetrieved

        if count == 0:
            vfense_status_code = GenericFailureCodes.DataIsEmpty
            msg = 'dataset is empty'

        else:
            vfense_status_code = GenericCodes.InformationRetrieved
            msg = 'dataset retrieved'

        results = (
            self._set_results(
                generic_status_code, vfense_status_code,
                msg, count, data
            )
        )
        return results

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
        generic_status_code = GenericCodes.InformationRetrieved

        if count == 0:
            vfense_status_code = GenericFailureCodes.DataIsEmpty
            msg = 'dataset is empty'

        else:
            vfense_status_code = GenericCodes.InformationRetrieved
            msg = 'dataset retrieved'

        results = (
            self._set_results(
                generic_status_code, vfense_status_code,
                msg, count, data
            )
        )
        return results

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
            generic_status_code = GenericCodes.InformationRetrieved

            if count == 0:
                vfense_status_code = GenericFailureCodes.DataIsEmpty
                msg = 'dataset is empty'

            else:
                vfense_status_code = GenericCodes.InformationRetrieved
                msg = 'dataset retrieved'
        else:
            count = 0
            data = []
            generic_status_code = GenericFailureCodes.InvalidFilterKey
            vfense_status_code = GenericFailureCodes.InvalidFilterKey
            msg = 'Invalid trigger {0}'.format(trigger)

        results = (
            self._set_results(
                generic_status_code, vfense_status_code,
                msg, count, data
            )
        )
        return results

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
            generic_status_code = GenericCodes.InformationRetrieved

            if count == 0:
                vfense_status_code = GenericFailureCodes.DataIsEmpty
                msg = 'dataset is empty'

            else:
                vfense_status_code = GenericCodes.InformationRetrieved
                msg = 'dataset retrieved'
        else:
            count = 0
            data = []
            generic_status_code = GenericFailureCodes.InvalidFilterKey
            vfense_status_code = GenericFailureCodes.InvalidFilterKey
            msg = 'Invalid timezone {0}'.format(timezone)

        results = (
            self._set_results(
                generic_status_code, vfense_status_code,
                msg, count, data
            )
        )
        return results

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
        generic_status_code = GenericCodes.InformationRetrieved

        if count == 0:
            vfense_status_code = GenericFailureCodes.DataIsEmpty
            msg = 'dataset is empty'

        else:
            vfense_status_code = GenericCodes.InformationRetrieved
            msg = 'dataset retrieved'

        results = (
            self._set_results(
                generic_status_code, vfense_status_code,
                msg, count, data
            )
        )
        return results

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
        generic_status_code = GenericCodes.InformationRetrieved

        if count == 0:
            vfense_status_code = GenericFailureCodes.DataIsEmpty
            msg = 'dataset is empty'

        else:
            vfense_status_code = GenericCodes.InformationRetrieved
            msg = 'dataset retrieved'

        results = (
            self._set_results(
                generic_status_code, vfense_status_code,
                msg, count, data
            )
        )
        return results

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
            generic_status_code = GenericCodes.InformationRetrieved

            if count == 0:
                vfense_status_code = GenericFailureCodes.DataIsEmpty
                msg = 'dataset is empty'

            else:
                vfense_status_code = GenericCodes.InformationRetrieved
                msg = 'dataset retrieved'
        else:
            count = 0
            data = []
            generic_status_code = GenericFailureCodes.InvalidFilterKey
            vfense_status_code = GenericFailureCodes.InvalidFilterKey
            msg = 'Invalid trigger {0}'.format(trigger)

        results = (
            self._set_results(
                generic_status_code, vfense_status_code,
                msg, count, data
            )
        )
        return results

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
            generic_status_code = GenericCodes.InformationRetrieved

            if count == 0:
                vfense_status_code = GenericFailureCodes.DataIsEmpty
                msg = 'dataset is empty'

            else:
                vfense_status_code = GenericCodes.InformationRetrieved
                msg = 'dataset retrieved'
        else:
            count = 0
            data = []
            generic_status_code = GenericFailureCodes.InvalidFilterKey
            vfense_status_code = GenericFailureCodes.InvalidFilterKey
            msg = 'Invalid trigger {0}'.format(trigger)

        results = (
            self._set_results(
                generic_status_code, vfense_status_code,
                msg, count, data
            )
        )
        return results

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
            generic_status_code = GenericCodes.InformationRetrieved

            if count == 0:
                vfense_status_code = GenericFailureCodes.DataIsEmpty
                msg = 'dataset is empty'

            else:
                vfense_status_code = GenericCodes.InformationRetrieved
                msg = 'dataset retrieved'
        else:
            count = 0
            data = []
            generic_status_code = GenericFailureCodes.InvalidFilterKey
            vfense_status_code = GenericFailureCodes.InvalidFilterKey
            msg = 'Invalid trigger {0}'.format(trigger)

        results = (
            self._set_results(
                generic_status_code, vfense_status_code,
                msg, count, data
            )
        )
        return results


    def _set_results(self, gen_status_code, vfense_status_code,
                     msg, count, data):

        results = {
            ApiResultKeys.GENERIC_STATUS_CODE: gen_status_code,
            ApiResultKeys.VFENSE_STATUS_CODE: vfense_status_code,
            ApiResultKeys.MESSAGE: msg,
            ApiResultKeys.COUNT: count,
            ApiResultKeys.DATA: data,
        }

        return(results)
