#!/usr/bin/env python
import logging
import logging.config
from vFense._constants import VFENSE_LOGGING_CONFIG

from datetime import datetime
from pytz import utc
from apscheduler.jobstores.rethinkdb import RethinkDBJobStore
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.schedulers.tornado import TornadoScheduler
from apscheduler.schedulers.blocking import BlockingScheduler

from vFense.core.operations._db_model import AgentOperationKey
from vFense.core.scheduler import Schedule
from vFense.core.scheduler._constants import ScheduleTriggers
from vFense.core.scheduler._db import (
    fetch_jobs_by_view, fetch_job_by_name_and_view,
    fetch_admin_jobs_by_view, fetch_admin_job_by_name_and_view
)
from vFense.core.results import ApiResults
from vFense.core.status_codes import (
    GenericCodes, GenericFailureCodes,
)

from vFense.core.scheduler.status_codes import (
    SchedulerCodes, SchedulerFailureCodes
)
logging.config.fileConfig(VFENSE_LOGGING_CONFIG)
logger = logging.getLogger('vfense_api')


def start_scheduler(scheduler_type='background', db='vFense',
                    collection='jobs'):
    """Create an instance of jobManager.
        Args:
            scheduler_type (str): tornado or background.
                default='tornado'
            db (str): The rethinkdb instance to use.
                default='vFense'
            collection (str): The table these jobs will be stored in.
                default='jobs'

    Basic Usage:
        >>> from vFense.core.scheduler.manager import start_scheduler
        >>> sched = start_scheduler()

    Returns:
        Either an active TornadoScheduler or an active BackgroundScheduler.
    """
    if scheduler_type == 'tornado':
        Scheduler = TornadoScheduler

    elif scheduler_type == 'background':
        Scheduler = BackgroundScheduler

    else:
        Scheduler = BlockingScheduler


    jobstore = {
        'default': RethinkDBJobStore(
            database='vFense', table=collection
        )
    }
    job_defaults = {
        'coalesce': True,
        'max_instances': 1,
    }
    sched = (
        Scheduler(
            jobstores=jobstore, job_defaults=job_defaults, timezone=utc
        )
    )
    try:
        sched.start()
    except Exception as e:
        logger.exception(e)
        sched = None

    return sched


def stop_scheduler(sched):
    stopped = False

    try:
        logger.info('Attempting to shutdown the Scheduler')
        sched.shutdown()
        logger.info('Scheduler has shutdown')
        stopped = True

    except Exception as e:
        logger.exception(e)

    return stopped


def restart_scheduler():
    stop = stop_scheduler()
    sched = None

    if stop:
        start = start_scheduler()

        if start:
            sched = start
            logger.info('Scheduler restarted successfully')

    return sched

class InvalidScheduleInstance(Exception):
    pass

