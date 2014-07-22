import logging

from vFense import VFENSE_LOGGING_CONFIG
from vFense.db.client import db_create_close, r
from vFense.core.decorators import time_it
from vFense.core._constants import CommonKeys
from vFense.core.agent._db_model import (
    AgentKeys, AgentCollections, AgentIndexes
)
from vFense.core.tag._db_model import (
    TagCollections, TagsPerAgentKeys, TagsPerAgentIndexes,
)
from vFense.plugins.patching._db_model import (
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
        >>>
        [
            {
                "count": 2059,
                "status": "installed",
                "name": "Software Inventory"
            },
            {
                "count": 21,
                "status": "available",
                "name": "OS"
            },
            {
                "count": 0,
                "status": "available",
                "name": "Custom"
            },
            {
                "count": 0,
                "status": "available",
                "name": "Supported"
            },
            {
                "count": 0,
                "status": "available",
                "name": "Agent Updates"
            }
        ]
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
        >>>
        [
            {
                "count": 2059,
                "status": "installed",
                "name": "Software Inventory"
            },
            {
                "count": 21,
                "status": "available",
                "name": "OS"
            },
            {
                "count": 0,
                "status": "available",
                "name": "Custom"
            },
            {
                "count": 0,
                "status": "available",
                "name": "Supported"
            },
            {
                "count": 0,
                "status": "available",
                "name": "Agent Updates"
            }
        ]
    """
    data = []
    try:
        inventory = (
            r
            .table(TagCollections.TagsPerAgent, use_outdated=True)
            .get_all(tag_id, index=TagsPerAgentIndexes.TagId)
            .pluck(TagsPerAgentKeys.AgentId)
            .eq_join(
                lambda x: [
                    CommonAppKeys.INSTALLED,
                    x[DbCommonAppPerAgentKeys.AgentId]
                ],
                r.table(AppCollections.AppsPerAgent),
                index=DbCommonAppPerAgentIndexes.StatusAndAgentId
            )
            .eq_join(
                lambda x: x['right'][DbCommonAppPerAgentKeys.AppId],
                r.table(AppCollections.UniqueApplications))
            .filter(
                lambda y: y['right'][DbCommonAppKeys.Hidden] == CommonKeys.NO
            )
            .map(
                {
                    DbCommonAppPerAgentKeys.AppId: (
                        r.row['right'][DbCommonAppPerAgentKeys.AppId]
                    ),
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
            .pluck(TagsPerAgentKeys.AgentId)
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
            .pluck(TagsPerAgentKeys.AgentId)
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
            .pluck(TagsPerAgentKeys.AgentId)
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
            .pluck(TagsPerAgentKeys.AgentId)
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

    return data


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
        >>>
        [
            {
                "count": 21,
                "status": "available",
                "name": "OS"
            },
            {
                "count": 0,
                "status": "available",
                "name": "Custom"
            },
            {
                "count": 0,
                "status": "available",
                "name": "Supported"
            },
            {
                "count": 0,
                "status": "available",
                "name": "Agent Updates"
            }
        ]

    """
    data = []
    try:
        os_apps_avail = (
            r
            .table(TagCollections.TagsPerAgent, use_outdated=True)
            .get_all(tag_id, index=TagsPerAgentIndexes.TagId)
            .pluck(TagsPerAgentKeys.AgentId)
            .eq_join(
                lambda x: [
                    CommonAppKeys.AVAILABLE,
                    x[DbCommonAppPerAgentKeys.AgentId]
                ],
                r.table(AppCollections.AppsPerAgent),
                index=DbCommonAppPerAgentIndexes.StatusAndAgentId
            )
            .eq_join(
                lambda x: x['right'][DbCommonAppPerAgentKeys.AppId],
                r.table(AppCollections.UniqueApplications)
            )
            .filter(
                lambda y: y['right'][DbCommonAppKeys.Hidden] == CommonKeys.NO
            )
            .map(
                {
                    DbCommonAppPerAgentKeys.AppId: (
                        r.row['right'][DbCommonAppPerAgentKeys.AppId]
                    ),
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
            .pluck(TagsPerAgentKeys.AgentId)
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
            .pluck(TagsPerAgentKeys.AgentId)
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
            .pluck(TagsPerAgentKeys.AgentId)
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

    return data

@time_it
@db_create_close
def get_all_app_stats_by_view(view_name, conn=None):
    """Retrieve the application stats for a view.
    Args:
        view_name (str): The name of the view you are retrieving
            application statistics for.

    Basic Usage:
        >>> from vFense.plugins.patching._db_stats import get_all_app_stats_by_view
        >>> view_name = 'default'
        >>> get_all_app_stats_by_view(view_name)

    Returns:
        List of application statistics.
        >>>
        [
            {
                "count": 21,
                "status": "available",
                "name": "OS"
            },
            {
                "count": 0,
                "status": "available",
                "name": "Custom"
            },
            {
                "count": 0,
                "status": "available",
                "name": "Supported"
            },
            {
                "count": 0,
                "status": "available",
                "name": "Agent Updates"
            }
        ]
    """
    data = []
    try:
        os_apps_avail = (
            r
            .table(AgentCollections.Agents, use_outdated=True)
            .get_all(view_name, index=AgentIndexes.Views)
            .pluck(AgentKeys.AgentId)
            .eq_join(
                lambda x:
                [
                    CommonAppKeys.AVAILABLE,
                    x[DbCommonAppPerAgentKeys.AgentId]
                ],
                r.table(AppCollections.AppsPerAgent, use_outdated=True),
                index=DbCommonAppPerAgentIndexes.StatusAndAgentId
            )
            .eq_join(
                lambda x:
                x['right'][DbCommonAppKeys.AppId],
                r.table(AppCollections.UniqueApplications)
            )
            .filter(
                lambda x: x['right'][DbCommonAppKeys.Hidden] == CommonKeys.NO
            )
            .map(
                lambda x:
                {
                    DbCommonAppPerAgentKeys.AppId: (
                        x['right'][DbCommonAppPerAgentKeys.AppId]
                    ),
                }
            )
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
            .table(AgentCollections.Agents, use_outdated=True)
            .get_all(view_name, index=AgentIndexes.Views)
            .pluck(AgentKeys.AgentId)
            .eq_join(
                lambda x:
                [
                    CommonAppKeys.AVAILABLE,
                    x[DbCommonAppPerAgentKeys.AgentId]
                ],
                r.table(AppCollections.CustomAppsPerAgent, use_outdated=True),
                index=DbCommonAppPerAgentIndexes.StatusAndAgentId
            )
            .eq_join(
                lambda x:
                x['right'][DbCommonAppKeys.AppId],
                r.table(AppCollections.CustomApps)
            )
            .filter(
                lambda x: x['right'][DbCommonAppKeys.Hidden] == CommonKeys.NO
            )
            .map(
                lambda x:
                {
                    DbCommonAppPerAgentKeys.AppId: (
                        x['right'][DbCommonAppPerAgentKeys.AppId]
                    ),
                }
            )
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
            .table(AgentCollections.Agents, use_outdated=True)
            .get_all(view_name, index=AgentIndexes.Views)
            .pluck(AgentKeys.AgentId)
            .eq_join(
                lambda x:
                [
                    CommonAppKeys.AVAILABLE,
                    x[DbCommonAppPerAgentKeys.AgentId]
                ],
                r.table(
                    AppCollections.SupportedAppsPerAgent, use_outdated=True
                ),
                index=DbCommonAppPerAgentIndexes.StatusAndAgentId
            )
            .eq_join(
                lambda x:
                x['right'][DbCommonAppKeys.AppId],
                r.table(AppCollections.SupportedApps)
            )
            .filter(
                lambda x: x['right'][DbCommonAppKeys.Hidden] == CommonKeys.NO
            )
            .map(
                lambda x:
                {
                    DbCommonAppPerAgentKeys.AppId: (
                        x['right'][DbCommonAppPerAgentKeys.AppId]
                    ),
                }
            )
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
            .table(AgentCollections.Agents, use_outdated=True)
            .get_all(view_name, index=AgentIndexes.Views)
            .pluck(AgentKeys.AgentId)
            .eq_join(
                lambda x:
                [
                    CommonAppKeys.AVAILABLE,
                    x[DbCommonAppPerAgentKeys.AgentId]
                ],
                r.table(
                    AppCollections.vFenseAppsPerAgent, use_outdated=True
                ),
                index=DbCommonAppPerAgentIndexes.StatusAndAgentId
            )
            .eq_join(
                lambda x:
                x['right'][DbCommonAppKeys.AppId],
                r.table(AppCollections.vFenseApps)
            )
            .filter(
                lambda x: x['right'][DbCommonAppKeys.Hidden] == CommonKeys.NO
            )
            .map(
                lambda x:
                {
                    DbCommonAppPerAgentKeys.AppId: (
                        x['right'][DbCommonAppPerAgentKeys.AppId]
                    ),
                }
            )
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
            .table(AgentCollections.Agents, use_outdated=True)
            .get_all(view_name, index=AgentIndexes.Views)
            .pluck(AgentKeys.AgentId)
            .eq_join(
                lambda x:
                [
                    CommonAppKeys.PENDING,
                    x[DbCommonAppPerAgentKeys.AgentId]
                ],
                r.table(
                    AppCollections.AppsPerAgent, use_outdated=True
                ),
                index=DbCommonAppPerAgentIndexes.StatusAndAgentId
            )
            .eq_join(
                lambda x:
                x['right'][DbCommonAppKeys.AppId],
                r.table(AppCollections.UniqueApplications)
            )
            .filter(
                lambda x: x['right'][DbCommonAppKeys.Hidden] == CommonKeys.NO
            )
            .map(
                lambda x:
                {
                    DbCommonAppPerAgentKeys.AppId: (
                        x['right'][DbCommonAppPerAgentKeys.AppId]
                    ),
                }
            )
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

    return data

@time_it
@db_create_close
def group_avail_app_stats_by_os_for_view(
        view_name, count=3, conn=None
    ):
    """Retrieve an array of the total count of update available, grouped by
        operating system for a view.
    Args:
        view_name (str): The name of the view.

    Kwargs:
        count (int, optional): The number of results to return.
            default = 3

    Basic Usage:
        >>> from vFense.plugins.patching._db_stats import group_avail_app_stats_by_os_for_view
        >>> group_avail_app_stats_by_os_for_view('default')

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
            .table(AgentCollections.Agents, use_outdated=True)
            .get_all(view_name, index=AgentIndexes.Views)
            .pluck(AgentKeys.OsString, AgentKeys.AgentId)
            .eq_join(
                lambda x:
                [CommonAppKeys.AVAILABLE, x[DbCommonAppPerAgentKeys.AgentId]],
                r.table(AppCollections.AppsPerAgent, use_outdated=True),
                index=DbCommonAppPerAgentIndexes.StatusAndAgentId
            )
            .eq_join(
                lambda x:
                x['right'][DbCommonAppKeys.AppId],
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
                    AgentKeys.OsString: (
                        r.row['left']['left'][AgentKeys.OsString]
                    )
                }
            )
            .distinct()
            .group(AgentKeys.OsString)
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
            .pluck(TagsPerAgentKeys.AgentId)
            .eq_join(
                lambda x:
                x[AgentKeys.AgentId],
                r.table(AgentCollections.Agents)
            )
            .map(
                lambda x:
                {
                    AgentKeys.AgentId: x['left'][AgentKeys.AgentId],
                    AgentKeys.OsString: x['right'][AgentKeys.OsString]
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
                    AgentKeys.OsString: x['left']['left'][AgentKeys.OsString]
                }
            )
            .distinct()
            .group(AgentKeys.OsString)
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
        app_id, view_name, conn=None
    ):
    """Retreive  the number of nodes that  either have this installed
        or need it to be installed.
    Args:
        app_id (str): The 64 character UUID of the application
        view_name (str): The name of the view.

    Basic Usage:
        >>> from vFense.plugins.patching._db_stats import fetch_bar_chart_for_appid_by_status
        >>> app_id = 'e49d2d84cb5c1e63df9b984646f38e6127242aeba258e29eeefaf180a9be98e7'
        >>> view_name = 'default'
        >>> fetch_bar_chart_for_appid_by_status(app_id, view_name)

    Returns:
        Dictionary
        >>>
        {
            u'available': 1
        }
    """
    data = {}
    try:
        data = (
            r
            .table(AgentCollections.Agents, use_outdated=True)
            .get_all(view_name, index=AgentIndexes.Views)
            .pluck(AgentKeys.AgentId)
            .eq_join(
                lambda x:
                [x[DbCommonAppPerAgentKeys.AgentId], app_id],
                r.table(AppCollections.AppsPerAgent, use_outdated=True),
                index=DbCommonAppPerAgentIndexes.AgentIdAndAppId
            )
            .map(
                lambda x:
                {
                    DbCommonAppPerAgentKeys.AppId: (
                        x['right'][DbCommonAppPerAgentKeys.AppId]
                    ),
                    DbCommonAppPerAgentKeys.Status: (
                        x['right'][DbCommonAppPerAgentKeys.Status]
                    ),
                }
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
def fetch_severity_bar_chart_stats_for_view(view_name, conn=None):
    """Retrieve a list of stats per severity for view.
    Args:
        view_name (str): The name of ther view.

    Basic Usage:
        >>> from vFense.plugins.patching._db_stats import fetch_severity_bar_chart_stats_for_view
        >>> view_name = 'default'
        >>> fetch_severity_bar_chart_stats_for_view(view_name)

    Returns:
        List of dictionaries, Number of updates per severity.
        >>>
        [
            {
                "count": 1,
                "severity": "Optional"
            },
            {
                "count": 3,
                "severity": "Critical"
            },
            {
                "count": 18,
                "severity": "Recommended"
            }
        ]
    """
    data = []
    try:
        data = (
            r
            .table(AgentCollections.Agents, use_outdated=True)
            .get_all(view_name, index=AgentIndexes.Views)
            .pluck(AgentKeys.AgentId)
            .eq_join(
                lambda x:
                [
                    CommonAppKeys.AVAILABLE,
                    x[DbCommonAppPerAgentKeys.AgentId]
                ],
                r.table(AppCollections.AppsPerAgent, use_outdated=True),
                index=DbCommonAppPerAgentIndexes.StatusAndAgentId
            )
            .map(
                lambda x:
                {
                    DbCommonAppKeys.AppId: (
                        x['right'][DbCommonAppKeys.AppId]
                    )
                }
            )
            .distinct()
            .eq_join(
                lambda x:
                x[DbCommonAppKeys.AppId],
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
                    DbCommonAppKeys.vFenseSeverity: (
                        r.row['right'][DbCommonAppKeys.vFenseSeverity]
                    )
                }
            )
            .group(DbCommonAppKeys.vFenseSeverity)
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
    """Retrieve a list of stats per severity for  an agent.
    Args:
        agent_id (str): 36 character UUID of an agent.

    Basic Usage:
        >>> from vFense.plugins.patching._db_stats import fetch_severity_bar_chart_stats_for_agent
        >>> agent_id = '114ef1ea-7fbc-4505-b702-1500f89e969c'
        >>> fetch_severity_bar_chart_stats_for_agent(agent_id)

    Returns:
        List of dictionaries, Number of updates per severity.
        >>>
        [
            {
                "count": 1,
                "severity": "Optional"
            },
            {
                "count": 3,
                "severity": "Critical"
            },
            {
                "count": 18,
                "severity": "Recommended"
            }
        ]
    """
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
                    DbCommonAppKeys.vFenseSeverity: (
                        r.row['right'][DbCommonAppKeys.vFenseSeverity]
                    )
                }
            )
            .group(DbCommonAppKeys.vFenseSeverity)
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
    """Retrieve a list of stats per severity for an tag.
    Args:
        agent_id (str): 36 character UUID of an agent.

    Basic Usage:
        >>> from vFense.plugins.patching._db_stats import fetch_severity_bar_chart_stats_for_tag
        >>> tag_id = '14dc332d-6ae1-46ba-8290-2619413816f9'
        >>> fetch_severity_bar_chart_stats_for_tag(tag_id)

    Returns:
        List of dictionaries, Number of updates per severity.
        >>>
        [
            {
                "count": 1,
                "severity": "Optional"
            },
            {
                "count": 3,
                "severity": "Critical"
            },
            {
                "count": 18,
                "severity": "Recommended"
            }
        ]
    """

    data = []
    try:
        data = (
            r
            .table(TagCollections.TagsPerAgent, use_outdated=True)
            .get_all(tag_id, index=TagsPerAgentIndexes.TagId)
            .pluck(TagsPerAgentKeys.AgentId)
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
                    DbCommonAppKeys.vFenseSeverity: (
                        r.row['right'][DbCommonAppKeys.vFenseSeverity]
                    )
                }
            )
            .group(DbCommonAppKeys.vFenseSeverity)
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
def fetch_top_apps_needed_for_view(view_name, count=5, conn=None):
    """Retrieve the top applications upadtes that are needed for a view.
    Args:
        view_name (str): The name of the view.

    Kwargs:
        count (int, optional): The number of results to return.

    Basic Usage:
        >>> from vFense.plugins.patching._db_stats import fetch_top_apps_needed_for_view
        >>> view_name = 'default'
        >>> count = 3
        >>> fetch_top_apps_needed_for_view(view_name, count)

    Returns:
        List of dictionaries.
        >>>
        [
            {
                "count": 1,
                "vfense_severity": "Recommended",
                "release_date": 1400644800,
                "app_id": "1a3c80714af0eeb7f739e8f42f80d41fe33ffce1d012fff7648b6e5658594e90",
                "name": "rethinkdb"
            },
            {
                "count": 1,
                "vfense_severity": "Recommended",
                "release_date": 1400644800,
                "app_id": "e49d2d84cb5c1e63df9b984646f38e6127242aeba258e29eeefaf180a9be98e7",
                "name": "python3-lxml"
            },
            {
                "count": 1,
                "vfense_severity": "Recommended",
                "release_date": 1400644800,
                "app_id": "8683a443a58aefcd5cef3025e6307569c6b722eccb64c9573750a4d11c0ffbe8",
                "name": "python-lxml"
            }
        ]
    """
    data=[]
    try:
        data = (
            r
            .table(AgentCollections.Agents, use_outdated=True)
            .get_all(view_name, index=AgentIndexes.Views)
            .pluck(AgentKeys.AgentId)
            .eq_join(
                lambda x:
                [
                    CommonAppKeys.AVAILABLE,
                    x[DbCommonAppPerAgentKeys.AgentId]
                ],
                r.table(AppCollections.AppsPerAgent, use_outdated=True),
                index=DbCommonAppPerAgentIndexes.StatusAndAgentId
            )
            .eq_join(
                lambda x:
                x['right'][DbCommonAppKeys.AppId],
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
                    DbCommonAppKeys.vFenseSeverity: (
                        x['right'][DbCommonAppKeys.vFenseSeverity]
                    ),
                    DbCommonAppKeys.ReleaseDate: (
                        x['right'][DbCommonAppKeys.ReleaseDate].to_epoch_time()
                    ),
                }
            )
            .group(
                DbCommonAppKeys.Name, DbCommonAppKeys.AppId,
                DbCommonAppKeys.vFenseSeverity, DbCommonAppKeys.ReleaseDate
            )
            .count()
            .ungroup()
            .map(
                lambda x:
                {
                    DbCommonAppKeys.Name: x['group'][0],
                    DbCommonAppKeys.AppId: x['group'][1],
                    DbCommonAppKeys.vFenseSeverity: x['group'][2],
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
def fetch_recently_released_apps(view_name, count=5, conn=None):
    """Fetch the latest available updates for a view.
    Args:
        view_name (str): The name of the view.
    Kwargs:
        count (int): The number of results to return.

    Basic Usage:
        >>> from vFense.plugins.patching._db_stats import fetch_recently_released_apps
        >>> view_name = 'default'
        >>> count = 3
        >>> fetch_recently_released_apps(view_name, count)

    Returns:
    >>> [
        {
            "count": 1,
            "vfense_severity": "Recommended",
            "release_date": 1400644800,
            "app_id": "4aaad1b2275141e0ccc5ee607377be28a947c0349128d3f066dba6b266fb2cf2",
            "hidden": "no",
            "name": "pidgin"
        },
        {
            "count": 1,
            "vfense_severity": "Recommended",
            "release_date": 1400644800,
            "app_id": "8bfbffd62cb74869119f28dbbdc06d4ce651286a5105b3c20227b60e4fad741d",
            "hidden": "no",
            "name": "libpurple0"
        },
        {
            "count": 1,
            "vfense_severity": "Recommended",
            "release_date": 1400644800,
            "app_id": "d081e1372cee5ae368b94d064982ddaad67c40aacd8c845570b97ee69c5adef4",
            "hidden": "no",
            "name": "rethinkdb"
        }
    ]
    """
    data = []
    try:
        data = list(
            r
            .table(AgentCollections.Agents, use_outdated=True)
            .get_all(view_name, index=AgentIndexes.Views)
            .pluck(AgentKeys.AgentId)
            .eq_join(
                lambda x:
                [
                    CommonAppKeys.AVAILABLE,
                    x[DbCommonAppPerAgentKeys.AgentId]
                ],
                r.table(AppCollections.AppsPerAgent, use_outdated=True),
                index=DbCommonAppPerAgentIndexes.StatusAndAgentId
            )
            .eq_join(
                lambda x:
                x['right'][DbCommonAppKeys.AppId],
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
                    DbCommonAppKeys.vFenseSeverity: (
                        x['right'][DbCommonAppKeys.vFenseSeverity]
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
                DbCommonAppKeys.Hidden, DbCommonAppKeys.vFenseSeverity,
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
        view_name, status, start_date, end_date,
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
        >>> view_name = 'default'
        >>> status = 'available'
        >>> start_date = 1369195464.0
        >>> end_date = 1400731464.0
        >>> fetch_os_apps_history(view_name, status, start_date, end_date)

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
            .table(AgentCollections.Agents, use_outdated=True)
            .get_all(view_name, index=AgentIndexes.Views)
            .pluck(AgentKeys.AgentId)
            .eq_join(
                lambda x:
                [
                    status,
                    x[DbCommonAppPerAgentKeys.AgentId]
                ],
                r.table(AppCollections.AppsPerAgent, use_outdated=True),
                index=DbCommonAppPerAgentIndexes.StatusAndAgentId
            )
            .eq_join(
                lambda x:
                x['right'][DbCommonAppKeys.AppId],
                r.table(AppCollections.UniqueApplications)
            )
            .map(
                lambda x:
                {
                    DbCommonAppKeys.AppId: (
                        x['right'][DbCommonAppKeys.AppId]
                    ),
                    DbCommonAppKeys.Name: (
                        x['right'][DbCommonAppKeys.Name]
                    ),
                    DbCommonAppKeys.Version: (
                        x['right'][DbCommonAppKeys.Version]
                    ),
                    DbCommonAppKeys.ReleaseDate: (
                        x['right'][DbCommonAppKeys.ReleaseDate]
                    ),
                    DbCommonAppKeys.vFenseSeverity: (
                        x['right'][DbCommonAppKeys.vFenseSeverity]
                    ),
                }
            )
            .filter(
                r.row[DbCommonAppKeys.ReleaseDate].during(
                    r.epoch_time(start_date), r.epoch_time(end_date)
                )
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
                                DbCommonAppKeys.vFenseSeverity: (
                                    x[DbCommonAppKeys.vFenseSeverity]
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
                            lambda a: a['vfense_severity']
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
            .map(
                lambda x:
                {
                    DbCommonAppKeys.AppId: (
                        x['right'][DbCommonAppKeys.AppId]
                    ),
                    DbCommonAppKeys.Name: (
                        x['right'][DbCommonAppKeys.Name]
                    ),
                    DbCommonAppKeys.Version: (
                        x['right'][DbCommonAppKeys.Version]
                    ),
                    DbCommonAppKeys.ReleaseDate: (
                        x['right'][DbCommonAppKeys.ReleaseDate]
                    ),
                    DbCommonAppKeys.vFenseSeverity: (
                        x['right'][DbCommonAppKeys.vFenseSeverity]
                    ),
                }
            )
            .filter(
                r.row[DbCommonAppKeys.ReleaseDate].during(
                    r.epoch_time(start_date), r.epoch_time(end_date)
                )
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
                                DbCommonAppKeys.vFenseSeverity: (
                                    x[DbCommonAppKeys.vFenseSeverity]
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
                            lambda a: a['vfense_severity']
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
            .pluck(TagsPerAgentKeys.AgentId)
            .eq_join(
                lambda x: [
                    status,
                    x[DbCommonAppPerAgentKeys.AgentId]
                ],
                r.table(AppCollections.AppsPerAgent),
                index=DbCommonAppPerAgentIndexes.StatusAndAgentId
            )
            .eq_join(
                lambda x:
                x['right'][DbCommonAppKeys.AppId],
                r.table(AppCollections.UniqueApplications)
            )
            .map(
                lambda x:
                {
                    DbCommonAppKeys.AppId: (
                        x['right'][DbCommonAppKeys.AppId]
                    ),
                    DbCommonAppKeys.Name: (
                        x['right'][DbCommonAppKeys.Name]
                    ),
                    DbCommonAppKeys.Version: (
                        x['right'][DbCommonAppKeys.Version]
                    ),
                    DbCommonAppKeys.ReleaseDate: (
                        x['right'][DbCommonAppKeys.ReleaseDate]
                    ),
                    DbCommonAppKeys.vFenseSeverity: (
                        x['right'][DbCommonAppKeys.vFenseSeverity]
                    ),
                }
            )
            .filter(
                r.row[DbCommonAppKeys.ReleaseDate].during(
                    r.epoch_time(start_date), r.epoch_time(end_date)
                )
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
                                DbCommonAppKeys.vFenseSeverity: (
                                    x[DbCommonAppKeys.vFenseSeverity]
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
                            lambda a: a['vfense_severity']
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
