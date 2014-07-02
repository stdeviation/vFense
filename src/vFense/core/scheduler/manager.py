#!/usr/bin/env python
import logging
import logging.config
from vFense import VFENSE_LOGGING_CONFIG

from datetime import datetime
from pytc import utc
from apscheduler.jobstores.rethinkdb_store import RethinkDBJobStore
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.schedulers.tornado import TornadoScheduler

from vFense.core.scheduler import Schedule
from vFense.result._constants import ApiResultKeys
from vFense.result.status_codes import (
    GenericCodes, GenericFailureCodes,
    SchedulerCodes, SchedulerFailureCodes
)

logging.config.fileConfig(VFENSE_LOGGING_CONFIG)
logger = logging.getLogger('rvapi')


def start_scheduler(scheduler_type='tornado', db='vFense', collection='jobs'):
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
    else:
        Scheduler = BackgroundScheduler


    jobstore = {'default': RethinkDBJobStore(table=collection)}
    job_defaults = {'coalesce': True}
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
        logger.error('Failed to shutdown the Scheduler')

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
        self.jobs = self.get_jobs(view_name)

    def get_jobs(self, view_name=None):
        if view_name:
            jobs = self.schedule.get_jobs(name=view_name)
        else:
            jobs = self.schedule.get_jobs(name=self.view_name)

        return jobs

    def job_exist(self, name):
        pass

    def add_yearly_job(self, job):
        """ Add a job that runs once every year.
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
            >>> job_status = manager.add_yearly_job(job)

        Returns:
            Dictionary of the results.
        """
        job_status = None
        results = {}
        try:
            if isinstance(job, Schedule):
                invalid_fields = job.get_invalid_fields()
                if not invalid_fields:
                    job.fill_in_defaults()
                    date=datetime.fromtimestamp(job.start_date)
                    year = date.year
                    month = date.month
                    day = date.day
                    hour = date.hour
                    minute = date.minute
                    job_status = (
                        self.schedule.add_job(
                            job.fn, kwargs=job.job_kwargs,
                            name=job.name, view_name=self.view_name,
                            operation=job.operation,
                            year=year, month=month, day=day, hour=hour,
                            minute=minute, timezone=job.time_zone
                        )
                    )

                    msg = 'Job {0} added successfully'.format(job.name)
                    results[ApiResultKeys.GENERIC_STATUS_CODE] = (
                        GenericCodes.ObjectCreated
                    )
                    results[ApiResultKeys.VFENSE_STATUS_CODE] = (
                        SchedulerCodes.ScheduleCreated
                    )
                    results[ApiResultKeys.MESSAGE] = msg
                    results[ApiResultKeys.GENERATED_IDS] = job_status.id

                else:
                    msg = (
                        'Failed to create job {0}, invalid fields were passed'
                        .format(job.name)
                    )
                    results[ApiResultKeys.GENERIC_STATUS_CODE] = (
                        GenericFailureCodes.FailedToCreateObject
                    )
                    results[ApiResultKeys.VFENSE_STATUS_CODE] = (
                        SchedulerFailureCodes.FailedToCreateSchedule
                    )
                    results[ApiResultKeys.MESSAGE] = msg
                    results[ApiResultKeys.ERRORS] = invalid_fields

            else:
                msg = (
                    'Invalid {0} Instance, must pass an instance of Schedule.'
                    .format(type(job))
                )
                results[ApiResultKeys.GENERIC_STATUS_CODE] = (
                    GenericFailureCodes.FailedToCreateObject
                )
                results[ApiResultKeys.VFENSE_STATUS_CODE] = (
                    SchedulerFailureCodes.FailedToCreateSchedule
                )
                results[ApiResultKeys.MESSAGE] = msg


        except Exception as e:
            logger.exception(e)
            msg = (
                'Something broke within apscheduler {0}.'.format(e)
            )
            results[ApiResultKeys.GENERIC_STATUS_CODE] = (
                GenericFailureCodes.FailedToCreateObject
            )
            results[ApiResultKeys.VFENSE_STATUS_CODE] = (
                SchedulerFailureCodes.FailedToCreateSchedule
            )
            results[ApiResultKeys.MESSAGE] = msg

        return results