class JobManager(object):
    def __init__(self, schedule, view_name):
        """Create an instance of jobManager.
        Args:
            schedule (BackgroundScheduler|TornadoScheduler): The scheduler
                instance, that is currently running the schedules in vFense.
            view_name (str): The name of the view this job belongs too.

        Basic Usage:
            >>> from vFense.core.scheduler.manager import start_scheduler
            >>> sched = start_scheduler()
            >>> view_name = 'global'
            >>> manager = JobManager(sched, view_name)

        Returns:
            JobManager instance
        """
        if (isinstance(schedule, BackgroundScheduler) or
                isinstance(schedule, TornadoScheduler)):
            self.schedule = schedule
        else:
            raise InvalidScheduleInstance(
                'Pass a valid instance of schedule and not {0}'
                .format(type(schedule))
            )

        self.view_name = view_name

    def get_jobs(self, view_name=None):
        if view_name:
            jobs = fetch_jobs_by_view(self.view_name)
        else:
            jobs = fetch_jobs_by_view(self.view_name)

        return jobs

    def job_exist(self, name):
        return fetch_job_by_name_and_view(name, self.view_name)

    def add_cron_job(self, job):
        """Add a scheduled job into vFense.
        Args:
            job (Schedule): The schedule instance with all the attributes,
                of this job.

        Basic Usage:
            >>> from vFense.core.scheduler import Schedule
            >>> from vFense.core.scheduler.manager import JobManager, start_scheduler
            >>> sched = start_scheduler()
            >>> view_name = 'global'
            >>> name = 'Install all patches on Tag Apache Every Month at 8:58am'
            >>> operation = 'install'
            >>> start_date = 1404305919.517522
            >>> fn = install_patches
            >>> job_kwargs = {'agents': ['agent_id1', 'agent_id2']'}
            >>> timezone = 'US/Eastern'
            >>> job = Schedule(name, fn, job_kwargs, start_date,
                               operation=operation, time_zone=timezone,
                               trigger=trigger)
            >>> manager = JobManager(sched, view_name)
            >>> job_status = manager.add_cron_job(job)

        Returns:
            Dictionary of the results.
        """
        results = ApiResults()
        results.fill_in_defaults()
        if isinstance(job, Schedule):
            job.fill_in_defaults()
            if job.trigger == ScheduleTriggers.CRON:
                if job.start_date and not job.minute:
                    date = datetime.fromtimestamp(job.start_date)
                    job.minute = date.minute
                    job.year = date.year
                    job.month = date.month
                    job.day = date.day
                    job.day_of_week = date.isoweekday()

                results = self.add_job(job)
            else:
                msg = (
                    'Invalid {0} Trigger, Trigger must be cron.'
                    .format(job.trigger)
                )
                results.generic_status_code = (
                    GenericFailureCodes.FailedToCreateObject
                )
                results.vfense_status_code = (
                    SchedulerFailureCodes.FailedToCreateSchedule
                )
                results.message = msg

        else:
            msg = (
                'Invalid {0} Instance, must pass an instance of Schedule.'
                .format(type(job))
            )
            results.generic_status_code = (
                GenericFailureCodes.FailedToCreateObject
            )
            results.vfense_status_code = (
                SchedulerFailureCodes.FailedToCreateSchedule
            )
            results.message = msg

        return results

    def add_interval_job(self, job):
        """Add a interval job into vFense.
        Args:
            job (Schedule): The schedule instance with all the attributes,
                of this job.

        Basic Usage:
            >>> from vFense.core.scheduler import Schedule
            >>> from vFense.core.scheduler.manager import JobManager, start_scheduler
            >>> sched = start_scheduler()
            >>> view_name = 'global'
            >>> name = 'Install all patches on Tag Apache Every Month at 8:58am'
            >>> operation = 'install'
            >>> start_date = 1404305919.517522
            >>> fn = install_patches
            >>> job_kwargs = {'agents': ['agent_id1', 'agent_id2']'}
            >>> timezone = 'US/Eastern'
            >>> job = Schedule(name, fn, job_kwargs, start_date,
                               operation=operation, time_zone=timezone,
                               trigger=trigger)
            >>> manager = JobManager(sched, view_name)
            >>> job_status = manager.add_interval_job(job)

        Returns:
            Dictionary of the results.
        """
        results = ApiResults()
        results.fill_in_defaults()
        if isinstance(job, Schedule):
            job.fill_in_defaults()
            if job.trigger == ScheduleTriggers.INTERVAL:
                results = self.add_job(job)
            else:
                msg = (
                    'Invalid {0} Trigger, Trigger must be interval.'
                    .format(job.trigger)
                )
                results.generic_status_code = (
                    GenericFailureCodes.FailedToCreateObject
                )
                results.vfense_status_code = (
                    SchedulerFailureCodes.FailedToCreateSchedule
                )
                results.message = msg

        else:
            msg = (
                'Invalid {0} Instance, must pass an instance of Schedule.'
                .format(type(job))
            )
            results.generic_status_code = (
                GenericFailureCodes.FailedToCreateObject
            )
            results.vfense_status_code = (
                SchedulerFailureCodes.FailedToCreateSchedule
            )
            results.message = msg

        return results


    def add_date_job(self, job):
        """Add a one time job into vFense.
        Args:
            job (Schedule): The schedule instance with all the attributes,
                of this job.

        Basic Usage:
            >>> from vFense.core.scheduler import Schedule
            >>> from vFense.core.scheduler.manager import JobManager, start_scheduler
            >>> sched = start_scheduler()
            >>> view_name = 'global'
            >>> name = 'Install all patches on Tag Apache Every Month at 8:58am'
            >>> operation = 'install'
            >>> start_date = 1404305919.517522
            >>> fn = install_patches
            >>> job_kwargs = {'agents': ['agent_id1', 'agent_id2']'}
            >>> timezone = 'US/Eastern'
            >>> job = Schedule(name, fn, job_kwargs, start_date,
                               operation=operation, time_zone=timezone,
                               trigger=trigger)
            >>> manager = JobManager(sched, view_name)
            >>> job_status = manager.add_date_job(job)

        Returns:
            Dictionary of the results.
        """
        results = ApiResults()
        results.fill_in_defaults()
        if isinstance(job, Schedule):
            job.fill_in_defaults()
            if job.run_date and job.trigger == ScheduleTriggers.DATE:
                results = self.add_job(job)

            else:
                msg = (
                    'Invalid {0} Trigger, Trigger must be a date.'
                    .format(job.trigger)
                )
                results.generic_status_code = (
                    GenericFailureCodes.FailedToCreateObject
                )
                results.vfense_status_code = (
                    SchedulerFailureCodes.FailedToCreateSchedule
                )
                results.message = msg

        else:
            msg = (
                'Invalid {0} Instance, must pass an instance of Schedule.'
                .format(type(job))
            )
            results.generic_status_code = (
                GenericFailureCodes.FailedToCreateObject
            )
            results.vfense_status_code = (
                SchedulerFailureCodes.FailedToCreateSchedule
            )
            results.message = msg

        return results


    def add_job(self, job):
        """Add a scheduled job into vFense.
        Args:
            job (Schedule): The schedule instance with all the attributes,
                of this job.

        Basic Usage:
            >>> from vFense.core.scheduler import Schedule
            >>> from vFense.core.scheduler.manager import JobManager, start_scheduler
            >>> sched = start_scheduler()
            >>> view_name = 'global'
            >>> name = 'Install all patches on Tag Apache Every Month at 8:58am'
            >>> operation = 'install'
            >>> start_date = 1404305919.517522
            >>> fn = install_patches
            >>> job_kwargs = {'agents': ['agent_id1', 'agent_id2']'}
            >>> timezone = 'US/Eastern'
            >>> job = Schedule(name, fn, job_kwargs, start_date,
                               operation=operation, time_zone=timezone,
                               trigger=trigger)
            >>> manager = JobManager(sched, view_name)
            >>> job_status = manager.add_job(job)

        Returns:
            Dictionary of the results.
        """
        job_status = None
        results = ApiResults()
        results.fill_in_defaults()
        try:
            if isinstance(job, Schedule):
                invalid_fields = job.get_invalid_fields()
                if not invalid_fields:
                    job.fill_in_defaults()
                    job.datetime_from_timestamp()
                    if not self.job_exist(job.name):
                        job_status = (
                            self.schedule.add_job(
                                job.fn, view_name=self.view_name,
                                **job.to_dict_non_null()
                            )
                        )
                        job.timestamp_from_datetime()
                        job.job_kwargs[AgentOperationKey.ScheduleId] = (
                            job_status.id
                        )
                        job_status.modify(kwargs=job.job_kwargs)
                        msg = 'Job {0} added successfully'.format(job.name)
                        results.generic_status_code = (
                            GenericCodes.ObjectCreated
                        )
                        results.vfense_status_code = (
                            SchedulerCodes.ScheduleCreated
                        )
                        results.message = msg
                        results.generated_ids.append(job_status.id)
                        results.data.append(job.to_dict_non_null())

                    else:
                        msg = (
                            'Job with name {0} already exist in this view.'
                            .format(job.name)
                        )
                        results.generic_status_code = (
                            GenericCodes.InvalidId
                        )
                        results.vfense_status_code = (
                            SchedulerFailureCodes.ScheduleExistsWithSameName
                        )
                        results.message = msg
                        results.errors = invalid_fields

                else:
                    msg = (
                        'Failed to create job {0}, invalid fields were passed'
                        .format(job.name)
                    )
                    results.generic_status_code = (
                        GenericFailureCodes.FailedToCreateObject
                    )
                    results.vfense_status_code = (
                        SchedulerFailureCodes.FailedToCreateSchedule
                    )
                    results.message = msg
                    results.errors = invalid_fields

            else:
                msg = (
                    'Invalid {0} Instance, must pass an instance of Schedule.'
                    .format(type(job))
                )
                results.generic_status_code = (
                    GenericFailureCodes.FailedToCreateObject
                )
                results.vfense_status_code = (
                    SchedulerFailureCodes.FailedToCreateSchedule
                )
                results.message = msg

        except Exception as e:
            logger.exception(e)
            msg = (
                'Something broke within apscheduler {0}.'.format(e)
            )
            results.generic_status_code = (
                GenericFailureCodes.FailedToCreateObject
            )
            results.vfense_status_code = (
                SchedulerFailureCodes.FailedToCreateSchedule
            )
            results.message = msg

        return results


class AdministrativeJobManager(JobManager):

    def get_jobs(self, view_name=None):
        if view_name:
            jobs = fetch_admin_jobs_by_view(view_name)
        else:
            jobs = fetch_admin_jobs_by_view(self.view_name)

        return jobs

    def job_exist(self, name):
        return fetch_admin_job_by_name_and_view(name, self.view_name)

