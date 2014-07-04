from vFense.core.operations._constants import AgentOperations
from vFense.core.scheduler import Schedule
from vFense.core.scheduler._constants import (
    ScheduleKeys, ScheduleTriggers
)
from vFense.core.scheduler.manager import JobManager
from vFense.core.agent._db import fetch_agent_ids
from vFense.core.tag._db import fetch_tag_ids
from vFense.core.plugins.patching.operations.store_agent_operations import (
    StorePatchingOperation
)

def install_os_apps_in_agents(agents=None, apps=None,
                              view_name=None, user_name=None):
    """Install system updates on 1 or multiple agents.
    Kwargs:
        agents (list): List of agent ids.
        tags (list): List of tag ids.
        apps (list): List of application ids.
        view_name (str): The name of the view, this operation is being
            performed on.
        user_name (str): The user who performed this operation.
    """
    operation = StorePatchingOperation(user_name, view_name)
    if not agents:
        agents = fetch_agent_ids(view_name)

    operation.install_os_apps(agentids=agents)

def install_os_apps_in_tags(tags=None, apps=None,
                            view_name=None, user_name=None):
    """Install system updates on 1 or multiple tags.
    Kwargs:
        tags (list): List of tag ids.
        apps (list): List of application ids.
        view_name (str): The name of the view, this operation is being
            performed on.
        user_name (str): The user who performed this operation.
    """
    operation = StorePatchingOperation(user_name, view_name)
    if not tags:
        tags = fetch_tag_ids(view_name)

    for tag_id in tags:
        operation.install_os_apps(tag_id=tag_id)

def install_custom_apps_in_agents(agents=None, apps=None,
                                  view_name=None, user_name=None):
    """Install custom application on 1 or multiple agents.
    Kwargs:
        agents (list): List of agent ids.
        tags (list): List of tag ids.
        apps (list): List of application ids.
        view_name (str): The name of the view, this operation is being
            performed on.
        user_name (str): The user who performed this operation.
    """
    operation = StorePatchingOperation(user_name, view_name)
    if not agents:
        agents = fetch_agent_ids(view_name)

    operation.install_custom_apps(agentids=agents)

def install_custom_apps_in_tags(tags=None, apps=None,
                                view_name=None, user_name=None):
    """Install custom applications on 1 or multiple tags.
    Kwargs:
        tags (list): List of tag ids.
        apps (list): List of application ids.
        view_name (str): The name of the view, this operation is being
            performed on.
        user_name (str): The user who performed this operation.
    """
    operation = StorePatchingOperation(user_name, view_name)
    if not tags:
        tags = fetch_tag_ids(view_name)

    for tag_id in tags:
        operation.install_custom_apps(tag_id=tag_id)


class AgentAppsJobManager(JobManager):
    def install_os_apps_once(self, start_date, label, user_name,
                             apps, agents=None, time_zone=None):
        """Install 1 or multiple applications to 1 or multiple agents.
        Args:
            start_date (float): The unix time, aka epoch time
            label (str): The name of this job.
            user_name (str): The name of the use who initiated this job.
            apps (list): List of application ids.

        Kwargs:
            agents (list): List of agent ids.
            time_zone (str):  Example... UTC, Chile/EasterIsland
        """
        job_kwargs = {
            ScheduleKeys.Agents: agents,
            ScheduleKeys.UserName: user_name,
            ScheduleKeys.ViewName: self.view_name,
        }
        job = (
            Schedule(
                label, install_os_apps_in_agents, job_kwargs,
                run_date=start_date, operation=AgentOperations.REBOOT,
                time_zone=time_zone, trigger=ScheduleTriggers.DATE
            )
        )
        results = self.add_date_job(job)
        return results

    def install_os_apps_for_agent_cron(self, start_date, label, user_name,
                                       apps, agents=None, year=None,
                                       month=None, day=None,
                                       day_of_week=None, hour=None,
                                       minute=None, time_zone=None,
                                       end_date=None):
        """Install 1 or multiple applications to 1 or multiple agents.
        Args:
            start_date (float): The unix time, aka epoch time
            label (str): The name of this job.
            user_name (str): The name of the use who initiated this job.
            apps (list): List of application ids.

        Kwargs:
            agents (list): List of agent ids.
            time_zone (str):  Example... UTC, Chile/EasterIsland
            year (int|str): 4-digit year
            month (int|str): month (1-12)
            day (int|str): day of the (1-31)
            week (int|str): ISO week (1-53)
            day_of_week (int|str): number or name of weekday (0-6 or mon,tue,wed,thu,fri,sat,sun)
            hour (int|str): hour (0-23)
            minute (int|str): minute (0-59)
            start_date (float): The unix time, aka epoch time
            end_date (float): The unix time, aka epoch time
        """
        job_kwargs = {
            ScheduleKeys.Agents: agents,
            ScheduleKeys.UserName: user_name,
            ScheduleKeys.ViewName: self.view_name,
        }
        job = (
            Schedule(
                label, install_os_apps_in_agents, job_kwargs, start_date,
                operation=AgentOperations.REBOOT, time_zone=time_zone,
                trigger=ScheduleTriggers.DATE, year=year, hour=hour,
                day_of_week=day_of_week, month=month, day=day,
                minute=minute, end_date=end_date
            )
        )
        results = self.add_cron_job(job)
        return results
