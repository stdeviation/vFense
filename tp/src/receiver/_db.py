import logging
import logging.config

from vFense.db.client import r, db_create_close
from vFense.receiver import *

logging.config.fileConfig('/opt/TopPatch/conf/logging.config')
logger = logging.getLogger('rvapi')

@db_create_close
def insert_into_agent_queue(operation, conn=None):
    success = False
    try:
        operation[AgentQueueKey.CreatedTime] = (
            r.epoch_time(operation[AgentQueueKey.CreatedTime])
        )
        operation[AgentQueueKey.ExpireTime] = (
            r.epoch_time(operation[AgentQueueKey.ExpireTime])
        )

        insert = (
            r
            .table(AgentQueueCollection)
            .insert(operation)
            .run(conn)
        )

        if insert.get('inserted') > 0:
            success = True

    except Exception as e:
        logger.exception(e)

    return(success)

@db_create_close
def get_next_avail_order_id_in_agent_queue(agent_id, conn=None):
    last_num_in_queue = 0
    try:
        last_num_in_queue = (
            r
            .table(AgentQueueCollection)
            .get_all(agent_id, index=AgentQueueIndexes.AgentId)
            .count()
            .run(conn)
        )

    except Exception as e:
        logger.exception(e)

    return(last_num_in_queue)


@db_create_close
def get_agent_queue(agent_id, conn=None):
    try:
        agent_queue = list(
            r
            .table(AgentQueueCollection)
            .get_all(agent_id, index=AgentQueueIndexes.AgentId)
            .without(
                AgentQueueKey.CreatedTime,
                AgentQueueKey.ExpireTime
            )
            .run(conn)
        )

    except Exception as e:
        logger.exception(e)

    return(agent_queue)


@db_create_close
def delete_job_in_queue(job_id, conn=None):
    try:
        job_deleted = (
            r
            .table(AgentQueueCollection)
            .get(job_id)
            .delete()
            .run(conn)
        )
        success=True

    except Exception as e:
        logger.exception(e)
        success=False

    return(success)


@db_create_close
def get_all_expired_jobs(now=None, conn=None):
    try:
        if not now:
            expired_jobs = list(
                r
                .table(AgentQueueCollection)
                .filter(
                    lambda x: x[AgentQueueKey.ExpireTime] <= r.now()
                )
                .run(conn)
            )

        else:
            expired_jobs = list(
                r
                .table(AgentQueueCollection)
                .filter(
                    lambda x:
                        x[AgentQueueKey.ExpireTime].to_epoch_time() <= now
                )
                .run(conn)
            )

    except Exception as e:
        logger.exception(e)

    return(expired_jobs)

@db_create_close
def delete_all_expired_jobs(now=None, conn=None):
    jobs_deleted = 0
    try:
        if not now:
            expired_jobs = (
                r
                .table(AgentQueueCollection)
                .filter(
                    lambda x: x[AgentQueueKey.ExpireTime] <= r.now()
                )
                .delete()
                .run(conn)
            )
            jobs_deleted = expired_jobs.get('deleted')

        else:
            expired_jobs = (
                r
                .table(AgentQueueCollection)
                .filter(
                    lambda x:
                        x[AgentQueueKey.ExpireTime].to_epoch_time() <= now
                )
                .delete()
                .run(conn)
            )
            jobs_deleted = expired_jobs.get('deleted')

    except Exception as e:
        logger.exception(e)

    return(jobs_deleted)

@db_create_close
def delete_multiple_jobs(job_ids, conn=None):
    jobs_deleted = 0
    try:
        if isinstance(job_ids, list):
            jobs = (
                r
                .table(AgentQueueCollection)
                .get_all(*job_ids)
                .delete()
                .run(conn)
            )
            jobs_deleted = jobs.get('deleted')

        else:
            jobs = (
                r
                .table(AgentQueueCollection)
                .get(job_ids)
                .delete()
                .run(conn)
            )
            jobs_deleted = jobs.get('deleted')

    except Exception as e:
        logger.exception(e)

    return(jobs_deleted)
