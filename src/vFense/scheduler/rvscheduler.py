from time import sleep
import logging

from vFense import VFENSE_LOGGING_CONFIG
from vFense.core.view._constants import DefaultViews
from vFense.core.scheduler import Schedule
from vFense.core.scheduler._db_model import JobCollections
from vFense.core.scheduler.manager import (
    start_scheduler, AdministrativeJobManager
)
from vFense.plugins.vuln.cve.parser import parse_cve_and_udpatedb
from vFense.plugins.vuln.windows.parser import parse_bulletin_and_updatedb
from vFense.plugins.vuln.ubuntu.parser import begin_usn_home_page_processing

from vFense.core.agent.agent_uptime_verifier import all_agent_status
from vFense.jobs.jobs import remove_expired_jobs_and_update_operations

logging.config.fileConfig(VFENSE_LOGGING_CONFIG)
logger = logging.getLogger('admin_scheduler')

if __name__ == '__main__':

    sched = start_scheduler(collection=JobCollections.AdministrativeJobs)
    list_of_cron_jobs = [
        {
            'name': 'parse_cve_and_udpatedb',
            'operation': 'parse_cve_and_udpatedb',
            'fn': parse_cve_and_udpatedb,
            'hour': '1,7,13',
            'minute': 5,
            'trigger': 'cron'
        },
        {
            'name': 'parse_bulletin_and_updatedb',
            'operation': 'parse_bulletin_and_updatedb',
            'fn': parse_bulletin_and_updatedb,
            'hour': '0,12',
            'minute': 0,
            'trigger': 'cron'
        },
        {
            'name': 'begin_usn_home_page_processing',
            'operation': 'begin_usn_home_page_processing',
            'fn': begin_usn_home_page_processing,
            'hour': '0,6,12',
            'minute': 30,
            'trigger': 'cron'
        },
        {
            'name': 'all_agent_status',
            'operation': 'all_agent_status',
            'fn': all_agent_status,
            'hour': '*',
            'minute': '*/5',
            'trigger': 'cron'
        },
        {
            'name': 'remove_expired_jobs_and_update_operations',
            'operation': 'remove_expired_jobs_and_update_operations',
            'fn': remove_expired_jobs_and_update_operations,
            'hour': '*',
            'minute': '*',
            'trigger': 'cron'
        },
    ]
    manager = AdministrativeJobManager(sched, DefaultViews.GLOBAL)
    for cron_job in list_of_cron_jobs:
        job = Schedule(**cron_job)
        manager.add_cron_job(job)
        logger.info('job %s added' % (job.name))

    while True:
        sleep(60)
