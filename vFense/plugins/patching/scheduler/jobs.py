from vFense.core.agent._db import fetch_agent_ids
from vFense.core.tag._db import fetch_tag_ids
from vFense.core.operations._constants import AgentOperations
from vFense.core.scheduler.decorators import update_job_history
from vFense.plugins.patching.operations.store_operations import (
    StorePatchingOperation
)
from vFense.plugins.patching.operations import Install

from vFense.plugins.patching.scheduler._db import (
    FetchAppsIdsForSchedule, FetchCustomAppsIdsForSchedule,
    FetchSupportedAppsIdsForSchedule
)

@update_job_history
def agent_apps_operation(agent_ids=None, app_ids=None, view_name=None,
                         user_name=None, restart=None, cpu_throttle=None,
                         net_throttle=None, operation=None, schedule_id=None):
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
        operation (str): The operation name.
            example install_os_apps, uninstall
        schedule_id (str): The id of the schedule that initiated this
            operation.
    """
    if not agent_ids:
        agent_ids = fetch_agent_ids(view_name)

    install = (
        Install(
            app_ids, agent_ids, user_name, view_name, restart,
            cpu_throttle, net_throttle
        )
    )
    store_operation = StorePatchingOperation(user_name, view_name)
    if operation == AgentOperations.INSTALL_OS_APPS:
        store_operation.install_os_apps(install, schedule_id=schedule_id)

    elif operation == AgentOperations.UNINSTALL:
        store_operation.uninstall_apps(install, schedule_id=schedule_id)

    elif operation == AgentOperations.INSTALL_AGENT_UPDATE:
        store_operation.install_agent_update(install, schedule_id=schedule_id)

    elif operation == AgentOperations.INSTALL_CUSTOM_APPS:
        store_operation.install_custom_apps(install, schedule_id=schedule_id)

    elif operation == AgentOperations.INSTALL_SUPPORTED_APPS:
        store_operation.install_supported_apps(
            install, schedule_id=schedule_id
        )

@update_job_history
def tag_apps_operation(tag_ids=None, app_ids=None, view_name=None,
                       user_name=None, restart=None, cpu_throttle=None,
                       net_throttle=None, operation=None, schedule_id=None):
    """Install system updates on 1 or multiple tags.
    Kwargs:
        tag_ids (list): List of tag ids.
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
        operation (str): The operation name.
            example install_os_apps, uninstall
        schedule_id (str): The id of the schedule that initiated this
            operation.
    """
    store_operation = StorePatchingOperation(user_name, view_name)
    if not tag_ids:
        tags = fetch_tag_ids(view_name)

    for tag_id in tags:
        install = (
            Install(
                app_ids, [], tag_id, user_name, view_name, restart,
                cpu_throttle, net_throttle
            )
        )
        if operation == AgentOperations.INSTALL_OS_APPS:
            store_operation.install_os_apps(install, schedule_id=schedule_id)

        elif operation == AgentOperations.UNINSTALL:
            store_operation.uninstall_apps(install, schedule_id=schedule_id)

        elif operation == AgentOperations.INSTALL_AGENT_UPDATE:
            store_operation.install_agent_update(
                install, schedule_id=schedule_id
                                                            )

        elif operation == AgentOperations.INSTALL_CUSTOM_APPS:
            store_operation.install_custom_apps(
                install, schedule_id=schedule_id
            )

        elif operation == AgentOperations.INSTALL_SUPPORTED_APPS:
            store_operation.install_supported_apps(
                install, schedule_id=schedule_id
            )

@update_job_history
def install_os_apps_by_severity_for_agent(severity, agent_ids=None,
                                          view_name=None, user_name=None):
    """Install system updates on 1 or multiple agents.
    Args:
        severity (str): Install all updates with a severity level.
            Example.. (critical, optional, recommended)
    Kwargs:
        agent_ids (list): List of agent ids.
        apps (list): List of application ids.
        view_name (str): The name of the view, this operation is being
            performed on.
        user_name (str): The user who performed this operation.
    """
    fetch = FetchAppsIdsForSchedule()
    operation = StorePatchingOperation(user_name, view_name)
    if not agent_ids:
        agents = fetch_agent_ids(view_name)

    if agents:
        for agent_id in agents:
            app_ids = fetch.by_sev_for_agent(severity, agent_id)
            if app_ids:
                operation.install_os_apps(app_ids, agentids=[agent_id])

@update_job_history
def install_os_apps_by_severity_for_tag(severity, tags=None,
                                        view_name=None, user_name=None,
                                        schedule_id=None):
    """Install system updates on 1 or multiple tags.
    Args:
        severity (str): Install all updates with a severity level.
            Example.. (critical, optional, recommended)
    Kwargs:
        tags (list): List of tag ids.
        view_name (str): The name of the view, this operation is being
            performed on.
        user_name (str): The user who performed this operation.
        schedule_id (str): The id of the schedule that initiated this
            operation.
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
