#!/usr/bin/env python
import logging
from time import mktime
from datetime import datetime, timedelta

from vFense import VFENSE_LOGGING_CONFIG
from vFense.db.client import db_create_close, r
from vFense.core._constants import CommonKeys
from vFense.core.decorators import results_message, time_it
from vFense.plugins.patching import *
from vFense.plugins.patching._constants import CommonAppKeys, CommonSeverityKeys
from vFense.plugins.patching._db_stats import (
    group_avail_app_stats_by_os_for_customer,
    group_avail_app_stats_by_os_for_tag, fetch_bar_chart_for_appid_by_status,
    fetch_severity_bar_chart_stats_for_agent,
    fetch_severity_bar_chart_stats_for_tag,
    fetch_top_apps_needed_for_customer, fetch_os_apps_history,
    fetch_recently_released_apps, fetch_severity_bar_chart_stats_for_customer,
    fetch_os_apps_history_for_agent, fetch_os_apps_history_for_tag
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
    """Retrieve an array of the total count of update available, grouped by
        operating system for a customer.
    Args:
        customer_name (str): The name of the customer.

    Kwargs:
        count (int, optional): The number of results to return.
            default = 3
        username (str): The name of the user who called this function.
        uri (str): The uri that was used to call this function.
        method (str): The HTTP methos that was used to call this function.

    Basic Usage:
        >>> from vFense.plugins.patching._db_stats import group_avail_app_stats_by_os_for_customer
        >>> group_avail_app_stats_by_os_for_customer('default')

    Returns:
        >>>
        {
            "count": 1,
            "uri": "/api/v1/dashboard/graphs/bar/stats_by_os",
            "rv_status_code": 1001,
            "http_method": "GET",
            "http_status": 200,
            "message": "admin - data was retrieved",
            "data": [
                {
                    "count": 22,
                    "os": "Ubuntu 14.04"
                }
            ]
        }
    """
    data = group_avail_app_stats_by_os_for_customer(customer_name, count)
    results = {
        ApiResultKeys.GENERIC_STATUS_CODE: GenericCodes.InformationRetrieved,
        ApiResultKeys.VFENSE_STATUS_CODE: GenericCodes.InformationRetrieved,
        ApiResultKeys.DATA: data,
        ApiResultKeys.COUNT: len(data),
        ApiResultKeys.USERNAME: username,
        ApiResultKeys.URI: uri,
        ApiResultKeys.HTTP_METHOD: method
    }
    return results


@time_it
@results_message
def tag_stats_by_os(
        tag_id, count=3,
        username=None, uri=None, method=None
    ):
    """Retrieve application stats for a tag and group it by the os string.
    Args:
        tag_id (str): The 36 character UUID of the tag

    Kwargs:
        count (int, optional): Limit how many results show.
            default = 3
        username (str): The name of the user who called this function.
        uri (str): The uri that was used to call this function.
        method (str): The HTTP methos that was used to call this function.

    Basic Usage:
        >>> from vFense.plugins.patching._db_stats import tag_stats_by_os
        >>> tag_id = '14dc332d-6ae1-46ba-8290-2619413816f9'
        >>> count = 3
        >>> tag_stats_by_os(tag_id, count)

    Returns:
        >>>
        {
            "count": 1,
            "uri": "/api/v1/tag/14dc332d-6ae1-46ba-8290-2619413816f9/stats_by_os",
            "rv_status_code": 1001,
            "http_method": "GET",
            "http_status": 200,
            "message": "admin - data was retrieved",
            "data": [
                {
                     "count": 22,
                     "os": "Ubuntu 14.04"
                }
            ]
        }
    """
    data = group_avail_app_stats_by_os_for_tag(tag_id, count)
    results = {
        ApiResultKeys.GENERIC_STATUS_CODE: GenericCodes.InformationRetrieved,
        ApiResultKeys.VFENSE_STATUS_CODE: GenericCodes.InformationRetrieved,
        ApiResultKeys.DATA: data,
        ApiResultKeys.COUNT: len(data),
        ApiResultKeys.USERNAME: username,
        ApiResultKeys.URI: uri,
        ApiResultKeys.HTTP_METHOD: method
    }

    return results


@time_it
@results_message
def bar_chart_for_appid_by_status(
        app_id, customer_name,
        username=None, uri=None, method=None
    ):
    """Retrieve application stats for a tag and group it by the os string.
    Args:
        app_id (str): The 64 character hex digest of the app.
        customer_name (str): The name of the customer.

    Kwargs:
        username (str): The name of the user who called this function.
        uri (str): The uri that was used to call this function.
        method (str): The HTTP methos that was used to call this function.

    Basic Usage:
        >>> from vFense.plugins.patching._db_stats import bar_chart_for_appid_by_status
        >>> app_id = 'aa565bb450cc7c15d6a7dbf177c31a1c6f5245e70b8014ffe5d098f85342d4fb'
        >>> customer_name = 'default'
        >>> bar_chart_for_appid_by_status(tag_id, count)

    Returns:
        >>>
        {
            "count": 2,
            "uri": null,
            "rv_status_code": 1001,
            "http_method": null,
            "http_status": 200,
            "message": "None - data was retrieved",
            "data": {
                "available": 1,
                "installed": 0
            }
        }
    """
    statuses = ['installed', 'available']
    data = fetch_bar_chart_for_appid_by_status(app_id, customer_name)
    for status in statuses:
        if status not in data.keys():
            data[status] = 0

    results = {
        ApiResultKeys.GENERIC_STATUS_CODE: GenericCodes.InformationRetrieved,
        ApiResultKeys.VFENSE_STATUS_CODE: GenericCodes.InformationRetrieved,
        ApiResultKeys.DATA: data,
        ApiResultKeys.COUNT: len(data),
        ApiResultKeys.USERNAME: username,
        ApiResultKeys.URI: uri,
        ApiResultKeys.HTTP_METHOD: method
    }

    return results


@time_it
@results_message
def get_severity_bar_chart_stats_for_customer(
        customer_name, username=None,
        uri=None, method=None
    ):
    """Retrieve the number of available updates by severity.
    Args:
        customer_name (str): The name of the customer.

    Kwargs:
        username (str): The name of the user who called this function.
        uri (str): The uri that was used to call this function.
        method (str): The HTTP methos that was used to call this function.

    Basic Usage:
        >>> from vFense.plugins.patching._db_stats import get_severity_bar_chart_stats_for_customer
        >>> customer_name = 'default'
        >>> get_severity_bar_chart_stats_for_customer(customer_name)

    Returns:
        List of dictionaries.
        >>>
        {
            "count": 3,
            "uri": "/api/v1/dashboard/graphs/bar/severity",
            "rv_status_code": 1001,
            "http_method": "GET",
            "http_status": 200,
            "message": "admin - data was retrieved",
            "data": [
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
        }
    """

    data = fetch_severity_bar_chart_stats_for_customer(customer_name)

    results = {
        ApiResultKeys.GENERIC_STATUS_CODE: GenericCodes.InformationRetrieved,
        ApiResultKeys.VFENSE_STATUS_CODE: GenericCodes.InformationRetrieved,
        ApiResultKeys.DATA: data,
        ApiResultKeys.COUNT: len(data),
        ApiResultKeys.USERNAME: username,
        ApiResultKeys.URI: uri,
        ApiResultKeys.HTTP_METHOD: method
    }

    return results


@time_it
@results_message
def get_severity_bar_chart_stats_for_agent(
        agent_id, username=None,
        uri=None, method=None
    ):
    """Retrieve the number of available updates by severity.
    Args:
        agent_id (str): The 36 character UUID of the agent.

    Kwargs:
        username (str): The name of the user who called this function.
        uri (str): The uri that was used to call this function.
        method (str): The HTTP methos that was used to call this function.

    Basic Usage:
        >>> from vFense.plugins.patching._db_stats import get_severity_bar_chart_stats_for_agent
        >>> agent_id = '114ef1ea-7fbc-4505-b702-1500f89e969c'
        >>> get_severity_bar_chart_stats_for_agent(agent_id)

    Returns:
        List of dictionaries.
        >>>
        {
            "count": 3,
            "uri": "/api/v1/agent/114ef1ea-7fbc-4505-b702-1500f89e969c/graphs/bar/severity",
            "rv_status_code": 1001,
            "http_method": "GET",
            "http_status": 200,
            "message": "admin - data was retrieved",
            "data": [
                {
                    "count": 3,
                    "severity": "Critical"
                },
                {
                    "count": 1,
                    "severity": "Optional"
                },
                {
                    "count": 18,
                    "severity": "Recommended"
                }
            ]
        }
    """
    data = fetch_severity_bar_chart_stats_for_agent(agent_id)

    results = {
        ApiResultKeys.GENERIC_STATUS_CODE: GenericCodes.InformationRetrieved,
        ApiResultKeys.VFENSE_STATUS_CODE: GenericCodes.InformationRetrieved,
        ApiResultKeys.DATA: data,
        ApiResultKeys.COUNT: len(data),
        ApiResultKeys.USERNAME: username,
        ApiResultKeys.URI: uri,
        ApiResultKeys.HTTP_METHOD: method
    }

    return results


@time_it
@results_message
def get_severity_bar_chart_stats_for_tag(
        tag_id, username=None,
        uri=None, method=None
    ):
    """Retrieve the number of available updates by severity.
    Args:
        tag_id (str): The 36 character UUID of the agent.

    Kwargs:
        username (str): The name of the user who called this function.
        uri (str): The uri that was used to call this function.
        method (str): The HTTP methos that was used to call this function.

    Basic Usage:
        >>> from vFense.plugins.patching._db_stats import get_severity_bar_chart_stats_for_tag
        >>> tag_id = '114ef1ea-7fbc-4505-b702-1500f89e969c'
        >>> get_severity_bar_chart_stats_for_tag(tag_id)

    Returns:
        List of dictionaries.
        >>>
        {
            "count": 3,
            "uri": "/api/v1/tag/14dc332d-6ae1-46ba-8290-2619413816f9/graphs/bar/severity",
            "rv_status_code": 1001,
            "http_method": "GET",
            "http_status": 200,
            "message": "admin - data was retrieved",
            "data": [
                {
                    "count": 3,
                    "severity": "Critical"
                },
                {
                    "count": 1,
                    "severity": "Optional"
                },
                {
                    "count": 18,
                    "severity": "Recommended"
                }
            ]
        }
    """

    data = fetch_severity_bar_chart_stats_for_tag(tag_id)

    results = {
        ApiResultKeys.GENERIC_STATUS_CODE: GenericCodes.InformationRetrieved,
        ApiResultKeys.VFENSE_STATUS_CODE: GenericCodes.InformationRetrieved,
        ApiResultKeys.DATA: data,
        ApiResultKeys.COUNT: len(data),
        ApiResultKeys.USERNAME: username,
        ApiResultKeys.URI: uri,
        ApiResultKeys.HTTP_METHOD: method
    }

    return results


@time_it
@results_message
def top_packages_needed(
        customer_name, count=5,
        username=None, uri=None, method=None
    ):
    """Retrieve the top number of updates needed across
        all agents.
    Args:
        customer_name (str): The name of the customer.

    Kwargs:
        count (int, optional): Limit how many results show.
            default = 3
        username (str): The name of the user who called this function.
        uri (str): The uri that was used to call this function.
        method (str): The HTTP methos that was used to call this function.

    Basic Usage:
        >>> from vFense.plugins.patching._db_stats import top_packages_needed
        >>> customer_name = 'default'
        >>> count = 3
        >>> top_packages_needed(customer_name, count)

    Returns:
        List of dictionaries.
        >>>
        {
                "count": 3,
                "uri":  "/api/v1/dashboard/widgets/top_needed",
                "rv_status_code": 1001,
                "http_method": null,
                "http_status": 200,
                "message": "admin - data was retrieved",
                "data": [
                {
                    "count": 1,
                    "rv_severity": "Recommended",
                    "release_date": 1400644800,
                    "app_id": "1a3c80714af0eeb7f739e8f42f80d41fe33ffce1d012fff7648b6e5658594e90",
                    "name": "rethinkdb"
                },
                {
                    "count": 1,
                    "rv_severity": "Recommended",
                    "release_date": 1400644800,
                    "app_id": "e49d2d84cb5c1e63df9b984646f38e6127242aeba258e29eeefaf180a9be98e7",
                    "name": "python3-lxml"
                },
                {
                    "count": 1,
                    "rv_severity": "Recommended",
                    "release_date": 1400644800,
                    "app_id": "8683a443a58aefcd5cef3025e6307569c6b722eccb64c9573750a4d11c0ffbe8",
                    "name": "python-lxml"
                }
            ]
        }
    """

    data = fetch_top_apps_needed_for_customer(customer_name, count)

    results = {
        ApiResultKeys.GENERIC_STATUS_CODE: GenericCodes.InformationRetrieved,
        ApiResultKeys.VFENSE_STATUS_CODE: GenericCodes.InformationRetrieved,
        ApiResultKeys.DATA: data,
        ApiResultKeys.COUNT: len(data),
        ApiResultKeys.USERNAME: username,
        ApiResultKeys.URI: uri,
        ApiResultKeys.HTTP_METHOD: method
    }

    return results


@time_it
@results_message
def recently_released_packages(
        customer_name, count=5,
        username=None, uri=None, method=None
    ):
    """Retrieve the most recently released updates
    Args:
        customer_name (str): The name of the customer.

    Kwargs:
        count (int, optional): Limit how many results show.
            default = 3
        username (str): The name of the user who called this function.
        uri (str): The uri that was used to call this function.
        method (str): The HTTP methos that was used to call this function.

    Basic Usage:
        >>> from vFense.plugins.patching._db_stats import recently_released_packages
        >>> customer_name = 'default'
        >>> count = 3
        >>> recently_released_packages(customer_name, count)

    Returns:
        List of dictionaries.
        >>>
        {
                "count": 3,
                "uri":  "/api/v1/dashboard/widgets/recently_released",
                "rv_status_code": 1001,
                "http_method": null,
                "http_status": 200,
                "message": "admin - data was retrieved",
                "data": [
                {
                    "count": 1,
                    "rv_severity": "Recommended",
                    "release_date": 1400644800,
                    "app_id": "1a3c80714af0eeb7f739e8f42f80d41fe33ffce1d012fff7648b6e5658594e90",
                    "name": "rethinkdb"
                },
                {
                    "count": 1,
                    "rv_severity": "Recommended",
                    "release_date": 1400644800,
                    "app_id": "e49d2d84cb5c1e63df9b984646f38e6127242aeba258e29eeefaf180a9be98e7",
                    "name": "python3-lxml"
                },
                {
                    "count": 1,
                    "rv_severity": "Recommended",
                    "release_date": 1400644800,
                    "app_id": "8683a443a58aefcd5cef3025e6307569c6b722eccb64c9573750a4d11c0ffbe8",
                    "name": "python-lxml"
                }
            ]
        }
    """
    data = fetch_recently_released_apps(customer_name, count)

    results = {
        ApiResultKeys.GENERIC_STATUS_CODE: GenericCodes.InformationRetrieved,
        ApiResultKeys.VFENSE_STATUS_CODE: GenericCodes.InformationRetrieved,
        ApiResultKeys.DATA: data,
        ApiResultKeys.COUNT: len(data),
        ApiResultKeys.USERNAME: username,
        ApiResultKeys.URI: uri,
        ApiResultKeys.HTTP_METHOD: method
    }

    return results


@time_it
@results_message
def get_os_apps_history(
        customer_name, status, start_date=None, end_date=None,
        username=None, uri=None, method=None
    ):
    """Retrieve all applications from within a time frame
        for a customer.
    Args:
        customer_name (str): The name of the customer.
        status (str): The status of the applictions you want to see.
            example... installed or available or pending

    Kwargs:
        start_date (epoch_time): The date you want the search to begin.
            default is 365 days from now, example..
            start_date = 1369315938.0
        end_date (epoch_time): The date you want the search to end.
            default is today, example
            end_date = 1400852008.0
        username (str): The name of the user who called this function.
        uri (str): The uri that was used to call this function.
        method (str): The HTTP methos that was used to call this function.

    Basic Usage:
        >>> from vFense.plugins.patching._db_stats import get_os_apps_history
        >>> customer_name = 'default'
        >>> get_os_apps_history(customer_name)

    Returns:
        >>>
        {
            "count": 1,
            "uri": "/api/v1/dashboard/graphs/column/range/apps/os",
            "rv_status_code": 1001,
            "http_method": "GET",
            "http_status": 200,
            "message": "admin - data was retrieved",
            "data": [
                {
                    "timestamp": 1398398400,
                    "details": [
                        {
                            "reduction": {
                                "count": 1,
                                "apps": [
                                    {
                                        "version": "1:0.9.11+14.04.20140423-0ubuntu1",
                                        "app_id": "14ccb5aec245468786081a28de59e840b961a14e9113c41e57db977846b78ded",
                                        "name": "libcompizconfig0"
                                    }
                                ]
                            },
                            "group": "Optional"
                        },
                    ],
                    "total_count": 1
                },
            ]
        }
    """
    if not start_date and not end_date:
        start_date = (
            mktime((datetime.now() - timedelta(days=1*365)).timetuple())
        )
        end_date = mktime(datetime.now().timetuple())

    elif start_date and not end_date:
        end_date = mktime(datetime.now().timetuple())

    elif not start_date and end_date:
        start_date = 0.0

    data = fetch_os_apps_history(customer_name, status, start_date, end_date)

    results = {
        ApiResultKeys.GENERIC_STATUS_CODE: GenericCodes.InformationRetrieved,
        ApiResultKeys.VFENSE_STATUS_CODE: GenericCodes.InformationRetrieved,
        ApiResultKeys.DATA: data,
        ApiResultKeys.COUNT: len(data),
        ApiResultKeys.USERNAME: username,
        ApiResultKeys.URI: uri,
        ApiResultKeys.HTTP_METHOD: method
    }

    return results

@time_it
@results_message
def get_os_apps_history_for_agent(
        agent_id, status, start_date=None, end_date=None,
        username=None, uri=None, method=None
    ):
    """Retrieve all applications from within a time frame
        for an agent.
    Args:
        agent_id (str): 36 character UUID of the agent.
        status (str): The status of the applictions you want to see.
            example... installed or available or pending

    Kwargs:
        start_date (epoch_time): The date you want the search to begin.
            default is 365 days from now, example..
            start_date = 1369315938.0
        end_date (epoch_time): The date you want the search to end.
            default is today, example
            end_date = 1400852008.0
        username (str): The name of the user who called this function.
        uri (str): The uri that was used to call this function.
        method (str): The HTTP methos that was used to call this function.

    Basic Usage:
        >>> from vFense.plugins.patching._db_stats import get_os_apps_history_for_agent
        >>> agent_id = '114ef1ea-7fbc-4505-b702-1500f89e969c'
        >>> get_os_apps_history_for_agent(agent_id)

    Returns:
        >>>
        {
            "count": 1,
            "uri": "/api/v1/agent/114ef1ea-7fbc-4505-b702-1500f89e969c/graphs/column/range/apps/os",
            "rv_status_code": 1001,
            "http_method": "GET",
            "http_status": 200,
            "message": "admin - data was retrieved",
            "data": [
                {
                    "timestamp": 1398398400,
                    "details": [
                        {
                            "reduction": {
                                "count": 1,
                                "apps": [
                                    {
                                        "version": "1:0.9.11+14.04.20140423-0ubuntu1",
                                        "app_id": "14ccb5aec245468786081a28de59e840b961a14e9113c41e57db977846b78ded",
                                        "name": "libcompizconfig0"
                                    }
                                ]
                            },
                            "group": "Optional"
                        },
                    ],
                    "total_count": 1
                },
            ]
        }
    """

    if not start_date and not end_date:
        start_date = (
            mktime((datetime.now() - timedelta(days=1*365)).timetuple())
        )
        end_date = mktime(datetime.now().timetuple())

    elif start_date and not end_date:
        end_date = mktime(datetime.now().timetuple())

    elif not start_date and end_date:
        start_date = 0.0

    data = (
        fetch_os_apps_history_for_agent(
            agent_id, status, start_date, end_date
        )
    )

    results = {
        ApiResultKeys.GENERIC_STATUS_CODE: GenericCodes.InformationRetrieved,
        ApiResultKeys.VFENSE_STATUS_CODE: GenericCodes.InformationRetrieved,
        ApiResultKeys.DATA: data,
        ApiResultKeys.COUNT: len(data),
        ApiResultKeys.USERNAME: username,
        ApiResultKeys.URI: uri,
        ApiResultKeys.HTTP_METHOD: method
    }

    return results

@time_it
@results_message
def get_os_apps_history_for_tag(
        tag_id, status, start_date=None,
        end_date=None, username=None, uri=None,
        method=None
    ):
    """Retrieve all applications from within a time frame
        for a customer.
    Args:
        tag_id (str): The 36 character UUID of the tag.
        status (str): The status of the applictions you want to see.
            example... installed or available or pending

    Kwargs:
        start_date (epoch_time): The date you want the search to begin.
            default is 365 days from now, example..
            start_date = 1369315938.0
        end_date (epoch_time): The date you want the search to end.
            default is today, example
            end_date = 1400852008.0
        username (str): The name of the user who called this function.
        uri (str): The uri that was used to call this function.
        method (str): The HTTP methos that was used to call this function.

    Basic Usage:
        >>> from vFense.plugins.patching._db_stats import get_os_apps_history_for_tag
        >>> tag_id = '14dc332d-6ae1-46ba-8290-2619413816f9'
        >>> get_os_apps_history_for_tag(tag_id)

    Returns:
        >>>
        {
            "count": 1,
            "uri": "/api/v1/tag/14dc332d-6ae1-46ba-8290-2619413816f9/graphs/column/range/apps/os",
            "rv_status_code": 1001,
            "http_method": "GET",
            "http_status": 200,
            "message": "admin - data was retrieved",
            "data": [
                {
                    "timestamp": 1398398400,
                    "details": [
                        {
                            "reduction": {
                                "count": 1,
                                "apps": [
                                    {
                                        "version": "1:0.9.11+14.04.20140423-0ubuntu1",
                                        "app_id": "14ccb5aec245468786081a28de59e840b961a14e9113c41e57db977846b78ded",
                                        "name": "libcompizconfig0"
                                    }
                                ]
                            },
                            "group": "Optional"
                        },
                    ],
                    "total_count": 1
                },
            ]
        }
    """


    if not start_date and not end_date:
        start_date = (
            mktime((datetime.now() - timedelta(days=1*365)).timetuple())
        )
        end_date = mktime(datetime.now().timetuple())

    elif start_date and not end_date:
        end_date = mktime(datetime.now().timetuple())

    elif not start_date and end_date:
        start_date = 0.0
    data = (
        fetch_os_apps_history_for_tag(
            tag_id, status, start_date, end_date
        )
    )

    results = {
        ApiResultKeys.GENERIC_STATUS_CODE: GenericCodes.InformationRetrieved,
        ApiResultKeys.VFENSE_STATUS_CODE: GenericCodes.InformationRetrieved,
        ApiResultKeys.DATA: data,
        ApiResultKeys.COUNT: len(data),
        ApiResultKeys.USERNAME: username,
        ApiResultKeys.URI: uri,
        ApiResultKeys.HTTP_METHOD: method
    }

    return results
