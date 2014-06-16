from vFense.db.client import db_create_close, r
from vFense.plugins.patching._db_model import *
from vFense.core.agent import *
from vFense.core.agent.agents import get_agent_info
from vFense.errorz.error_messages import GenericResults
from vFense.plugins.patching._db_files import fetch_file_data
from vFense.plugins.patching._db import fetch_apps_data_by_os_code, \
    insert_app_data

from vFense.plugins.patching.file_data import add_file_data

import logging
import logging.config
from vFense import VFENSE_LOGGING_CONFIG

logging.config.fileConfig(VFENSE_LOGGING_CONFIG)
logger = logging.getLogger('rvapi')


def add_supported_app_to_agents(username, view_name, uri, method, agent_id=None):

    if agent_id:
        agent_info = get_agent_info(agent_id)
        apps_info = (
            fetch_apps_data_by_os_code(
                agent_info[AgentKeys.OsCode],
                view_name,
                collection=AppCollections.SupportedApps,
            )
        )
        if len(apps_info) > 0:
            for app_info in apps_info:
                app_id = app_info.get(SupportedAppsKey.AppId)
                file_data = fetch_file_data(app_id)
                add_file_data(
                    app_id, file_data, agent_id
                )
                agent_info_to_insert = (
                    {
                        SupportedAppsPerAgentKey.AgentId: agent_id,
                        SupportedAppsPerAgentKey.AppId: app_id,
                        SupportedAppsPerAgentKey.Status: AVAILABLE,
                        SupportedAppsPerAgentKey.ViewName: view_name,
                        SupportedAppsPerAgentKey.InstallDate: r.epoch_time(0.0)
                    }
                )
                insert_app_data(
                    agent_info_to_insert,
                    collection=AppCollections.SupportedAppsPerAgent
                )


@db_create_close
def get_all_stats_by_appid(username, view_name,
                          uri, method, app_id, conn=None):
    data = []
    try:
        apps = (
            r
            .table(AppCollections.SupportedAppsPerAgent)
            .get_all(
                [app_id, view_name],
                index=SupportedAppsPerAgentIndexes.AppIdAndView
            )
            .group(SupportedAppsPerAgentKey.Status)
            .count()
            .ungroup()
            .run(conn)
        )
        if apps:
            for i in apps:
                new_data = i['reduction']
                new_data = (
                    {
                        SupportedAppsPerAgentKey.Status: i['group'][SupportedAppsPerAgentKey.Status],
                        COUNT: i['reduction'],
                        NAME: i['group'][SupportedAppsPerAgentKey.Status].capitalize()
                    }
                )
                data.append(new_data)

        statuses = map(lambda x: x['status'], data)
        difference = set(ValidPackageStatuses).difference(statuses)
        if len(difference) > 0:
            for status in difference:
                status = {
                    COUNT: 0,
                    STATUS: status,
                    NAME: status.capitalize()
                }
                data.append(status)

        results = (
            GenericResults(
                username, uri, method
            ).information_retrieved(data, len(data))
        )

        logger.info(results)

    except Exception as e:
        results = (
            GenericResults(
                username, uri, method
            ).something_broke('getting_pkg_stats', 'updates', e)
        )

        logger.info(results)

    return(results)


