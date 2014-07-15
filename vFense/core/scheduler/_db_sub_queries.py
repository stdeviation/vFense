from vFense.db.client import r
from vFense.core.scheduler._db_model import JobKeys


def job_get_merge():
    merge = (
        lambda job:
        {
            JobKeys.NextRunTime: job[JobKeys.NextRunTime].to_epoch_time(),
            JobKeys.StartDate: job[JobKeys.StartDate].to_epoch_time(),
            JobKeys.EndDate: (
                r
                .branch(
                    job[JobKeys.EndDate] != None,
                    job[JobKeys.EndDate].to_epoch_time(),
                    None
                )
            )
        }
    )

    return merge
