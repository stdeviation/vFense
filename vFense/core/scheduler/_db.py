from vFense._constants import VFENSE_LOGGING_CONFIG
from vFense.db.client import r, db_create_close
from vFense.core.decorators import catch_it, time_it
from vFense.core.scheduler._db_model import (
    JobCollections, JobKeys, JobIndexes
)
from vFense.core.scheduler._db_sub_queries import (
    job_get_merge
)


@time_it
@catch_it({})
@db_create_close
def fetch_job(job_id, conn=None):
    """Fetch all information about a job
    Args:
        job_id (str): the primary id of the job.

    Basic Usage:
        >>> from vFense.core.scheduler._db import fetch_job
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
        .table(JobCollections.Jobs)
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
        >>> from vFense.core.scheduler._db import fetch_jobs_by_view
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
        .table(JobCollections.Jobs)
        .get_all(view_name, index=JobIndexes.ViewName)
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
        >>> from vFense.core.scheduler._db import fetch_job
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
        .table(JobCollections.Jobs)
        .get_all(view_name, index=JobIndexes.ViewName)
        .filter(
            {
                JobKeys.Name: name
            }
        )
        .merge(job_merge)
        .run(conn)
    )
    if job:
        job = job[0]

    return job


@time_it
@catch_it([])
@db_create_close
def fetch_admin_jobs_by_view(view_name, conn=None):
    """Fetch all admin jobs by view.
    Args:
        view_name (str): The name of the view, this job belongs to.

    Basic Usage:
        >>> from vFense.core.scheduler._db import fetch_jobs_by_view
        >>> job_info = fetch_jobs_by_view('global')

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
        .table(JobCollections.AdministrativeJobs)
        .get_all(view_name, index=JobIndexes.ViewName)
        .merge(job_merge)
        .run(conn)
    )

    return job

@time_it
@catch_it({})
@db_create_close
def fetch_admin_job_by_name_and_view(name, view_name, conn=None):
    """Fetch all information about a job
    Args:
        name (str): The name of the job.
        view_name (str): The name of the view, this job belongs to.

    Basic Usage:
        >>> from vFense.core.scheduler._db import fetch_job
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
        .table(JobCollections.AdministrativeJobs)
        .get_all(view_name, index=JobIndexes.ViewName)
        .filter(
            {
                JobKeys.Name: name
            }
        )
        .merge(job_merge)
        .run(conn)
    )
    if job:
        job =- job[0]

    return job
