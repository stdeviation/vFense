import logging
from vFense.core.agent import *
from vFense.db.client import r
from vFense.plugins.patching import *
from vFense.core.agent.agents import get_all_agent_ids, get_agent_info
from vFense.core.tag import *
from vFense.plugins.patching._db_files import fetch_file_data
from vFense.plugins.patching._db import fetch_app_data, \
    fetch_apps_data_by_os_code, fetch_file_data, insert_app_data

from vFense.plugins.patching.rv_db_calls import update_file_data

logging.config.fileConfig('/opt/TopPatch/conf/logging.config')
logger = logging.getLogger('rvapi')


def add_custom_app_to_agents(username, customer_name, uri, method,
                             file_data, agent_id=None, app_id=None):

    if app_id and not agent_id:
        app_info = (
            fetch_app_data(
                app_id, table=AppCollections.CustomApps
            )
        )

        agent_ids = get_all_agent_ids(customer_name, agent_os=app_info[AgentKey.OsCode])
        if len(agent_ids) > 0:
            for agentid in agent_ids:
                update_file_data(app_id, agentid, file_data)
                agent_info_to_insert = (
                    {
                        CustomAppsPerAgentKey.AgentId: agentid,
                        CustomAppsPerAgentKey.AppId: app_id,
                        CustomAppsPerAgentKey.Status: AVAILABLE,
                        CustomAppsPerAgentKey.CustomerName: customer_name,
                        CustomAppsPerAgentKey.InstallDate: r.epoch_time(0.0)
                    }
                )
                insert_app_data(agent_info_to_insert, table=AppCollections.CustomAppsPerAgent)

    if agent_id and not app_id:
        agent_info = get_agent_info(agent_id)
        apps_info = (
            fetch_apps_data_by_os_code(
                agent_info[AgentKey.OsCode], customer_name
            )
        )
        if len(apps_info) > 0:
            for app_info in apps_info:
                app_id = app_info.get(CustomAppsKey.AppId)
                file_data = fetch_file_data(app_id)
                update_file_data(
                    app_id,
                    agent_id, file_data
                )
                agent_info_to_insert = (
                    {
                        CustomAppsPerAgentKey.AgentId: agent_id,
                        CustomAppsPerAgentKey.AppId: app_id,
                        CustomAppsPerAgentKey.Status: AVAILABLE,
                        CustomAppsPerAgentKey.CustomerName: customer_name,
                        CustomAppsPerAgentKey.InstallDate: r.epoch_time(0.0)
                    }
                )
                insert_app_data(agent_info_to_insert, table=AppCollections.CustomAppsPerAgent)
