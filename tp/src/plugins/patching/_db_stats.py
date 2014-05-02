import logging

from vFense.db.client import db_create_close, r
from vFense.core.decorators import time_it
from vFense.plugins.patching import AppCollections, DbCommonAppPerAgentIndexes
from vFense.plugins.patching._constants import CommonAppKeys

logging.config.fileConfig('/opt/TopPatch/conf/logging.config')
logger = logging.getLogger('rvapi')

@time_it
@db_create_close
def get_all_app_stats_by_agentid(agent_id, conn=None):
    data = []
    try:
        inventory = (
            r
            .table(AppCollections.AppsPerAgent)
            .get_all(
                [CommonAppKeys.INSTALLED, agent_id],
                index=DbCommonAppPerAgentIndexes.StatusAndAgentId
            )
            .count()
            .run(conn)
        )
        data.append(
            {
                CommonAppKeys.COUNT: inventory,
                CommonAppKeys.STATUS: CommonAppKeys.INSTALLED,
                CommonAppKeys.NAME: CommonAppKeys.SOFTWAREINVENTORY
            }
        )
        os_apps_avail = (
            r
            .table(AppCollections.AppsPerAgent)
            .get_all(
                [CommonAppKeys.AVAILABLE, agent_id],
                index=DbCommonAppPerAgentIndexes.StatusAndAgentId
            )
            .count()
            .run(conn)
        )
        data.append(
            {
                CommonAppKeys.COUNT: os_apps_avail,
                CommonAppKeys.STATUS: CommonAppKeys.AVAILABLE,
                CommonAppKeys.NAME: CommonAppKeys.OS
            }
        )
        custom_apps_avail = (
            r
            .table(AppCollections.CustomAppsPerAgent)
            .get_all(
                [CommonAppKeys.AVAILABLE, agent_id],
                index=DbCommonAppPerAgentIndexes.StatusAndAgentId
            )
            .count()
            .run(conn)
        )
        data.append(
            {
                CommonAppKeys.COUNT: custom_apps_avail,
                CommonAppKeys.STATUS: CommonAppKeys.AVAILABLE,
                CommonAppKeys.NAME: CommonAppKeys.CUSTOM
            }
        )
        supported_apps_avail = (
            r
            .table(AppCollections.SupportedAppsPerAgent)
            .get_all(
                [CommonAppKeys.AVAILABLE, agent_id],
                index=DbCommonAppPerAgentIndexes.StatusAndAgentId
            )
            .count()
            .run(conn)
        )

        data.append(
            {
                CommonAppKeys.COUNT: supported_apps_avail,
                CommonAppKeys.STATUS: CommonAppKeys.AVAILABLE,
                CommonAppKeys.NAME: CommonAppKeys.SUPPORTED
            }
        )

        agent_apps_avail = (
            r
            .table(AppCollections.vFenseAppsPerAgent)
            .get_all(
                [CommonAppKeys.AVAILABLE, agent_id],
                index=DbCommonAppPerAgentIndexes.StatusAndAgentId
            )
            .count()
            .run(conn)
        )

        data.append(
            {
                CommonAppKeys.COUNT: agent_apps_avail,
                CommonAppKeys.STATUS: CommonAppKeys.AVAILABLE,
                CommonAppKeys.NAME: CommonAppKeys.AGENT_UPDATES
            }
        )

    except Exception as e:
        logger.exception(e)

    return(data)



