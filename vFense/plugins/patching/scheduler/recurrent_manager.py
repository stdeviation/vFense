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
               severity=None, every=None, months=None, agent_ids=None,
               view_name=None, user_name=None):
        """Install applications based on a severity on a yearly basis.
        Args:
            job_name (str): The name of this job.
            start_date (float): The unix time, aka epoch time.

        Kwargs:
            end_date (float): The unix time, aka epoch time.
            time_zone (str):  Example... UTC, Chile/EasterIsland.
            severity (str): Critical, Recommended, or Optional.
            every (int|str): Repeat every x.
            months (list): List of months to repeat on.
            agent_ids (list): List of agent ids.
            view_name (str): The name of the view, this was called on.
            user_name (str): The name of the user.
        """
        results = (
            super(AgentSeverityRecurrentJobManager, self).yearly(
                job_name, start_date, end_date=end_date, time_zone=time_zone,
                severity=severity, every=every, months=months,
                agent_ids=agent_ids, view_name=view_name, user_name=user_name
            )
        )
        return results

    def monthly(self, job_name, start_date, end_date=None, time_zone=None,
               severity=None, every=None, days=None, agent_ids=None,
                view_name=None, user_name=None):
        """Install applications based on a severity on a monthly basis.
        Args:
            job_name (str): The name of this job.
            start_date (float): The unix time, aka epoch time.

        Kwargs:
            end_date (float): The unix time, aka epoch time.
            time_zone (str):  Example... UTC, Chile/EasterIsland.
            severity (str): Critical, Recommended, or Optional.
            every (int|str): Repeat every x.
            days (list): List of days to repeat on.
            agent_ids (list): List of agent ids.
            view_name (str): The name of the view, this was called on.
            user_name (str): The name of the user.
        """
        results = (
            super(AgentSeverityRecurrentJobManager, self).monthly(
                job_name, start_date, end_date=end_date, time_zone=time_zone,
                severity=severity, every=every, days=days,
                agent_ids=agent_ids, view_name=view_name, user_name=user_name
            )
        )
        return results

    def weekly(self, job_name, start_date, end_date=None, time_zone=None,
               severity=None, every=None, days=None, agent_ids=None,
               view_name=None, user_name=None):
        """Install applications based on a severity on a weekly basis.
        Args:
            job_name (str): The name of this job.
            start_date (float): The unix time, aka epoch time.

        Kwargs:
            end_date (float): The unix time, aka epoch time.
            time_zone (str):  Example... UTC, Chile/EasterIsland.
            severity (str): Critical, Recommended, or Optional.
            every (int|str): Repeat every x.
            days (list): List of days to repeat on.
            agent_ids (list): List of agent ids.
            view_name (str): The name of the view, this was called on.
            user_name (str): The name of the user.
        """
        results = (
            super(AgentSeverityRecurrentJobManager, self).weekly(
                job_name, start_date, end_date=end_date, time_zone=time_zone,
                severity=severity, every=every, days=days,
                agent_ids=agent_ids, view_name=view_name, user_name=user_name
            )
        )
        return results

    def daily(self, job_name, start_date, end_date=None, time_zone=None,
               severity=None, every=None, agent_ids=None, view_name=None, user_name=None):
        """Install applications based on a severity on a daily basis.
        Args:
            job_name (str): The name of this job.
            start_date (float): The unix time, aka epoch time.

        Kwargs:
            end_date (float): The unix time, aka epoch time.
            time_zone (str):  Example... UTC, Chile/EasterIsland.
            severity (str): Critical, Recommended, or Optional.
            every (int|str): Repeat every x.
            agent_ids (list): List of agent ids.
            view_name (str): The name of the view, this was called on.
            user_name (str): The name of the user.
        """
        results = (
            super(self, AgentSeverityRecurrentJobManager).daily(
                job_name, start_date, end_date=end_date, time_zone=time_zone,
                severity=severity, agent_ids=agent_ids, view_name=view_name,
                user_name=user_name, every=None
            )
        )
        return results


