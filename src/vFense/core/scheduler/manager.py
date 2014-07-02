#!/usr/bin/env python
import logging
import logging.config
from vFense import VFENSE_LOGGING_CONFIG

from datetime import datetime
from pytc import utc, all_timezones
from apscheduler.jobstores.rethinkdb_store import RethinkDBJobStore
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.schedulers.tornado import TornadoScheduler

from vFense.result._constants import ApiResultKeys
from vFense.result.status_codes import (
    DbCodes, GenericCodes, AgentResultCodes, GenericFailureCodes,
    ScheduleCodes, SchedulerFailureCodes
)

logging.config.fileConfig(VFENSE_LOGGING_CONFIG)
logger = logging.getLogger('rvapi')


def start_scheduler(scheduler_type='tornado', db='vFense', collection='jobs'):
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


class JobManager(object):
    def __init__(self, schedule, view_name):
        self.schedule = schedule
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

    def add_yearly_job(self, name, operation, start_date,
                       job, job_kwargs=None, timezone=utc, end_date=None):
        """ Add a job that runs once every year.
        Args:
            name (str): The name of this job.
            operation (str): The operation type.
                Examples.. (install, uninstall, reboot, shutdown)
            start_date (float): The time in seconds (epoch_time)
            job (func): The function that is being scheduled to run.

        Kwargs:
            job_kwargs (dict): The keyword arguments that will be passed
                to the job.
            timezone (str): Valid timezone string.
                default=UTC
            end_date (float): When do you want this job to stop.
                default=None (run for ever).

        Basic Usage:
            >>> from vFense.core.scheduler.manager import JobManager
            >>> view_name = 'global'
            >>> name = 'Install all patches on Tag Apache Every Month at 8:58am'
            >>> operation = 'install'
            >>> start_date = 1404305919.517522
            >>> job = install_patches
            >>> job_kwargs = {'agents': ['agent_id1', 'agent_id2']'}
            >>> timezone = 'US/Eastern'
            >>> manager = JobManager(schedule, view_name)
            >>> job_status = manager.add_yearly_job(name, operation,
                                                    start_date, job,
                                                    job_kwargs, timezone)

        Returns:
        """
        job_status = None
        results = {}
        try:
            if ( isinstance(self.schedule, BackgroundScheduler) or
                    isinstance(self.schedule, TornadoScheduler)):
                if timezone in all_timezones:
                    date=datetime.fromtimestamp(start_date)
                    year = date.year
                    month = date.month
                    day = date.day
                    hour = date.hour
                    minute = date.minute
                    job_status = (
                        self.schedule.add_job(
                            job, 'cron', kwargs=job_kwargs, name=name,
                            view_name=self.view_name, operation=operation,
                            year=year, month=month, day=day, hour=hour,
                            minute=minute
                        )
                    )

                    msg = 'Job {0} added successfully'.format(name)
                    results[ApiResultKeys.GENERIC_STATUS_CODE] = (
                        GenericCodes.ObjectCreated
                    )
                    results[ApiResultKeys.VFENSE_STATUS_CODE] = (
                        SchedulerCodes.ScheduleCreated
                    )
                    results[ApiResultKeys.MESSAGE] = msg
                    results[ApiResultKeys.DATA] = job_kwargs
                    results[ApiResultKeys.GENERATED_IDS] = job_status.id

        except Exception as e:
            logger.exception(e)

        return job_status
