from vFense.db.client import db_create_close, r
from vFense.plugins.patching._db_model import *
from vFense.core.agent._db_model import *
from vFense.core.results import Results, PackageResults

import logging
import logging.config
from vFense._constants import VFENSE_LOGGING_CONFIG

logging.config.fileConfig(VFENSE_LOGGING_CONFIG)
logger = logging.getLogger('rvapi')


@db_create_close
def get_all_stats_by_appid(username, view_name,
                          uri, method, app_id, conn=None):
    data = []
    try:
        apps = (
            r
            .table(AppCollections.CustomAppsPerAgent)
            .get_all(
                [app_id, view_name],
                index=CustomAppsPerAgentIndexes.AppIdAndView
            )
            .group(CustomAppsPerAgentKey.Status)
            .count()
            .ungroup()
            .run(conn)
        )
        if apps:
            for i in apps:
                new_data = i['reduction']
                new_data = (
                    {
                        CustomAppsPerAgentKey.Status: i['group'][CustomAppsPerAgentKey.Status],
                        COUNT: i['reduction'],
                        NAME: i['group'][CustomAppsPerAgentKey.Status].capitalize()
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
            Results(
                username, uri, method
            ).information_retrieved(data, len(data))
        )

        logger.info(results)

    except Exception as e:
        results = (
            Results(
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
            .table(AppCollections.CustomAppsPerAgent)
            .get_all(app_id, index=CustomAppsPerAgentKey.AppId)
            .eq_join(CustomAppsPerAgentKey.AgentId, r.table(AgentCollections.Agents))
            .zip()
            .group(
                lambda x: x[CustomAppsPerAgentKey.Status]
            )
            .map(
                lambda x:
                {
                    AGENTS:
                    [
                        {
                            AgentKeys.ComputerName: x[AgentKeys.ComputerName],
                            AgentKeys.DisplayName: x[AgentKeys.DisplayName],
                            CustomAppsPerAgentKey.AgentId: x[CustomAppsPerAgentKey.AgentId]
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
                new_data[CustomAppsPerAgentKey.Status] = i['group']
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
            Results(
                username, uri, method
            ).information_retrieved(data, len(data))
        )

        logger.info(results)

    except Exception as e:
        results = (
            Results(
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
            .table(AppCollections.CustomAppsPerAgent)
            .get_all(agent_id, index=CustomAppsPerAgentKey.AgentId)
            .group(CustomAppsPerAgentKey.Status)
            .count()
            .ungroup()
            .run(conn)
        )
        if apps:
            for i in apps:
                new_data = i['reduction']
                new_data = (
                    {
                        CustomAppsPerAgentKey.Status: i['group'][CustomAppsPerAgentKey.Status],
                        COUNT: i['reduction'],
                        NAME: i['group'][CustomAppsPerAgentKey.Status].capitalize()
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
            Results(
                username, uri, method
            ).information_retrieved(data, len(data))
        )

        logger.info(results)

    except Exception as e:
        results = (
            Results(
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
            .table(CustomAppsPerTagCollection)
            .get_all(tag_id, index=CustomAppsPerTagKey.TagId)
            .group(CustomAppsPerTagKey.Status)
            .count()
            .ungroup()
            .run(conn)
        )
        if apps:
            for i in apps:
                new_data = i['reduction']
                new_data = (
                    {
                        CustomAppsPerTagKey.Status: i['group'][CustomAppsPerTagKey.Status],
                        COUNT: i['reduction'],
                        NAME: i['group'][CustomAppsPerTagKey.Status].capitalize()
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
            Results(
                username, uri, method
            ).information_retrieved(data, len(data))
        )

        logger.info(results)

    except Exception as e:
        results = (
            Results(
                username, uri, method
            ).something_broke('getting_pkg_stats', 'updates', e)
        )
        logger.info(results)

    return(results)
