from vFense.core.agent._db import fetch_agent_ids
from vFense.core.tag._db import fetch_tag_ids
from vFense.core.plugins.patching.operations.store_agent_operations import (
    StorePatchingOperation
)
from vFense.core.plugins.patching.operations import Install

from vFense.core.plugins.patching.scheduler._db import (
    FetchAppsIdsForSchedule, FetchCustomAppsIdsForSchedule,
    FetchSupportedAppsIdsForSchedule
)

def install_os_apps_in_agents(agent_ids=None, app_ids=None, view_name=None,
                              user_name=None, restart=None, cpu_throttle=None,
                              net_throttle=None):
    """Install system updates on 1 or multiple agents.

    Kwargs:
        agent_ids (list): List of agent ids.
        app_ids (list): List of application ids.
        view_name (str): The name of the view, this operation is being
            performed on.
        user_name (str): The user who performed this operation.
        restart (str): After installing the application, do you want the agent
            to reboot the host. Valid values: none, needed, and force.
            default=none
        cpu_throttle (str): Set the CPU affinity for the install process.
            Valid values: idle, below_normal, normal, above_normal, high.
            default=normal
        net_throttle (str): The amount of traffic in KB to use.
            default=0 (unlimitted)
    """
    operation = StorePatchingOperation(user_name, view_name)
    if not agent_ids:
        agent_ids = fetch_agent_ids(view_name)

    install = (
        Install(
            app_ids, agent_ids, user_name, view_name, restart,
            cpu_throttle, net_throttle
        )
    )
    operation.install_os_apps(install)

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

def install_os_apps_by_severity_for_agent(severity, agents=None,
                                          view_name=None, user_name=None):
    """Install system updates on 1 or multiple agents.
    Args:
        severity (str): Install all updates with a severity level.
            Example.. (critical, optional, recommended)
    Kwargs:
        agents (list): List of agent ids.
        apps (list): List of application ids.
        view_name (str): The name of the view, this operation is being
            performed on.
        user_name (str): The user who performed this operation.
    """
    fetch = FetchAppsIdsForSchedule()
    operation = StorePatchingOperation(user_name, view_name)
    if not agents:
        agents = fetch_agent_ids(view_name)

    if agents:
        for agent_id in agents:
            app_ids = fetch.by_sev_for_agent(severity, agent_id)
            if app_ids:
                operation.install_os_apps(app_ids, agentids=[agent_id])

def install_os_apps_by_severity_for_tag(severity, tags=None,
                                        view_name=None, user_name=None):
    """Install system updates on 1 or multiple tags.
    Args:
        severity (str): Install all updates with a severity level.
            Example.. (critical, optional, recommended)
    Kwargs:
        tags (list): List of tag ids.
        view_name (str): The name of the view, this operation is being
            performed on.
        user_name (str): The user who performed this operation.
    """
    fetch = FetchAppsIdsForSchedule()
    operation = StorePatchingOperation(user_name, view_name)
    if not tags:
        tags = fetch_tag_ids(view_name)

    if tags:
        for tag_id in tags:
            app_ids = fetch.by_sev_for_tag(severity, tag_id)
            if app_ids:
                operation.install_os_apps(app_ids, tag_id=[tag_id])

