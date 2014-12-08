from vFense.core._db import (
    insert_data_in_table, delete_data_in_table,
    update_data_in_table
)
from vFense.core.decorators import catch_it, time_it
from vFense.core.scheduler._db_history_model import (
    JobCollections, JobHistoryKeys, JobHistoryIndexes
)
from vFense.core.scheduler._db_history_sub_queries import (
    job_get_merge
)
from vFense.db.client import r, db_create_close


@time_it
@catch_it({})
@db_create_close
def fetch_historical_job(job_id, conn=None):
    """Fetch all information about a job
    Args:
        job_id (str): the primary id of the job.

    Basic Usage:
        >>> from vFense.core.scheduler._db_history import fetch_job
        >>> job_info = fetch_job('job_id')

    Returns:
    >>>
        {
            "next_run_time": 1404262689.472,
            "misfire_grace_time": 1,
            "end_date": null,
            "job_state": "eJxFUU1PGzEQTUKa3bik4bPfHxQ4kEuUooVQTpV6qKpIPUTM2fLas7sWGy/j9YaAFKm9UH4fP4Df\nwm4CrQ+jJ8+z37w3vxtzqh9AU9g4p0YPfJyhLFxmaQU8hZEoUkdN6EzEjGuTO2Ek5vRsVIdmVB
        hJ\nLVjlfCK04fw0yjLyoKEV+bCjBkM1GASD6CiIgi/Hw/BQDfE4ODmJwsMw/BpQGzoGZ47bwnCnJ0hM\nKuGwguwfoOfAvHuvUTtte8GdvLhy14zD2XdGq70xdW7G9AKaRpSvu7BS6a/BxkTnkbbIYyskLr9e\nL+f1nNVxjJ
        Y2pLjIZYKqSNH2H2/zvjYO7VSk7OcjOFt2GG32/tDWnLah+8ThKZrYJfTyx7d+bXHy\nOb06AL9Su84M0uukA/4Tnd78t1YVhakTjN6OaqPuqPZ3TO+AldFaxysavU+Wrutbw8p1Utn8UG7G\nqGX/46/iJgRfZiLFXCJ9uoX2
        VOMlXwSxA604zcJS9TN409KZzgztlgG0zi8XW96b037RfwAOFKXB",
            "time_zone": "UTC",
            "max_instances": 1,
            "start_date": 1404262614.472,
            "coalesce": true,
            "view_name": "global",
            "trigger": "interval",
            "version": 1,
            "id": "d07d0040f54f4167b2d7e6488fb2bb94",
            "name": "foo"
        }
    """
    job = None
    job_merge = job_get_merge()
    job = (
        r
        .table(JobCollections.JobsHistory)
        .get(job_id)
        .merge(job_merge)
        .run(conn)
    )

    return job

@time_it
@catch_it([])
@db_create_close
def fetch_jobs_by_view(view_name, conn=None):
    """Fetch all jobs by view.
    Args:
        view_name (str): The name of the view, this job belongs to.

    Basic Usage:
        >>> from vFense.core.scheduler._db_history import fetch_jobs_by_view
        >>> job_info = fetch_jobs_by_view('global')

    Returns:
        list
    >>>
        {
            "next_run_time": 1404262689.472,
            "misfire_grace_time": 1,
            "end_date": null,
            "job_state": "eJxFUU1PGzEQTUKa3bik4bPfHxQ4kEuUooVQTpV6qKpIPUTM2fLas7sWGy/j9YaAFKm9UH4fP4Df\nwm4CrQ+jJ8+z37w3vxtzqh9AU9g4p0YPfJyhLFxmaQU8hZEoUkdN6EzEjGuTO2Ek5vRsVIdmVB
        hJ\nLVjlfCK04fw0yjLyoKEV+bCjBkM1GASD6CiIgi/Hw/BQDfE4ODmJwsMw/BpQGzoGZ47bwnCnJ0hM\nKuGwguwfoOfAvHuvUTtte8GdvLhy14zD2XdGq70xdW7G9AKaRpSvu7BS6a/BxkTnkbbIYyskLr9e\nL+f1nNVxjJ
        Y2pLjIZYKqSNH2H2/zvjYO7VSk7OcjOFt2GG32/tDWnLah+8ThKZrYJfTyx7d+bXHy\nOb06AL9Su84M0uukA/4Tnd78t1YVhakTjN6OaqPuqPZ3TO+AldFaxysavU+Wrutbw8p1Utn8UG7G\nqGX/46/iJgRfZiLFXCJ9uoX2
        VOMlXwSxA604zcJS9TN409KZzgztlgG0zi8XW96b037RfwAOFKXB",
            "time_zone": "UTC",
            "max_instances": 1,
            "start_date": 1404262614.472,
            "coalesce": true,
            "view_name": "global",
            "trigger": "interval",
            "version": 1,
            "id": "d07d0040f54f4167b2d7e6488fb2bb94",
            "name": "foo"
        }
    """
    job = None
    job_merge = job_get_merge()
    job = list(
        r
        .table(JobCollections.JobsHistory)
        .get_all(view_name, index=JobHistoryIndexes.ViewName)
        .merge(job_merge)
        .run(conn)
    )

    return job

