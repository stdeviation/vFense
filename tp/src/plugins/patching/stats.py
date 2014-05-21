#!/usr/bin/env python
import logging
from time import mktime
from datetime import datetime, timedelta

from vFense import VFENSE_LOGGING_CONFIG
from vFense.db.client import db_create_close, r
from vFense.core._constants import CommonKeys
from vFense.core.decorators import results_message, time_it
from vFense.plugins.patching._constants import CommonAppKeys, CommonSeverityKeys
from vFense.plugins.patching._db_stats import (
    group_avail_app_stats_by_os_for_customer,
    group_avail_app_stats_by_os_for_tag
)
from vFense.errorz.error_messages import GenericResults
from vFense.errorz.status_codes import GenericCodes
from vFense.errorz._constants import ApiResultKeys
logging.config.fileConfig(VFENSE_LOGGING_CONFIG)
logger = logging.getLogger('rvapi')


@time_it
@results_message
def customer_stats_by_os(
        customer_name, count=3,
        username=None, uri=None, method=None
    ):
    data = group_avail_app_stats_by_os_for_customer(customer_name, count)
    results = {
        ApiResultKeys.GENERIC_STATUS_CODE: GenericCodes.InformationRetrieved,
        ApiResultKeys.VFENSE_STATUS_CODE: GenericCodes.InformationRetrieved,
        ApiResultKeys.DATA: data,
        ApiResultKeys.USERNAME: username,
        ApiResultKeys.URI: uri,
        ApiResultKeys.HTTP_METHOD: method
    }
    return(results)


def tag_stats_by_os(
        tag_id, count=3,
        username=None, uri=None, method=None
    ):
    data = group_avail_app_stats_by_os_for_tag(tag_id, count)
    results = {
        ApiResultKeys.GENERIC_STATUS_CODE: GenericCodes.InformationRetrieved,
        ApiResultKeys.VFENSE_STATUS_CODE: GenericCodes.InformationRetrieved,
        ApiResultKeys.DATA: data,
        ApiResultKeys.USERNAME: username,
        ApiResultKeys.URI: uri,
        ApiResultKeys.HTTP_METHOD: method
    }

    return(results)

@db_create_close
def bar_chart_for_appid_by_status(app_id=None, customer_name='default',
                                 conn=None):
    statuses = ['installed', 'available'] 
    try:
        status = (
            r
            .table(AppCollections.AppsPerAgent, use_outdated=True)
            .get_all([app_id, customer_name], index=AppsPerAgentIndexes.AppIdAndCustomer)
            .group('status')
            .count()
            .run(conn)
        )

    except Exception as e:
        msg = (
            'Couldnt get bar chart stats for appid %s for customer %s: %s' %
            (customer_name, e)
        )
        logger.error(msg)

    new_status = {}
    for stat in status:
        new_status[stat['group']['status']] = stat['reduction']
    for s in statuses:
        if not s in new_status:
            new_status[s] = 0.0

    return(
        {
            'pass': True,
            'message': '',
            'data': [new_status]
        }
    )

def app_stats_by_severity(sevs):
    try:
        new_sevs = []
        for i in xrange(len(sevs)):
            sevs[i] = (
                {
                    'severity': sevs[i]['group'],
                    'count': sevs[i]['reduction']
                }
            )
        sevs_in_sevs = map(lambda x: x['severity'], sevs)
        difference = list(set(CommonSeverityKeys.ValidRvSeverities).difference(sevs_in_sevs))

        if difference:
            for sev in difference:
                sevs.append(
                    {
                        'severity': sev,
                        'count': 0
                    }
                )

        for sev in sevs:
            if sev['severity'] == CommonSeverityKeys.CRITICAL:
                crit = sev

            elif sev['severity'] == CommonSeverityKeys.OPTIONAL:
                opt = sev

            elif sev['severity'] == CommonSeverityKeys.RECOMMENDED:
                rec = sev

        new_sevs.append(opt)
        new_sevs.append(crit)
        new_sevs.append(rec)

    except Exception as e:
        logger.exception(e)

    return(new_sevs)