@db_create_close
def get_all_agents_per_appid(username, view_name,
                            uri, method, app_id, conn=None):
    data = []
    try:
        agents = (
            r
            .table(AppCollections.SupportedAppsPerAgent)
            .get_all(app_id, index=SupportedAppsPerAgentKey.AppId)
            .eq_join(SupportedAppsPerAgentKey.AgentId, r.table(AgentsCollection))
            .zip()
            .group(
                lambda x: x[SupportedAppsPerAgentKey.Status]
            )
            .map(
                lambda x:
                {
                    AGENTS:
                    [
                        {
                            AgentKeys.ComputerName: x[AgentKeys.ComputerName],
                            AgentKeys.DisplayName: x[AgentKeys.DisplayName],
                            SupportedAppsPerAgentKey.AgentId: x[SupportedAppsPerAgentKey.AgentId]
                        }
                    ],
                    COUNT: 1
                }
            )
            .reduce(
                lambda x, y:
                {
                    AGENTS: x[AGENTS] + y[AGENTS],
                    COUNT: x[COUNT] + y[COUNT]
                }
            )
            .ungroup()
            .run(conn)
        )
        if agents:
            for i in agents:
                new_data = i['reduction']
                new_data[SupportedAppsPerAgentKey.Status] = i['group']
                data.append(new_data)

        statuses = map(lambda x: x['status'], data)
        difference = set(ValidPackageStatuses).difference(statuses)
        if len(difference) > 0:
            for status in difference:
                status = {
                    COUNT: 0,
                    AGENTS: [],
                    STATUS: status
                }
                data.append(status)

        results = (
            GenericResults(
                username, uri, method
            ).information_retrieved(data, len(data))
        )

        logger.info(results)

    except Exception as e:
        results = (
            GenericResults(
                username, uri, method
            ).something_broke('getting_pkg_stats', 'updates', e)
        )

        logger.info(results)

    return(results)


@db_create_close
def get_all_stats_by_agentid(username, view_name,
                              uri, method, agent_id, conn=None):
    data = []
    try:
        apps = (
            r
            .table(AppCollections.SupportedAppsPerAgent)
            .get_all(agent_id, index=SupportedAppsPerAgentKey.AgentId)
            .group(SupportedAppsPerAgentKey.Status)
            .count()
            .ungroup()
            .run(conn)
        )
        if apps:
            for i in apps:
                new_data = i['reduction']
                new_data = (
                    {
                        SupportedAppsPerAgentKey.Status: i['group'][SupportedAppsPerAgentKey.Status],
                        COUNT: i['reduction'],
                        NAME: i['group'][SupportedAppsPerAgentKey.Status].capitalize()
                    }
                )
                data.append(new_data)

        statuses = map(lambda x: x['status'], data)
        difference = set(ValidPackageStatuses).difference(statuses)
        if len(difference) > 0:
            for status in difference:
                status = {
                    COUNT: 0,
                    STATUS: status,
                    NAME: status.capitalize()
                }
                data.append(status)

        results = (
            GenericResults(
                username, uri, method
            ).information_retrieved(data, len(data))
        )

        logger.info(results)

    except Exception as e:
        results = (
            GenericResults(
                username, uri, method
            ).something_broke('getting_pkg_stats', 'updates', e)
        )
        logger.info(results)

    return(results)

@db_create_close
def get_all_stats_by_tagid(username, view_name,
                           uri, method, tag_id, conn=None):
    data = []
    try:
        apps = (
            r
            .table(SupportedAppsPerTagCollection)
            .get_all(tag_id, index=SupportedAppsPerTagKey.TagId)
            .group(SupportedAppsPerTagKey.Status)
            .count()
            .ungroup()
            .run(conn)
        )
        if apps:
            for i in apps:
                new_data = i['reduction']
                new_data = (
                    {
                        SupportedAppsPerTagKey.Status: i['group'][SupportedAppsPerTagKey.Status],
                        COUNT: i['reduction'],
                        NAME: i['group'][SupportedAppsPerTagKey.Status].capitalize()
                    }
                )
                data.append(new_data)

        statuses = map(lambda x: x['status'], data)
        difference = set(ValidPackageStatuses).difference(statuses)
        if len(difference) > 0:
            for status in difference:
                status = {
                    COUNT: 0,
                    STATUS: status,
                    NAME: status.capitalize()
                }
                data.append(status)

        results = (
            GenericResults(
                username, uri, method
            ).information_retrieved(data, len(data))
        )

        logger.info(results)

    except Exception as e:
        results = (
            GenericResults(
                username, uri, method
            ).something_broke('getting_pkg_stats', 'updates', e)
        )
        logger.info(results)

    return(results)
