from vFense.core.scheduler.recurrent_manager import (
    AgentRecurrentJobManager
)
from vFense.plugins.patching.scheduler.jobs import (
    install_os_apps_by_severity_for_agent,
    install_os_apps_by_severity_for_tag
)

class AgentSeverityRecurrentJobManager(AgentRecurrentJobManager):
    def _set_funcs(self):
        self.cron_func = install_os_apps_by_severity_for_agent

    def yearly(self, job_name, start_date, end_date=None, time_zone=None,
               severity=None, view_name=None, user_name=None ):
        """Install applications based on a severity on a yearly basis.
        Args:
            job_name (str): The name of this job.
            start_date (float): The unix time, aka epoch time.

        Kwargs:
            end_date (float): The unix time, aka epoch time.
            time_zone (str):  Example... UTC, Chile/EasterIsland.
            severity (str): Critical, Recommended, or Optional.
            view_name (str): The name of the view, this was called on.
            user_name (str): The name of the user.
        """
        results = (
            self.AgentSeverityRecurrentJobManager.yearly(
                job_name, start_date, end_date=end_date, time_zone=time_zone,
                severity=severity, view_name=view_name, user_name=user_name
            )
        )
        return results

    def monthly(self, job_name, start_date, end_date=None, time_zone=None,
               severity=None, view_name=None, user_name=None ):
        """Install applications based on a severity on a monthly basis.
        Args:
            job_name (str): The name of this job.
            start_date (float): The unix time, aka epoch time.

        Kwargs:
            end_date (float): The unix time, aka epoch time.
            time_zone (str):  Example... UTC, Chile/EasterIsland.
            severity (str): Critical, Recommended, or Optional.
            view_name (str): The name of the view, this was called on.
            user_name (str): The name of the user.
        """
        results = (
            self.AgentSeverityRecurrentJobManager.monthly(
                job_name, start_date, end_date=end_date, time_zone=time_zone,
                severity=severity, view_name=view_name, user_name=user_name
            )
        )
        return results

    def weekly(self, job_name, start_date, end_date=None, time_zone=None,
               severity=None, view_name=None, user_name=None ):
        """Install applications based on a severity on a weekly basis.
        Args:
            job_name (str): The name of this job.
            start_date (float): The unix time, aka epoch time.

        Kwargs:
            end_date (float): The unix time, aka epoch time.
            time_zone (str):  Example... UTC, Chile/EasterIsland.
            severity (str): Critical, Recommended, or Optional.
            view_name (str): The name of the view, this was called on.
            user_name (str): The name of the user.
        """
        results = (
            self.AgentSeverityRecurrentJobManager.weekly(
                job_name, start_date, end_date=end_date, time_zone=time_zone,
                severity=severity, view_name=view_name, user_name=user_name
            )
        )
        return results

    def daily(self, job_name, start_date, end_date=None, time_zone=None,
               severity=None, view_name=None, user_name=None ):
        """Install applications based on a severity on a daily basis.
        Args:
            job_name (str): The name of this job.
            start_date (float): The unix time, aka epoch time.

        Kwargs:
            end_date (float): The unix time, aka epoch time.
            time_zone (str):  Example... UTC, Chile/EasterIsland.
            severity (str): Critical, Recommended, or Optional.
            view_name (str): The name of the view, this was called on.
            user_name (str): The name of the user.
        """
        results = (
            self.AgentSeverityRecurrentJobManager.daily(
                job_name, start_date, end_date=end_date, time_zone=time_zone,
                severity=severity, view_name=view_name, user_name=user_name
            )
        )
        return results


class TagAppsRecurrentJobManager(AgentSeverityRecurrentJobManager):
    def _set_funcs(self):
        self.cron_func = install_os_apps_by_severity_for_tag