@db_create_close
def get_severity_bar_chart_stats_for_customer(username, customer_name,
                                              uri, method, conn=None):
    try:
        sevs = (
            r
            .table(AppCollections.AppsPerAgent, use_outdated=True)
            .get_all(
                [CommonAppKeys.AVAILABLE, customer_name],
                index=AppsPerAgentIndexes.StatusAndCustomer
            )
            .pluck(AppsKey.AppId)
            .distinct()
            .eq_join(AppsKey.AppId, r.table(AppCollections.UniqueApplications))
            .filter(
                lambda x: x['right'][AppsKey.Hidden] == CommonKeys.NO
            )
            .map(
                {
                    AppsKey.AppId: r.row['right'][AppsKey.AppId],
                    AppsKey.RvSeverity: r.row['right'][AppsKey.RvSeverity]
                }
            )
            .group(AppsKey.RvSeverity)
            .count()
            .ungroup()
            .order_by(r.asc('group'))
            .run(conn)
        )
        data = app_stats_by_severity(sevs)

        results = (
            GenericResults(
                username, uri, method
            ).information_retrieved(data, len(CommonSeverityKeys.ValidRvSeverities))
        )

    except Exception as e:
        results = (
            GenericResults(
                username, uri, method
            ).something_broke('widget severity stats', 'widget', e)
        )
        logger.exception(results)

    return(results)


@db_create_close
def get_severity_bar_chart_stats_for_agent(username, customer_name,
                                           uri, method, agent_id, conn=None):
    try:
        sevs = (
            r
            .table(AppCollections.AppsPerAgent, use_outdated=True)
            .get_all(
                [CommonAppKeys.AVAILABLE, agent_id],
                index=AppsPerAgentIndexes.StatusAndAgentId
            )
            .eq_join(AppsKey.AppId, r.table(AppCollections.UniqueApplications))
            .filter(
                lambda x: x['right'][AppsKey.Hidden] == CommonKeys.NO
            )
            .map(
                {
                    AppsKey.AppId: r.row['right'][AppsKey.AppId],
                    AppsKey.RvSeverity: r.row['right'][AppsKey.RvSeverity]
                }
            )
            .group(AppsKey.RvSeverity)
            .count()
            .ungroup()
            .order_by(r.desc('reduction'))
            .run(conn)
        )
        data = app_stats_by_severity(sevs)

        results = (
            GenericResults(
                username, uri, method
            ).information_retrieved(data, len(CommonSeverityKeys.ValidRvSeverities))
        )

    except Exception as e:
        results = (
            GenericResults(
                username, uri, method
            ).something_broke('widget severity stats', 'widget', e)
        )
        logger.exception(results)

    return(results)


@db_create_close
def get_severity_bar_chart_stats_for_tag(username, customer_name,
                                         uri, method, tag_id, conn=None):
    try:
        sevs = (
            r
            .table(TagsPerAgentCollection, use_outdated=True)
            .get_all(tag_id, index=TagsPerAgentIndexes.TagId)
            .pluck(TagsPerAgentKey.AgentId)
            .eq_join(
                lambda x: [
                    CommonAppKeys.AVAILABLE,
                    x[AppsPerAgentKey.AgentId]
                ],
                r.table(AppCollections.AppsPerAgent),
                index=AppsPerAgentIndexes.StatusAndAgentId
            )
            .map(
                {
                    AppsKey.AppId: r.row['right'][AppsKey.AppId],
                }
            )
            .eq_join(AppsKey.AppId, r.table(AppCollections.UniqueApplications))
            .filter(
                lambda x: x['right'][AppsKey.Hidden] == CommonKeys.NO
            )
            .map(
                {
                    AppsKey.AppId: r.row['right'][AppsKey.AppId],
                    AppsKey.RvSeverity: r.row['right'][AppsKey.RvSeverity]
                }
            )
            .group(AppsKey.RvSeverity)
            .count()
            .ungroup()
            .order_by(r.desc('reduction'))
            .run(conn)
        )
        data = app_stats_by_severity(sevs)

        results = (
            GenericResults(
                username, uri, method
            ).information_retrieved(data, len(CommonSeverityKeys.ValidRvSeverities))
        )

    except Exception as e:
        results = (
            GenericResults(
                username, uri, method
            ).something_broke('widget severity stats', 'widget', e)
        )
        logger.exception(results)

    return(results)