@time_it
@catch_it({})
@db_create_close
def fetch_job_by_name_and_view(name, view_name, conn=None):
    """Fetch all information about a job
    Args:
        name (str): The name of the job.
        view_name (str): The name of the view, this job belongs to.

    Basic Usage:
        >>> from vFense.core.scheduler._db_history import fetch_job
        >>> job_info = fetch_job('job_id')

    Returns:
    >>>
        {
            "next_run_time": 1404262689.472,
            "misfire_grace_time": 1,
            "end_date": null,
            "job_state": "eJxFUU1PGzEQTUKa3bik4bPfHxQ4kEuUooVQTpV6qKpIPUTM2fLas7sWGy/j9YaAFKm9UH4fP4Df\nwm4CrQ+jJ8+z37w3vxtzqh9AU9g4p0YPfJyhLFxmaQU8hZEoUkdN6EzEjGuTO2Ek5vRsVIdmVB
        hJ\nLVjlfCK04fw0yjLyoKEV+bCjBkM1GASD6CiIgi/Hw/BQDfE4ODmJwsMw/BpQGzoGZ47bwnCnJ0hM\nKuGwguwfoOfAvHuvUTtte8GdvLhy14zD2XdGq70xdW7G9AKaRpSvu7BS6a/BxkTnkbbIYyskLr9e\nL+f1nNVxjJ
        Y2pLjIZYKqSNH2H2/zvjYO7VSk7OcjOFt2GG32/tDWnLah+8ThKZrYJfTyx7d+bXHy\nOb06AL9Su84M0uukA/4Tnd78t1YVhakTjN6OaqPuqPZ3TO+AldFaxysavU+Wrutbw8p1Utn8UG7G\nqGX/46/iJgRfZiLFXCJ9uoX2
        VOMlXwSxA604zcJS9TN409KZzgztlgG0zi8XW96b037RfwAOFKXB",
            "time_zone": "UTC",
            "max_instances": 1,
            "start_date": 1404262614.472,
            "coalesce": true,
            "view_name": "global",
            "trigger": "interval",
            "version": 1,
            "id": "d07d0040f54f4167b2d7e6488fb2bb94",
            "name": "foo"
        }
    """
    job = None
    job_merge = job_get_merge()
    job = list(
        r
        .table(JobCollections.JobsHistory)
        .get_all(view_name, index=JobHistoryIndexes.ViewName)
        .filter(
            {
                JobHistoryKeys.Name: name
            }
        )
        .merge(job_merge)
        .run(conn)
    )
    if job:
        job = job[0]

    return job

@time_it
def insert_historical_job(job_data, conn=None):
    """insert a new historical job
    Args:
        job_data (dict): The historical data you need to insert.

    Basic Usage:
        >>> from vFense.core.schedule._db_history import insert_historical_job
        >>> job_data = {}
        >>> insert_historical_job(job_data)

    Returns:
        Tuple (status_code, count, error, generated ids)
        >>> (2001, 1, None, [])
    """
    data = (
        insert_data_in_table(
            job_data, JobCollections.JobsHistory
        )
    )
    return data

@time_it
def update_historical_job(job_id, job_data, conn=None):
    """update an existing historical job
    Args:
        job_id (str): The primary key of the job you are updateing.
        job_data (dict): The historical data you need to insert.

    Basic Usage:
        >>> from vFense.core.schedule._db_history import update_historical_job
        >>> job_id = '5440e4ca3aa44fc59e777027863eb72e'
        >>> job_data = {}
        >>> update_historical_job(job_data)

    Returns:
        Tuple (status_code, count, error, generated ids)
        >>> (2001, 1, None, [])
    """
    data = (
        update_data_in_table(
            job_id, job_data, JobCollections.JobsHistory
        )
    )
    return data

@time_it
def delete_historical_job(job_id, conn=None):
    """delete an existing historical job
    Args:
        job_id (str): The primary key of the job you are deleteing.

    Basic Usage:
        >>> from vFense.core.schedule._db_history import delete_historical_job
        >>> job_id = '5440e4ca3aa44fc59e777027863eb72e'
        >>> delete_data_in_table(job_id)

    Returns:
        Tuple (status_code, count, error, generated ids)
        >>> (2001, 1, None, [])
    """
    data = (
        update_data_in_table(
            job_id, job_data, JobCollections.JobsHistory
        )
    )
    return data
