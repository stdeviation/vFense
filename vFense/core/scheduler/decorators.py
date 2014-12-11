from functools import wraps
from vFense.core.scheduler._db_history import (
    insert_historical_job_by_job_id, update_historical_job_by_job_id
)

def add_to_job_history(fn):
    """add the newly created job into the job_history collection"""
    def db_wrapper(*args, **kwargs):
        output = fn(*args, **kwargs)
        if output.generated_ids:
            insert_historical_job_by_job_id(output.generated_ids[0])
        return(output)

    return wraps(fn)(db_wrapper)

def update_job_history(fn):
    """Update a job in the job_history collection"""
    def db_wrapper(*args, **kwargs):
        output = fn(*args, **kwargs)
        if output.generated_ids:
            update_historical_job_by_job_id(output.generated_ids[0])
        return(output)

    return wraps(fn)(db_wrapper)
