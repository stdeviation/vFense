import logging

from vFense import VFENSE_LOGGING_CONFIG
from vFense.db.client import db_create_close, r
from vFense.core.decorators import time_it
from vFense.core._constants import CommonKeys
from vFense.core.agent import AgentKey, AgentCollections
from vFense.core.tag import (
    TagCollections, TagsPerAgentKey, TagsPerAgentIndexes,
)
from vFense.plugins.patching import (
    AppCollections, DbCommonAppPerAgentIndexes,
    DbCommonAppPerAgentKeys, DbCommonAppKeys
)
from vFense.plugins.patching._constants import CommonAppKeys

logging.config.fileConfig(VFENSE_LOGGING_CONFIG)
logger = logging.getLogger('rvapi')

@time_it
@db_create_close
def get_all_app_stats_by_agentid(agent_id, conn=None):
    """Retrieve the application statistics for an agent.
    Args:
        agent_id (str): The agent id of the agent you are retrieving
            application statistics for.

    Basic Usage:
        >>> from vFense.plugins.patching._db_stats import get_all_app_stats_by_agentid
        >>> agent_id = 'default'
        >>> get_all_app_stats_by_agentid(tag_id)

    Returns:
        List of application statistics.
    """
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

    return data


@db_create_close
def get_all_app_stats_by_tagid(tag_id, conn=None):
    """Retrieve the application statistics for a tag.
    Args:
        tag_id (str): The tag id of the tag you are retrieving
            application statistics for.

    Basic Usage:
        >>> from vFense.plugins.patching._db_stats import get_all_app_stats_by_tagid
        >>> tag_id = 'default'
        >>> get_all_app_stats_by_tagid(tag_id)

    Returns:
        List of application statistics.
    """
    data = []
    try:
        inventory = (
            r
            .table(TagCollections.TagsPerAgent, use_outdated=True)
            .get_all(tag_id, index=TagsPerAgentIndexes.TagId)
            .pluck(TagsPerAgentKey.AgentId)
            .eq_join(
                lambda x: [
                    CommonAppKeys.INSTALLED,
                    x[DbCommonAppPerAgentKeys.AgentId]
                ],
                r.table(AppCollections.AppsPerAgent),
                index=DbCommonAppPerAgentIndexes.StatusAndAgentId
            )
            .eq_join(lambda x: x['right'][DbCommonAppPerAgentKeys.AppId], r.table(AppCollections.UniqueApplications))
            .filter(
                lambda y: y['right'][DbCommonAppKeys.Hidden] == CommonKeys.NO
            )
            .map(
                {
                    DbCommonAppPerAgentKeys.AppId: r.row['right'][DbCommonAppPerAgentKeys.AppId],
                }
            )
            .pluck(DbCommonAppPerAgentKeys.AppId)
            .distinct()
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
            .table(TagCollections.TagsPerAgent, use_outdated=True)
            .get_all(tag_id, index=TagsPerAgentIndexes.TagId)
            .pluck(TagsPerAgentKey.AgentId)
            .eq_join(
                lambda x: [
                    CommonAppKeys.AVAILABLE,
                    x[DbCommonAppPerAgentKeys.AgentId]
                ],
                r.table(AppCollections.AppsPerAgent),
                index=DbCommonAppPerAgentIndexes.StatusAndAgentId
            )
            .pluck({'right': DbCommonAppPerAgentKeys.AppId})
            .distinct()
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
            .table(TagCollections.TagsPerAgent, use_outdated=True)
            .get_all(tag_id, index=TagsPerAgentIndexes.TagId)
            .pluck(TagsPerAgentKey.AgentId)
            .eq_join(
                lambda x: [
                    CommonAppKeys.AVAILABLE,
                    x[DbCommonAppPerAgentKeys.AgentId]
                ],
                r.table(AppCollections.CustomAppsPerAgent),
                index=DbCommonAppPerAgentIndexes.StatusAndAgentId
            )
            .pluck({'right': DbCommonAppPerAgentKeys.AppId})
            .distinct()
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
            .table(TagCollections.TagsPerAgent, use_outdated=True)
            .get_all(tag_id, index=TagsPerAgentIndexes.TagId)
            .pluck(TagsPerAgentKey.AgentId)
            .eq_join(
                lambda x: [
                    CommonAppKeys.AVAILABLE,
                    x[DbCommonAppPerAgentKeys.AgentId]
                ],
                r.table(AppCollections.SupportedAppsPerAgent),
                index=DbCommonAppPerAgentIndexes.StatusAndAgentId
            )
            .pluck({'right': DbCommonAppPerAgentKeys.AppId})
            .distinct()
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
            .table(TagCollections.TagsPerAgent, use_outdated=True)
            .get_all(tag_id, index=TagsPerAgentIndexes.TagId)
            .pluck(TagsPerAgentKey.AgentId)
            .eq_join(
                lambda x: [
                    CommonAppKeys.AVAILABLE,
                    x[DbCommonAppPerAgentKeys.AgentId]
                ],
                r.table(AppCollections.vFenseAppsPerAgent),
                index=DbCommonAppPerAgentIndexes.StatusAndAgentId
            )
            .pluck({'right': DbCommonAppPerAgentKeys.AppId})
            .distinct()
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


@db_create_close
def get_all_avail_stats_by_tagid(tag_id, conn=None):
    """Retrieve the available update statistics for a tag.
    Args:
        tag_id (str): The tag id of the tag you are retrieving
            application statistics for.

    Basic Usage:
        >>> from vFense.plugins.patching._db_stats import get_all_avail_stats_by_tagid
        >>> tag_id = 'default'
        >>> get_all_avail_stats_by_tagid(tag_id)

    Returns:
        List of application statistics.
    """
    data = []
    try:
        os_apps_avail = (
            r
            .table(TagCollections.TagsPerAgent, use_outdated=True)
            .get_all(tag_id, index=TagsPerAgentIndexes.TagId)
            .pluck(TagsPerAgentKey.AgentId)
            .eq_join(
                lambda x: [
                    CommonAppKeys.AVAILABLE,
                    x[DbCommonAppPerAgentKeys.AgentId]
                ],
                r.table(AppCollections.AppsPerAgent),
                index=DbCommonAppPerAgentIndexes.StatusAndAgentId
            )
            .eq_join(lambda x: x['right'][DbCommonAppPerAgentKeys.AppId], r.table(AppCollections.UniqueApplications))
            .filter(
                lambda y: y['right'][DbCommonAppKeys.Hidden] == CommonKeys.NO
            )
            .map(
                {
                    DbCommonAppPerAgentKeys.AppId: r.row['right'][DbCommonAppPerAgentKeys.AppId],
                }
            )
            .pluck(DbCommonAppPerAgentKeys.AppId)
            .distinct()
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
            .table(TagCollections.TagsPerAgent, use_outdated=True)
            .get_all(tag_id, index=TagsPerAgentIndexes.TagId)
            .pluck(TagsPerAgentKey.AgentId)
            .eq_join(
                lambda x: [
                    CommonAppKeys.AVAILABLE,
                    x[DbCommonAppPerAgentIndexes.AgentId]
                ],
                r.table(AppCollections.CustomAppsPerAgent),
                index=DbCommonAppPerAgentIndexes.StatusAndAgentId
            )
            .pluck({'right': DbCommonAppPerAgentKeys.AppId})
            .distinct()
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
            .table(TagCollections.TagsPerAgent, use_outdated=True)
            .get_all(tag_id, index=TagsPerAgentIndexes.TagId)
            .pluck(TagsPerAgentKey.AgentId)
            .eq_join(
                lambda x: [
                    CommonAppKeys.AVAILABLE,
                    x[DbCommonAppPerAgentKeys.AgentId]
                ],
                r.table(AppCollections.SupportedAppsPerAgent),
                index=DbCommonAppPerAgentIndexes.StatusAndAgentId
            )
            .pluck({'right': DbCommonAppPerAgentKeys.AppId})
            .distinct()
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
            .table(TagCollections.TagsPerAgent, use_outdated=True)
            .get_all(tag_id, index=TagsPerAgentIndexes.TagId)
            .pluck(TagsPerAgentKey.AgentId)
            .eq_join(
                lambda x: [
                    CommonAppKeys.AVAILABLE,
                    x[DbCommonAppPerAgentKeys.AgentId]
                ],
                r.table(AppCollections.vFenseAppsPerAgent),
                index=DbCommonAppPerAgentIndexes.StatusAndAgentId
            )
            .pluck({'right': DbCommonAppPerAgentKeys.AppId})
            .distinct()
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

@time_it
@db_create_close
def get_all_app_stats_by_customer(customer_name, conn=None):
    """Retrieve the application stats for a customer.
    Args:
        customer_name (str): The name of the customer you are retrieving
            application statistics for.

    Basic Usage:
        >>> from vFense.plugins.patching._db_stats import get_all_app_stats_by_customer
        >>> customer_name = 'default'
        >>> get_all_app_stats_by_customer(customer_name)

    Returns:
        List of application statistics.
    """
    data = []
    try:
        os_apps_avail = (
            r
            .table(AppCollections.AppsPerAgent, use_outdated=True)
            .get_all(
                [
                    CommonAppKeys.AVAILABLE, customer_name
                ],
                index=DbCommonAppPerAgentIndexes.StatusAndCustomer
            )
            .eq_join(DbCommonAppKeys.AppId, r.table(AppCollections.UniqueApplications))
            .filter(
                lambda x: x['right'][DbCommonAppKeys.Hidden] == CommonKeys.NO
            )
            .map(
                {
                    DbCommonAppPerAgentKeys.AppId: r.row['left'][DbCommonAppPerAgentKeys.AppId],
                }
            )
            .pluck(DbCommonAppPerAgentKeys.AppId)
            .distinct()
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
            .table(AppCollections.CustomAppsPerAgent, use_outdated=True)
            .get_all(
                [
                    CommonAppKeys.AVAILABLE, customer_name
                ],
                index=DbCommonAppPerAgentIndexes.StatusAndCustomer
            )
            .pluck(DbCommonAppPerAgentKeys.AppId)
            .distinct()
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
            .table(AppCollections.SupportedAppsPerAgent, use_outdated=True)
            .get_all(
                [
                    CommonAppKeys.AVAILABLE, customer_name
                ],
                index=DbCommonAppPerAgentIndexes.StatusAndCustomer
            )
            .pluck(DbCommonAppPerAgentKeys.AppId)
            .distinct()
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
            .table(AppCollections.vFenseAppsPerAgent, use_outdated=True)
            .get_all(
                [
                    CommonAppKeys.AVAILABLE, customer_name
                ],
                index=DbCommonAppPerAgentIndexes.StatusAndCustomer
            )
            .pluck(DbCommonAppPerAgentKeys.AppId)
            .distinct()
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

        all_pending_apps = (
            r
            .table(AppCollections.AppsPerAgent, use_outdated=True)
            .get_all(
                [
                    CommonAppKeys.PENDING, customer_name
                ],
                index=DbCommonAppPerAgentIndexes.StatusAndCustomer
            )
            .pluck((CommonAppKeys.APP_ID))
            .distinct()
            .count()
            .run(conn)
        )

        data.append(
            {
                CommonAppKeys.COUNT: all_pending_apps,
                CommonAppKeys.STATUS: CommonAppKeys.PENDING,
                CommonAppKeys.NAME: CommonAppKeys.PENDING.capitalize()
            }
        )

    except Exception as e:
        logger.exception(e)

    return(data)

@time_it
@db_create_close
def group_avail_app_stats_by_os_for_customer(
        customer_name, count=3, conn=None
    ):
    """Retrieve an array of the total count of update available, grouped by
        operating system for a customer.
    Args:
        customer_name (str): The name of the customer.

    Kwargs:
        count (int, optional): The number of results to return.
            default = 3

    Basic Usage:
        >>> from vFense.plugins.patching._db_stats import group_avail_app_stats_by_os_for_customer
        >>> group_avail_app_stats_by_os_for_customer('default')

    Returns:
        >>> [
                {
                    u'count': 253,
                    u'os': u'LinuxMint 16'
                }
            ]
    """
    stats = []
    try:
        stats = (
            r
            .table(AppCollections.AppsPerAgent, use_outdated=True)
            .get_all(
                [CommonAppKeys.AVAILABLE, customer_name],
                index=DbCommonAppPerAgentIndexes.StatusAndCustomer
            )
            .eq_join(
                DbCommonAppKeys.AppId,
                r.table(AppCollections.UniqueApplications)
            )
            .filter(
                lambda x: x['right'][DbCommonAppKeys.Hidden] == CommonKeys.NO
            )
            .map(
                {
                    DbCommonAppPerAgentKeys.AppId: (
                        r.row['left'][DbCommonAppPerAgentKeys.AppId]
                    ),
                    DbCommonAppPerAgentKeys.AgentId: (
                        r.row['left'][DbCommonAppPerAgentKeys.AgentId]
                    ),
                }
            )
            .eq_join(
                AgentKey.AgentId,
                r.table(AgentCollections.Agents)
            )
            .map(
                {
                    DbCommonAppKeys.AppId: (
                        r.row['left'][DbCommonAppKeys.AppId]
                    ),
                    AgentKey.OsString: (
                        r.row['right'][AgentKey.OsString]
                    )
                }
            )
            .pluck(DbCommonAppKeys.AppId, AgentKey.OsString)
            .distinct()
            .group(AgentKey.OsString)
            .count()
            .ungroup()
            .map(
                lambda x:
                {
                    'os': x['group'],
                    'count': x['reduction']
                }
            )
            .order_by(r.desc('count'))
            .limit(count)
            .run(conn)
        )

    except Exception as e:
        logger.exception(e)

    return stats


@time_it
@db_create_close
def group_avail_app_stats_by_os_for_tag(
        tag_id, count=3, conn=None
    ):
    """Retrieve an array of the total count of update available, grouped by
        operating system for a tag.
    Args:
        tag_id (str): 36 character UUID of the tag.

    Kwargs:
        count (int, optional): The number of results to return.
            default = 3

    Basic Usage:
        >>> from vFense.plugins.patching._db_stats import group_avail_app_stats_by_os_for_tag
        >>> group_avail_app_stats_by_os_for_tag('f9be1795-1f3b-45a1-8ea2-3178346a1261')

    Returns:
        >>> [
                {
                    u'count': 253,
                    u'os': u'LinuxMint 16'
                }
            ]
    """
    try:
        stats = (
            r
            .table(TagCollections.TagsPerAgent, use_outdated=True)
            .get_all(tag_id, index=TagsPerAgentIndexes.TagId)
            .pluck(TagsPerAgentKey.AgentId)
            .eq_join(
                lambda x:
                x[AgentKey.AgentId],
                r.table(AgentCollections.Agents)
            )
            .map(
                lambda x:
                {
                    AgentKey.AgentId: x['left'][AgentKey.AgentId],
                    AgentKey.OsString: x['right'][AgentKey.OsString]
                }
            )
            .eq_join(
                lambda x: [
                    CommonAppKeys.AVAILABLE,
                    x[DbCommonAppPerAgentKeys.AgentId]
                ],
                r.table(AppCollections.AppsPerAgent),
                index=DbCommonAppPerAgentIndexes.StatusAndAgentId
            )
            .eq_join(
                lambda x:
                x['right'][DbCommonAppPerAgentKeys.AppId],
                r.table(AppCollections.UniqueApplications)
            )
            .filter(
                lambda x: x['right'][DbCommonAppKeys.Hidden] == CommonKeys.NO
            )
            .map(
                lambda x:
                {
                    CommonAppKeys.APP_ID: x['right'][CommonAppKeys.APP_ID],
                    AgentKey.OsString: x['left']['left'][AgentKey.OsString]
                }
            )
            .distinct()
            .group(AgentKey.OsString)
            .count()
            .ungroup()
            .map(
                lambda x:
                {
                    'os': x['group'],
                    'count': x['reduction']
                }
            )
            .order_by(r.desc('count'))
            .limit(count)
            .run(conn)
        )

    except Exception as e:
        logger.exception(e)

    return stats


@db_create_close
def fetch_bar_chart_for_appid_by_status(
        app_id, customer_name, conn=None
    ):
    data = {}
    try:
        data = (
            r
            .table(AppCollections.AppsPerAgent, use_outdated=True)
            .get_all(
                [app_id, customer_name],
                index=DbCommonAppPerAgentIndexes.AppIdAndCustomer
            )
            .group(DbCommonAppPerAgentKeys.Status)
            .count()
            .run(conn)
        )

    except Exception as e:
        logger.exception(e)

    return data

@time_it
@db_create_close
def fetch_severity_bar_chart_stats_for_customer(customer_name, conn=None):
    data = []
    try:
        data = (
            r
            .table(AppCollections.AppsPerAgent, use_outdated=True)
            .get_all(
                [CommonAppKeys.AVAILABLE, customer_name],
                index=DbCommonAppPerAgentIndexes.StatusAndCustomer
            )
            .pluck(DbCommonAppKeys.AppId)
            .distinct()
            .eq_join(
                DbCommonAppKeys.AppId,
                r.table(AppCollections.UniqueApplications)
            )
            .filter(
                lambda x: x['right'][DbCommonAppKeys.Hidden] == CommonKeys.NO
            )
            .map(
                {
                    DbCommonAppKeys.AppId: (
                        r.row['right'][DbCommonAppKeys.AppId]
                    ),
                    DbCommonAppKeys.RvSeverity: (
                        r.row['right'][DbCommonAppKeys.RvSeverity]
                    )
                }
            )
            .group(DbCommonAppKeys.RvSeverity)
            .count()
            .ungroup()
            .map(
                lambda x:
                {
                    'count': x['reduction'],
                    'severity': x['group'],
                }
            )
            .order_by(r.asc('count'))
            .run(conn)
        )

    except Exception as e:
        logger.exception(e)

    return data


@time_it
@db_create_close
def fetch_severity_bar_chart_stats_for_agent(agent_id, conn=None):
    data = []
    try:
        data = (
            r
            .table(AppCollections.AppsPerAgent, use_outdated=True)
            .get_all(
                [CommonAppKeys.AVAILABLE, agent_id],
                index=DbCommonAppPerAgentIndexes.StatusAndAgentId
            )
            .eq_join(
                DbCommonAppKeys.AppId,
                r.table(AppCollections.UniqueApplications)
            )
            .filter(
                lambda x: x['right'][DbCommonAppKeys.Hidden] == CommonKeys.NO
            )
            .map(
                {
                    DbCommonAppKeys.AppId: (
                        r.row['right'][DbCommonAppKeys.AppId]
                    ),
                    DbCommonAppKeys.RvSeverity: (
                        r.row['right'][DbCommonAppKeys.RvSeverity]
                    )
                }
            )
            .group(DbCommonAppKeys.RvSeverity)
            .count()
            .ungroup()
            .map(
                lambda x:
                {
                    'count': x['reduction'],
                    'severity': x['group'],
                }
            )
            .order_by(r.desc('reduction'))
            .run(conn)
        )

    except Exception as e:
        logger.exception(e)

    return data


@time_it
@db_create_close
def fetch_severity_bar_chart_stats_for_tag(tag_id, conn=None):
    data = []
    try:
        data = (
            r
            .table(TagCollections.TagsPerAgent, use_outdated=True)
            .get_all(tag_id, index=TagsPerAgentIndexes.TagId)
            .pluck(TagsPerAgentKey.AgentId)
            .eq_join(
                lambda x: [
                    CommonAppKeys.AVAILABLE,
                    x[DbCommonAppPerAgentKeys.AgentId]
                ],
                r.table(AppCollections.AppsPerAgent),
                index=DbCommonAppPerAgentIndexes.StatusAndAgentId
            )
            .map(
                {
                    DbCommonAppKeys.AppId: (
                        r.row['right'][DbCommonAppKeys.AppId]
                    ),
                }
            )
            .eq_join(
                DbCommonAppKeys.AppId,
                r.table(AppCollections.UniqueApplications)
            )
            .filter(
                lambda x: x['right'][DbCommonAppKeys.Hidden] == CommonKeys.NO
            )
            .map(
                {
                    DbCommonAppKeys.AppId: (
                        r.row['right'][DbCommonAppKeys.AppId]
                    ),
                    DbCommonAppKeys.RvSeverity: (
                        r.row['right'][DbCommonAppKeys.RvSeverity]
                    )
                }
            )
            .group(DbCommonAppKeys.RvSeverity)
            .count()
            .ungroup()
            .map(
                lambda x:
                {
                    'count': x['reduction'],
                    'severity': x['group'],
                }
            )
            .order_by(r.desc('reduction'))
            .run(conn)
        )

    except Exception as e:
        logger.exception(e)

    return data


@time_it
@db_create_close
def fetch_top_apps_needed_for_customer(customer_name, count=5, conn=None):

    data=[]
    try:
        data = (
            r
            .table(AppCollections.AppsPerAgent)
            .get_all(
                [CommonAppKeys.AVAILABLE, customer_name],
                index=DbCommonAppPerAgentIndexes.StatusAndCustomer
            )
            .eq_join(
                DbCommonAppKeys.AppId,
                r.table(AppCollections.UniqueApplications)
            )
            .filter(
                lambda x: x['right'][DbCommonAppKeys.Hidden] == CommonKeys.NO
            )
            .map(
                lambda x:
                {
                    DbCommonAppKeys.Name: x['right'][DbCommonAppKeys.Name],
                    DbCommonAppKeys.AppId: x['right'][DbCommonAppKeys.AppId],
                    DbCommonAppKeys.RvSeverity: (
                        x['right'][DbCommonAppKeys.RvSeverity]
                    ),
                    DbCommonAppKeys.ReleaseDate: (
                        x['right'][DbCommonAppKeys.ReleaseDate].to_epoch_time()
                    ),
                }
            )
            .group(
                DbCommonAppKeys.Name, DbCommonAppKeys.AppId,
                DbCommonAppKeys.RvSeverity, DbCommonAppKeys.ReleaseDate
            )
            .count()
            .ungroup()
            .map(
                lambda x:
                {
                    DbCommonAppKeys.Name: x['group'][0],
                    DbCommonAppKeys.AppId: x['group'][1],
                    DbCommonAppKeys.RvSeverity: x['group'][2],
                    DbCommonAppKeys.ReleaseDate: x['group'][3],
                    'count': x['reduction'],
                }
            )
            .order_by(r.desc('count'), r.desc(DbCommonAppKeys.ReleaseDate))
            .limit(count)
            .run(conn)
        )

    except Exception as e:
        logger.exception(e)

    return data


@time_it
@db_create_close
def fetch_recently_released_apps(customer_name, count=5, conn=None):
    data = []
    try:
        data = list(
            r
            .table(AppCollections.AppsPerAgent, use_outdated=True)
            .get_all(
                [
                    CommonAppKeys.AVAILABLE, customer_name
                ],
                index=DbCommonAppPerAgentIndexes.StatusAndCustomer
            )
            .eq_join(
                DbCommonAppKeys.AppId,
                r.table(AppCollections.UniqueApplications)
            )
            .map(
                lambda x:
                {
                    DbCommonAppKeys.Name: (
                        x['right'][DbCommonAppKeys.Name]
                    ),
                    DbCommonAppKeys.AppId: (
                        x['right'][DbCommonAppKeys.AppId]
                    ),
                    DbCommonAppKeys.RvSeverity: (
                        x['right'][DbCommonAppKeys.RvSeverity]
                    ),
                    DbCommonAppKeys.Hidden: (
                        x['right'][DbCommonAppKeys.Hidden]
                    ),
                    DbCommonAppKeys.ReleaseDate: (
                        x['right'][DbCommonAppKeys.ReleaseDate].to_epoch_time()
                    ),
                    'count': (
                        r
                        .table(AppCollections.AppsPerAgent)
                        .get_all(
                            [
                                x['right'][DbCommonAppKeys.AppId],
                                CommonAppKeys.AVAILABLE
                            ],
                            index=DbCommonAppPerAgentIndexes.AppIdAndStatus
                        )
                        .eq_join(
                            DbCommonAppKeys.AppId,
                            r.table(AppCollections.UniqueApplications)
                        )
                        .filter(
                            lambda y:
                            y['right'][DbCommonAppKeys.Hidden] == CommonKeys.NO
                        )
                        .count()
                    )
                }
            )
            .pluck(
                DbCommonAppKeys.Name, DbCommonAppKeys.AppId,
                DbCommonAppKeys.Hidden, DbCommonAppKeys.RvSeverity,
                DbCommonAppKeys.ReleaseDate, 'count'
            )
            .order_by(r.desc(DbCommonAppKeys.ReleaseDate))
            .limit(count)
            .run(conn)
        )

    except Exception as e:
        logger.exception(e)

    return data


@time_it
@db_create_close
def fetch_os_apps_history(
        customer_name, status, start_date, end_date,
        conn=None
    ):
    """Retrieve all applications and their posted dates
        from start date to end date.
    Args:
        agent_id (str): The 36 character UUID of the tag.
        status (str): available or installed.
        start_date (epoch_time): The date you want the search to begin.
        end_date (epoch_time): The date you want the search to end.

    Basic Usage:
        >>> from vFense.plugins.patching._db_stats import fetch_os_apps_history
        >>> customer_name = 'default'
        >>> status = 'available'
        >>> start_date = 1369195464.0
        >>> end_date = 1400731464.0
        >>> fetch_os_apps_history(customer_name, status, start_date, end_date)

    Returns:
        >>> {
            "timestamp": 1383019200,
            "details": [
                {
                    "reduction": {
                        "count": 3,
                        "apps": [
                            {
                                "version": "2.10.1-0ubuntu0.1",
                                "app_id": "9da05dc98a2f4fa4ac14bed0b9334831955acc43648fff88c53102b194cc2a34",
                                "name": "at-spi2-core"
                            },
                            {
                                "version": "2.10.1-0ubuntu0.1",
                                "app_id": "b2df3c0131248d305d97c953c78635cc8e4c9e3665a571b921d2a91412e7c6b6",
                                "name": "gir1.2-atspi-2.0"
                            },
                            {
                                "version": "2.10.1-0ubuntu0.1",
                                "app_id": "683a5d9be358f277fb35171790e13e4ef4a5a4112827a339219cd8694c795c64",
                                "name": "libatspi2.0-0"
                            }
                        ]
                    },
                    "group": "Recommended"
                }
            ],
            "total_count": 3
        }
    """
    data = []
    try:
        data = (
            r
            .table(AppCollections.AppsPerAgent)
            .get_all(
                [CommonAppKeys.AVAILABLE, customer_name],
                index=DbCommonAppPerAgentIndexes.StatusAndCustomer
            )
            .eq_join(
                DbCommonAppKeys.AppId,
                r.table(AppCollections.UniqueApplications)
            )
            .zip()
            .filter(
                r.row[DbCommonAppKeys.ReleaseDate].during(
                    r.epoch_time(start_date), r.epoch_time(end_date)
                )
            )
            .pluck(
                DbCommonAppKeys.AppId, DbCommonAppKeys.Name,
                DbCommonAppKeys.Version, DbCommonAppKeys.RvSeverity,
                DbCommonAppKeys.ReleaseDate
            )
            .group(
                lambda x: x[DbCommonAppKeys.ReleaseDate].to_epoch_time()
            )
            .map(
                lambda x:
                {
                    'details':
                        [
                            {
                                DbCommonAppKeys.AppId: (
                                    x[DbCommonAppKeys.AppId]
                                ),
                                DbCommonAppKeys.Name: (
                                    x[DbCommonAppKeys.Name]
                                ),
                                DbCommonAppKeys.Version: (
                                    x[DbCommonAppKeys.Version]
                                ),
                                DbCommonAppKeys.RvSeverity: (
                                    x[DbCommonAppKeys.RvSeverity]
                                )
                            }
                        ],
                    CommonAppKeys.COUNT: 1,
                }
            )
            .reduce(
                lambda x, y:
                {
                    "count": x["count"] + y["count"],
                    "details": x["details"] + y["details"],
                }
            )
            .ungroup()
            .map(
                {
                    'timestamp': r.row['group'],
                    'total_count': r.row['reduction']['count'],
                    'details': (
                        r.row['reduction']['details']
                        .group(
                            lambda a: a['rv_severity']
                        )
                        .map(
                            lambda a:
                            {
                                'apps':
                                    [
                                        {
                                            DbCommonAppKeys.AppId: (
                                                a[DbCommonAppKeys.AppId]
                                            ),
                                            DbCommonAppKeys.Name: (
                                                a[DbCommonAppKeys.Name]
                                            ),
                                            DbCommonAppKeys.Version: (
                                                a[DbCommonAppKeys.Version]
                                            ),
                                        }
                                    ],
                                CommonAppKeys.COUNT: 1
                            }
                        )
                        .reduce(
                            lambda a, b:
                            {
                                "count": a["count"] + b["count"],
                                "apps": a["apps"] + b["apps"],
                            }
                        )
                        .ungroup()
                    )
                }
            )
            .run(conn)
        )

    except Exception as e:
        logger.exception(e)

    return data

@time_it
@db_create_close
def fetch_os_apps_history_for_agent(
        agent_id, status, start_date, end_date,
        conn=None
    ):
    """Retrieve all applications and their posted dates
        from start date to end date.
    Args:
        agent_id (str): The 36 character UUID of the tag.
        status (str): available or installed.
        start_date (epoch_time): The date you want the search to begin.
        end_date (epoch_time): The date you want the search to end.

    Basic Usage:
        >>> from vFense.plugins.patching._db_stats import fetch_os_apps_history_for_agent
        >>> agent_id = 'fd0988f5-50c6-4b58-876b-ade20f3e272c'
        >>> status = 'available'
        >>> start_date = 1369195464.0
        >>> end_date = 1400731464.0
        >>> fetch_os_apps_history_for_agent(agent_id, status, start_date, end_date)

    Returns:
        >>> {
            "timestamp": 1383019200,
            "details": [
                {
                    "reduction": {
                        "count": 3,
                        "apps": [
                            {
                                "version": "2.10.1-0ubuntu0.1",
                                "app_id": "9da05dc98a2f4fa4ac14bed0b9334831955acc43648fff88c53102b194cc2a34",
                                "name": "at-spi2-core"
                            },
                            {
                                "version": "2.10.1-0ubuntu0.1",
                                "app_id": "b2df3c0131248d305d97c953c78635cc8e4c9e3665a571b921d2a91412e7c6b6",
                                "name": "gir1.2-atspi-2.0"
                            },
                            {
                                "version": "2.10.1-0ubuntu0.1",
                                "app_id": "683a5d9be358f277fb35171790e13e4ef4a5a4112827a339219cd8694c795c64",
                                "name": "libatspi2.0-0"
                            }
                        ]
                    },
                    "group": "Recommended"
                }
            ],
            "total_count": 3
        }
    """
    data = []
    try:
        data = (
            r
            .table(AppCollections.AppsPerAgent)
            .get_all(
                [status, agent_id],
                index=DbCommonAppPerAgentIndexes.StatusAndAgentId
            )
            .eq_join(
                DbCommonAppKeys.AppId,
                r.table(AppCollections.UniqueApplications)
            )
            .zip()
            .filter(
                r.row[DbCommonAppKeys.ReleaseDate].during(
                    r.epoch_time(start_date), r.epoch_time(end_date)
                )
            )
            .pluck(
                DbCommonAppKeys.AppId, DbCommonAppKeys.Name,
                DbCommonAppKeys.Version, DbCommonAppKeys.RvSeverity,
                DbCommonAppKeys.ReleaseDate
            )
             .group(
                lambda x: x[DbCommonAppKeys.ReleaseDate].to_epoch_time()
            )
            .map(
                lambda x:
                {
                    'details':
                        [
                            {
                                DbCommonAppKeys.AppId: (
                                    x[DbCommonAppKeys.AppId]
                                ),
                                DbCommonAppKeys.Name: (
                                    x[DbCommonAppKeys.Name]
                                ),
                                DbCommonAppKeys.Version: (
                                    x[DbCommonAppKeys.Version]
                                ),
                                DbCommonAppKeys.RvSeverity: (
                                    x[DbCommonAppKeys.RvSeverity]
                                )
                            }
                        ],
                    CommonAppKeys.COUNT: 1,
                }
            )
            .reduce(
                lambda x, y:
                {
                    "count": x["count"] + y["count"],
                    "details": x["details"] + y["details"],
                }
            )
            .ungroup()
            .map(
                {
                    'timestamp': r.row['group'],
                    'total_count': r.row['reduction']['count'],
                    'details': (
                        r.row['reduction']['details']
                        .group(
                            lambda a: a['rv_severity']
                        )
                        .map(
                            lambda a:
                            {
                                'apps':
                                    [
                                        {
                                            DbCommonAppKeys.AppId: (
                                                a[DbCommonAppKeys.AppId]
                                            ),
                                            DbCommonAppKeys.Name: (
                                                a[DbCommonAppKeys.Name]
                                            ),
                                            DbCommonAppKeys.Version: (
                                                a[DbCommonAppKeys.Version]
                                            ),
                                        }
                                    ],
                                CommonAppKeys.COUNT: 1
                            }
                        )
                        .reduce(
                            lambda a, b:
                            {
                                "count": a["count"] + b["count"],
                                "apps": a["apps"] + b["apps"],
                            }
                        )
                        .ungroup()
                    )
                }
            )
            .run(conn)
        )

    except Exception as e:
        logger.exception(e)

    return data


@time_it
@db_create_close
def fetch_os_apps_history_for_tag(
        tag_id, status, start_date, end_date,
        conn=None
    ):
    """Retrieve all applications and their posted dates
        from start date to end date.
    Args:
        tag_id (str): The 36 character UUID of the tag.
        status (str): available or installed.
        start_date (epoch_time): The date you want the search to begin.
        end_date (epoch_time): The date you want the search to end.

    Basic Usage:
        >>> from vFense.plugins.patching._db_stats import fetch_os_apps_history_for_tag
        >>> tag_id = '1e7403c8-36b9-4f16-b29a-57f55a0b3243'
        >>> status = 'available'
        >>> start_date = 1369195464.0
        >>> end_date = 1400731464.0
        >>> fetch_os_apps_history_for_tag(tag_id, status, start_date, end_date)

    Returns:
        >>> {
            "timestamp": 1383019200,
            "details": [
                {
                    "reduction": {
                        "count": 3,
                        "apps": [
                            {
                                "version": "2.10.1-0ubuntu0.1",
                                "app_id": "9da05dc98a2f4fa4ac14bed0b9334831955acc43648fff88c53102b194cc2a34",
                                "name": "at-spi2-core"
                            },
                            {
                                "version": "2.10.1-0ubuntu0.1",
                                "app_id": "b2df3c0131248d305d97c953c78635cc8e4c9e3665a571b921d2a91412e7c6b6",
                                "name": "gir1.2-atspi-2.0"
                            },
                            {
                                "version": "2.10.1-0ubuntu0.1",
                                "app_id": "683a5d9be358f277fb35171790e13e4ef4a5a4112827a339219cd8694c795c64",
                                "name": "libatspi2.0-0"
                            }
                        ]
                    },
                    "group": "Recommended"
                }
            ],
            "total_count": 3
        }
    """
    data = []

    try:
        data = (
            r
            .table(TagCollections.TagsPerAgent, use_outdated=True)
            .get_all(tag_id, index=TagsPerAgentIndexes.TagId)
            .pluck(TagsPerAgentKey.AgentId)
            .eq_join(
                lambda x: [
                    status,
                    x[DbCommonAppPerAgentKeys.AgentId]
                ],
                r.table(AppCollections.AppsPerAgent),
                index=DbCommonAppPerAgentIndexes.StatusAndAgentId
            )
            .zip()
            .eq_join(
                DbCommonAppKeys.AppId,
                r.table(AppCollections.UniqueApplications)
            )
            .zip()
            .filter(
                r.row[DbCommonAppKeys.ReleaseDate].during(
                    r.epoch_time(start_date), r.epoch_time(end_date)
                )
            )
            .pluck(
                DbCommonAppKeys.AppId, DbCommonAppKeys.Name,
                DbCommonAppKeys.Version, DbCommonAppKeys.RvSeverity,
                DbCommonAppKeys.ReleaseDate
            )
             .group(
                lambda x: x[DbCommonAppKeys.ReleaseDate].to_epoch_time()
            )
            .map(
                lambda x:
                {
                    'details':
                        [
                            {
                                DbCommonAppKeys.AppId: (
                                    x[DbCommonAppKeys.AppId]
                                ),
                                DbCommonAppKeys.Name: (
                                    x[DbCommonAppKeys.Name]
                                ),
                                DbCommonAppKeys.Version: (
                                    x[DbCommonAppKeys.Version]
                                ),
                                DbCommonAppKeys.RvSeverity: (
                                    x[DbCommonAppKeys.RvSeverity]
                                )
                            }
                        ],
                    CommonAppKeys.COUNT: 1,
                }
            )
            .reduce(
                lambda x, y:
                {
                    "count": x["count"] + y["count"],
                    "details": x["details"] + y["details"],
                }
            )
            .ungroup()
            .map(
                {
                    'timestamp': r.row['group'],
                    'total_count': r.row['reduction']['count'],
                    'details': (
                        r.row['reduction']['details']
                        .group(
                            lambda a: a['rv_severity']
                        )
                        .map(
                            lambda a:
                            {
                                'apps':
                                    [
                                        {
                                            DbCommonAppKeys.AppId: (
                                                a[DbCommonAppKeys.AppId]
                                            ),
                                            DbCommonAppKeys.Name: (
                                                a[DbCommonAppKeys.Name]
                                            ),
                                            DbCommonAppKeys.Version: (
                                                a[DbCommonAppKeys.Version]
                                            ),
                                        }
                                    ],
                                CommonAppKeys.COUNT: 1
                            }
                        )
                        .reduce(
                            lambda a, b:
                            {
                                "count": a["count"] + b["count"],
                                "apps": a["apps"] + b["apps"],
                            }
                        )
                        .ungroup()
                    )
                }
            )
            .run(conn)
        )


    except Exception as e:
        logger.exception(e)

    return data
