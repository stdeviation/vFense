from datetime import datetime

from vFense.core.operations._constants import AgentOperations
from vFense.core.results import ApiResults
from vFense.core.scheduler import Schedule
from vFense.core.scheduler._constants import ScheduleTriggers
from vFense.core.scheduler.manager import JobManager

class AgentRecurrentJobManager(JobManager):
    def _set_funcs(self):
        self.cron_func = None

    def yearly(self, job_name, start_date,
               end_date=None, time_zone=None, months=None, **kwargs):
        """Perform job on a yearly basis.
        Args:
            job_name (str): The name of this job.
            start_date (float): The unix time, aka epoch time

        Kwargs:
            end_date (float): The unix time, aka epoch time
            time_zone (str):  Example... UTC, Chile/EasterIsland
            months (list): List of months to run this on.
            **kwargs: all keywords that belong to the calling function
        """
        date = datetime.fromtimestamp(start_date)
        results = (
            self.cron(
                job_name, start_date, month=date.month, day=date.day,
                hour=date.hour, minute=date.minute, time_zone=time_zone,
                end_date=end_date, **kwargs
            )
        )
        return results

    def monthly(self, install, job_name, start_date,
               end_date=None, time_zone=None, **kwargs):
        """Perform a job on a monthly basis.
        Args:
            job_name (str): The name of this job.
            start_date (float): The unix time, aka epoch time

        Kwargs:
            end_date (float): The unix time, aka epoch time
            time_zone (str):  Example... UTC, Chile/EasterIsland
            **kwargs: all keywords that belong to the calling function
        """
        date = datetime.fromtimestamp(start_date)
        results = (
            self.cron(
                install, job_name, start_date, day=date.day, hour=date.hour,
                minute=date.minute, time_zone=time_zone, end_date=end_date,
                **kwargs
            )
        )
        return results

    def weekly(self, install, job_name, start_date,
               end_date=None, time_zone=None, **kwargs):
        """Perform a job on a weekly basis.
        Args:
            job_name (str): The name of this job.
            start_date (float): The unix time, aka epoch time

        Kwargs:
            end_date (float): The unix time, aka epoch time
            time_zone (str):  Example... UTC, Chile/EasterIsland
            **kwargs: all keywords that belong to the calling function
        """
        date = datetime.fromtimestamp(start_date)
        results = (
            self.cron(
                install, job_name, start_date, day_of_week=date.weekday,
                hour=date.hour, minute=date.minute, time_zone=time_zone,
                end_date=end_date, **kwargs
            )
        )
        return results

    def daily(self, install, job_name, start_date,
               end_date=None, time_zone=None, **kwargs):
        """Perform a job on a daily basis.
        Args:
            job_name (str): The name of this job.
            start_date (float): The unix time, aka epoch time

        Kwargs:
            end_date (float): The unix time, aka epoch time
            time_zone (str):  Example... UTC, Chile/EasterIsland
            **kwargs: all keywords that belong to the calling function
        """
        date = datetime.fromtimestamp(start_date)
        results = (
            self.cron(
                install, job_name, start_date, hour=date.hour,
                minute=date.minute, time_zone=time_zone, end_date=end_date,
                **kwargs
            )
        )
        return results

    def cron(self, job_name, start_date, year=None, month=None,
             day=None, day_of_week=None, hour=None, minute=None,
             time_zone=None, end_date=None,
             operation=AgentOperations.INSTALL_OS_APPS, **kwargs):
        """Install 1 or multiple applications to 1 or multiple agents.
        Args:
            job_name (str): The name of this job.
            start_date (float): The unix time, aka epoch time

        Kwargs:
            time_zone (str):  Example... UTC, Chile/EasterIsland
            year (int|str): 4-digit year
            month (int|str): month (1-12)
            day (int|str): day of the (1-31)
            week (int|str): ISO week (1-53)
            day_of_week (int|str): number or name of weekday (0-6 or mon,tue,wed,thu,fri,sat,sun)
            hour (int|str): hour (0-23)
            minute (int|str): minute (0-59)
            end_date (float): The unix time, aka epoch time
            operation (str): The name of the operation.
                example install_os_apps, uninstall
            **kwargs: all keywords that belong to the calling function
        """
        self._set_funcs()
        results = ApiResults()
        job = (
            Schedule(
                job_name, self.cron_func, kwargs,
                start_date, operation=operation, time_zone=time_zone,
                trigger=ScheduleTriggers.CRON, year=year,
                hour=hour, day_of_week=day_of_week,
                month=month, day=day, minute=minute, end_date=end_date
            )
        )

        results = self.add_cron_job(job)
        return results


class TagRecurrentJobManager(AgentRecurrentJobManager):
    def _set_funcs(self):
        self.cron_func = None