@db_create_close
def top_packages_needed(username, customer_name,
                        uri, method, count=5, conn=None):
    
    apps_needed=[]
    
    try:
        data = (
            r
            .table(AppCollections.AppsPerAgent)
            .get_all(
                [CommonAppKeys.AVAILABLE, customer_name],
                index=AppsPerAgentIndexes.StatusAndCustomer
            )
            .eq_join(AppsKey.AppId, r.table(AppCollections.UniqueApplications))
            .filter(
                lambda x: x['right'][AppsKey.Hidden] == CommonKeys.NO
            )
            .map(
                lambda x:
                {
                    AppsKey.Name: x['right'][AppsKey.Name],
                    AppsKey.AppId: x['right'][AppsKey.AppId],
                    AppsKey.RvSeverity: x['right'][AppsKey.RvSeverity],
                    AppsKey.ReleaseDate: x['right'][AppsKey.ReleaseDate].to_epoch_time(),
                }
            )
            .group(AppsKey.Name, AppsKey.AppId, AppsKey.RvSeverity, AppsKey.ReleaseDate)
            .count()
            .ungroup()
            .map(
                lambda x:
                {
                    AppsKey.Name: x['group'][0],
                    AppsKey.AppId: x['group'][1],
                    AppsKey.RvSeverity: x['group'][2],
                    AppsKey.ReleaseDate: x['group'][3],
                    'count': x['reduction'],
                }
            )
            .order_by(r.desc('count'), r.desc(AppsKey.ReleaseDate))
            .limit(count)
            .run(conn)
        )

        results = (
            GenericResults(
                username, uri, method
            ).information_retrieved(data, count)
        )

    except Exception as e:
        results = (
            GenericResults(
                username, uri, method
            ).something_broke('top os apps needed', 'widget', e)
        )
        logger.exception(results)

    return(results)


@db_create_close
def recently_released_packages(username, customer_name,
                               uri, method, count=5, conn=None):

    data=[]

    try:
        data = list(
            r
            .table(AppCollections.AppsPerAgent, use_outdated=True)
            .get_all(
                [
                    CommonAppKeys.AVAILABLE, customer_name
                ],
                index=AppsPerAgentIndexes.StatusAndCustomer
            )
            .eq_join(AppsKey.AppId, r.table(AppCollections.UniqueApplications))
            .map(
                lambda x:
                {
                    AppsKey.Name: x['right'][AppsKey.Name],
                    AppsKey.AppId: x['right'][AppsKey.AppId],
                    AppsKey.RvSeverity: x['right'][AppsKey.RvSeverity],
                    AppsKey.Hidden: x['right'][AppsKey.Hidden],
                    AppsKey.ReleaseDate: x['right'][AppsKey.ReleaseDate].to_epoch_time(),
                    'count': (
                        r
                        .table(AppCollections.AppsPerAgent)
                        .get_all(
                            [x['right'][AppsKey.AppId], CommonAppKeys.AVAILABLE],
                            index=AppsPerAgentIndexes.AppIdAndStatus
                        )
                        .eq_join(AppsKey.AppId, r.table(AppCollections.UniqueApplications))
                        .filter(
                            lambda y: y['right'][AppsKey.Hidden] == CommonKeys.NO
                        )
                        .count()
                    )
                }
            )
            .pluck(
                AppsKey.Name, AppsKey.AppId,AppsKey.Hidden,
                AppsKey.RvSeverity, AppsKey.ReleaseDate, 'count'
            )
            .order_by(r.desc(AppsKey.ReleaseDate))
            .limit(count)
            .run(conn)
        )

        results = (
            GenericResults(
                username, uri, method
            ).information_retrieved(data, count)
        )

    except Exception as e:
        results = (
            GenericResults(
                username, uri, method
            ).something_broke('recently released os apps', 'widget', e)
        )
        logger.exception(results)

    return(results)