class TagAppsRecurrentJobManager(AgentSeverityRecurrentJobManager):
    def _set_funcs(self):
        self.cron_func = install_os_apps_by_severity_for_tag

    def yearly(self, job_name, start_date, end_date=None, time_zone=None,
               severity=None, every=None, months=None, tag_ids=None,
               view_name=None, user_name=None):
        """Install applications based on a severity on a yearly basis.
        Args:
            job_name (str): The name of this job.
            start_date (float): The unix time, aka epoch time.

        Kwargs:
            end_date (float): The unix time, aka epoch time.
            time_zone (str):  Example... UTC, Chile/EasterIsland.
            severity (str): Critical, Recommended, or Optional.
            every (int|str): Repeat every x.
            months (list): List of months to repeat on.
            tag_ids (list): List of  tag ids.
            view_name (str): The name of the view, this was called on.
            user_name (str): The name of the user.
        """
        results = (
            super(AgentSeverityRecurrentJobManager, self).yearly(
                job_name, start_date, end_date=end_date, time_zone=time_zone,
                severity=severity, every=every, months=months,
                tag_ids=tag_ids, view_name=view_name, user_name=user_name
            )
        )
        return results

    def monthly(self, job_name, start_date, end_date=None, time_zone=None,
               severity=None, every=None, days=None, tag_ids=None,
                view_name=None, user_name=None):
        """Install applications based on a severity on a monthly basis.
        Args:
            job_name (str): The name of this job.
            start_date (float): The unix time, aka epoch time.

        Kwargs:
            end_date (float): The unix time, aka epoch time.
            time_zone (str):  Example... UTC, Chile/EasterIsland.
            severity (str): Critical, Recommended, or Optional.
            every (int|str): Repeat every x.
            days (list): List of days to repeat on.
            tag_ids (list): List of  tag ids.
            view_name (str): The name of the view, this was called on.
            user_name (str): The name of the user.
        """
        results = (
            super(AgentSeverityRecurrentJobManager, self).monthly(
                job_name, start_date, every=every, days=days,
                end_date=end_date, time_zone=time_zone,
                severity=severity, tag_ids=tag_ids, view_name=view_name,
                user_name=user_name
            )
        )
        return results

    def weekly(self, job_name, start_date, end_date=None, time_zone=None,
               severity=None, tag_ids=None, view_name=None, user_name=None):
        """Install applications based on a severity on a weekly basis.
        Args:
            job_name (str): The name of this job.
            start_date (float): The unix time, aka epoch time.

        Kwargs:
            end_date (float): The unix time, aka epoch time.
            time_zone (str):  Example... UTC, Chile/EasterIsland.
            severity (str): Critical, Recommended, or Optional.
            tag_ids (list): List of  tag ids.
            view_name (str): The name of the view, this was called on.
            user_name (str): The name of the user.
        """
        results = (
            super(AgentSeverityRecurrentJobManager, self).weekly(
                job_name, start_date, end_date=end_date, time_zone=time_zone,
                severity=severity, tag_ids=tag_ids, view_name=view_name,
                user_name=user_name
            )
        )
        return results

    def daily(self, job_name, start_date, end_date=None, time_zone=None,
               severity=None, tag_ids=None, view_name=None, user_name=None):
        """Install applications based on a severity on a daily basis.
        Args:
            job_name (str): The name of this job.
            start_date (float): The unix time, aka epoch time.

        Kwargs:
            end_date (float): The unix time, aka epoch time.
            time_zone (str):  Example... UTC, Chile/EasterIsland.
            severity (str): Critical, Recommended, or Optional.
            tag_ids (list): List of  tag ids.
            view_name (str): The name of the view, this was called on.
            user_name (str): The name of the user.
        """
        results = (
            super(AgentSeverityRecurrentJobManager, self).daily(
                job_name, start_date, end_date=end_date, time_zone=time_zone,
                severity=severity, tag_ids=tag_ids, view_name=view_name,
                user_name=user_name
            )
        )
        return results
