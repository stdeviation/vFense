from vFense.core.agent.scheduler.recurrent_manager import (
    AgentRebootRecurrentJobManager
)
from vFense.core.tag.scheduler.manager import reboot_tags

class TagAppsRecurrentJobManager(AgentRebootRecurrentJobManager):
    def _set_funcs(self):
        self.cron_func = reboot_tags

    def yearly(self, job_name, start_date, end_date=None, time_zone=None,
               tag_ids=None, view_name=None, user_name=None ):
        """Reboot agents on a yearly basis.
        Args:
            job_name (str): The name of this job.
            start_date (float): The unix time, aka epoch time.

        Kwargs:
            end_date (float): The unix time, aka epoch time.
            time_zone (str):  Example... UTC, Chile/EasterIsland.
            tag_ids (list): List of tag ids.
            view_name (str): The name of the view, this was called on.
            user_name (str): The name of the user.
        """
        results = (
            super(self, AgentRebootRecurrentJobManager).yearly(
                job_name, start_date, end_date=end_date, time_zone=time_zone,
                tag_ids=tag_ids, view_name=view_name, user_name=user_name
            )
        )
        return results

    def monthly(self, job_name, start_date, end_date=None, time_zone=None,
               tag_ids=None, view_name=None, user_name=None ):
        """Reboot agents on a monthly basis.
        Args:
            job_name (str): The name of this job.
            start_date (float): The unix time, aka epoch time.

        Kwargs:
            end_date (float): The unix time, aka epoch time.
            time_zone (str):  Example... UTC, Chile/EasterIsland.
            tag_ids (list): List of tag ids.
            view_name (str): The name of the view, this was called on.
            user_name (str): The name of the user.
        """
        results = (
            super(self, AgentRebootRecurrentJobManager).monthly(
                job_name, start_date, end_date=end_date, time_zone=time_zone,
                tag_ids=tag_ids, view_name=view_name, user_name=user_name
            )
        )
        return results

    def weekly(self, job_name, start_date, end_date=None, time_zone=None,
               tag_ids=None, view_name=None, user_name=None ):
        """Reboot agents on a weekly basis.
        Args:
            job_name (str): The name of this job.
            start_date (float): The unix time, aka epoch time.

        Kwargs:
            end_date (float): The unix time, aka epoch time.
            time_zone (str):  Example... UTC, Chile/EasterIsland.
            tag_ids (list): List of tag ids.
            view_name (str): The name of the view, this was called on.
            user_name (str): The name of the user.
        """
        results = (
            super(self, AgentRebootRecurrentJobManager).weekly(
                job_name, start_date, end_date=end_date, time_zone=time_zone,
                tag_ids=tag_ids, view_name=view_name, user_name=user_name
            )
        )
        return results

    def daily(self, job_name, start_date, end_date=None, time_zone=None,
               tag_ids=None, view_name=None, user_name=None ):
        """Reboot agents on a daily basis.
        Args:
            job_name (str): The name of this job.
            start_date (float): The unix time, aka epoch time.

        Kwargs:
            end_date (float): The unix time, aka epoch time.
            time_zone (str):  Example... UTC, Chile/EasterIsland.
            tag_ids (list): List of tag ids.
            view_name (str): The name of the view, this was called on.
            user_name (str): The name of the user.
        """
        results = (
            super(self, AgentRebootRecurrentJobManager).daily(
                job_name, start_date, end_date=end_date, time_zone=time_zone,
                tag_ids=tag_ids, view_name=view_name, user_name=user_name
            )
        )
        return results