@db_create_close
def get_os_apps_history(username, customer_name, uri, method, status,
                        start_date=None, end_date=None, conn=None):

    try:
        if not start_date and not end_date:
            start_date = mktime((datetime.now() - timedelta(days=1*365)).timetuple())
            end_date = mktime(datetime.now().timetuple())

        elif start_date and not end_date:
            end_date = mktime(datetime.now().timetuple())

        elif not start_date and end_date:
            start_date = 0.0
        data = (
            r
            .table(AppCollections.AppsPerAgent)
            .get_all(
                [CommonAppKeys.AVAILABLE, customer_name],
                index=AppsPerAgentIndexes.StatusAndCustomer
            )
            .eq_join(AppsKey.AppId, r.table(AppCollections.UniqueApplications))
            .zip()
            .filter(
                r.row[AppsKey.ReleaseDate].during(
                    r.epoch_time(start_date), r.epoch_time(end_date)
                )
            )
            .pluck(
                AppsKey.AppId, AppsKey.Name, AppsKey.Version,
                AppsKey.RvSeverity, AppsKey.ReleaseDate
            )
            .group(
                lambda x: x[AppsKey.ReleaseDate].to_epoch_time()
            )
            .map(
                lambda x:
                {
                    'details':
                        [
                            {
                                AppsKey.AppId: x[AppsKey.AppId],
                                AppsKey.Name: x[AppsKey.Name],
                                AppsKey.Version: x[AppsKey.Version],
                                AppsKey.RvSeverity: x[AppsKey.RvSeverity]
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
                                            AppsKey.AppId: a[AppsKey.AppId],
                                            AppsKey.Name: a[AppsKey.Name],
                                            AppsKey.Version: a[AppsKey.Version],
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

        results = (
            GenericResults(
                username, uri, method
            ).information_retrieved(data, len(data))
        )

    except Exception as e:
        results = (
            GenericResults(
                username, uri, method
            ).something_broke('available apps over time graph', 'graph', e)
        )
        logger.exception(results)

    return(results)

@db_create_close
def get_os_apps_history_for_agent(username, customer_name, uri, method,
                                  agent_id, status, start_date=None,
                                  end_date=None, conn=None):

    try:
        if not start_date and not end_date:
            start_date = mktime((datetime.now() - timedelta(days=1*365)).timetuple())
            end_date = mktime(datetime.now().timetuple())

        elif start_date and not end_date:
            end_date = mktime(datetime.now().timetuple())

        elif not start_date and end_date:
            start_date = 0.0
        data = (
            r
            .table(AppCollections.AppsPerAgent)
            .get_all(
                [status, agent_id],
                index=AppsPerAgentIndexes.StatusAndAgentId
            )
            .eq_join(AppsKey.AppId, r.table(AppCollections.UniqueApplications))
            .zip()
            .filter(
                r.row[AppsKey.ReleaseDate].during(
                    r.epoch_time(start_date), r.epoch_time(end_date)
                )
            )
            .pluck(
                AppsKey.AppId, AppsKey.Name, AppsKey.Version,
                AppsKey.RvSeverity, AppsKey.ReleaseDate
            )
             .group(
                lambda x: x[AppsKey.ReleaseDate].to_epoch_time()
            )
            .map(
                lambda x:
                {
                    'details':
                        [
                            {
                                AppsKey.AppId: x[AppsKey.AppId],
                                AppsKey.Name: x[AppsKey.Name],
                                AppsKey.Version: x[AppsKey.Version],
                                AppsKey.RvSeverity: x[AppsKey.RvSeverity]
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
                                            AppsKey.AppId: a[AppsKey.AppId],
                                            AppsKey.Name: a[AppsKey.Name],
                                            AppsKey.Version: a[AppsKey.Version],
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

        results = (
            GenericResults(
                username, uri, method
            ).information_retrieved(data, len(data))
        )

    except Exception as e:
        results = (
            GenericResults(
                username, uri, method
            ).something_broke('available apps over time graph', 'graph', e)
        )
        logger.exception(results)

    return(results)

@db_create_close
def get_os_apps_history_for_tag(username, customer_name, uri, method,
                                tag_id, status, start_date=None,
                                end_date=None, conn=None):

    try:
        if not start_date and not end_date:
            start_date = mktime((datetime.now() - timedelta(days=1*365)).timetuple())
            end_date = mktime(datetime.now().timetuple())

        elif start_date and not end_date:
            end_date = mktime(datetime.now().timetuple())

        elif not start_date and end_date:
            start_date = 0.0
        data = (
            r
            .table(TagsPerAgentCollection, use_outdated=True)
            .get_all(tag_id, index=TagsPerAgentIndexes.TagId)
            .pluck(TagsPerAgentKey.AgentId)
            .eq_join(
                lambda x: [
                    status,
                    x[AppsPerAgentKey.AgentId]
                ],
                r.table(AppCollections.AppsPerAgent),
                index=AppsPerAgentIndexes.StatusAndAgentId
            )
            .zip()
            .eq_join(AppsKey.AppId, r.table(AppCollections.UniqueApplications))
            .zip()
            .filter(
                r.row[AppsKey.ReleaseDate].during(
                    r.epoch_time(start_date), r.epoch_time(end_date)
                )
            )
            .pluck(
                AppsKey.AppId, AppsKey.Name, AppsKey.Version,
                AppsKey.RvSeverity, AppsKey.ReleaseDate
            )
             .group(
                lambda x: x[AppsKey.ReleaseDate].to_epoch_time()
            )
            .map(
                lambda x:
                {
                    'details':
                        [
                            {
                                AppsKey.AppId: x[AppsKey.AppId],
                                AppsKey.Name: x[AppsKey.Name],
                                AppsKey.Version: x[AppsKey.Version],
                                AppsKey.RvSeverity: x[AppsKey.RvSeverity]
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
                                            AppsKey.AppId: a[AppsKey.AppId],
                                            AppsKey.Name: a[AppsKey.Name],
                                            AppsKey.Version: a[AppsKey.Version],
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

        results = (
            GenericResults(
                username, uri, method
            ).information_retrieved(data, len(data))
        )

    except Exception as e:
        results = (
            GenericResults(
                username, uri, method
            ).something_broke('available apps over time graph', 'graph', e)
        )
        logger.exception(results)

    return(results)
