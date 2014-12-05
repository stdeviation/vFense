import logging, logging.config
from vFense._constants import VFENSE_LOGGING_CONFIG
from vFense.db.client import r
from vFense.db.manager import DbInit
from vFense.core.scheduler._db_model import (
    JobCollections, JobKeys, JobIndexes
)

logging.config.fileConfig(VFENSE_LOGGING_CONFIG)
logger = logging.getLogger('vfense_api')

collections = [
    (JobCollections.Jobs, JobKeys.Id),
    (JobCollections.AdministrativeJobs, JobKeys.Id),
]

secondary_indexes = [
    (
        JobCollections.Jobs,
        JobIndexes.ViewName,
        (
            r
            .table(JobCollections.Jobs)
            .index_create(JobIndexes.ViewName)
        )
    ),
    (
        JobCollections.Jobs,
        JobIndexes.NextRunTime,
        (
            r
            .table(JobCollections.Jobs)
            .index_create(JobIndexes.NextRunTime)
        )
    )
]


try:
    db = DbInit()
    db.initialize(collections, secondary_indexes)

except Exception as e:
    logger.exception(e)
