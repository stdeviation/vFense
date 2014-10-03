import logging, logging.config
from vFense import VFENSE_LOGGING_CONFIG
from vFense.db.client import db_create_close, r
from vFense.core.scheduler._db_model import (
    JobCollections, JobKeys, JobIndexes
)
from vFense.core._db import (
    retrieve_collections, create_collection, retrieve_indexes
)

logging.config.fileConfig(VFENSE_LOGGING_CONFIG)
logger = logging.getLogger('rvapi')

def initialize_collections(collection, current_collections):
    name, key = collection
    if name not in current_collections:
        create_collection(name, key)

@db_create_close
def initialize_job_indexes(collection, indexes, conn=None):
    if not JobIndexes.ViewName in indexes:
        (
            r
            .table(collection)
            .index_create(
                JobIndexes.ViewName
            )
            .run(conn)
        )

    if not JobIndexes.NextRunTime in indexes:
        (
            r
            .table(collection)
            .index_create(
                JobIndexes.NextRunTime
            )
            .run(conn)
        )


try:
    job_collections = [
        (JobCollections.Jobs, JobKeys.Id),
        (JobCollections.AdministrativeJobs, JobKeys.Id),
    ]
    current_collections = retrieve_collections()
    for collection in job_collections:
        initialize_collections(collection, current_collections)
        name, _ = collection
        indexes = retrieve_indexes(name)
        initialize_job_indexes(name, indexes)

except Exception as e:
    logger.exception(e)
