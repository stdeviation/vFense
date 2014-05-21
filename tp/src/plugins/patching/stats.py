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
    Returns:
        >>> {
            "count": 0, 
            "uri": null, 
            "rv_status_code": 1001, 
            "http_method": null, 
            "http_status": 200, 
            "message": "None - data was retrieved", 
            "data": [
                {
                    "count": 253, 
                    "os": "LinuxMint 16"
                }
            ]
        }
    """
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

    Returns:
        >>> {
            "count": 0, 
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

    data = fetch_severity_bar_chart_stats_for_customer(customer_name)

    results = {
        ApiResultKeys.GENERIC_STATUS_CODE: GenericCodes.InformationRetrieved,
        ApiResultKeys.VFENSE_STATUS_CODE: GenericCodes.InformationRetrieved,
        ApiResultKeys.DATA: data,
        ApiResultKeys.USERNAME: username,
        ApiResultKeys.URI: uri,
        ApiResultKeys.HTTP_METHOD: method
    }

    return(results)


@time_it
@results_message
def get_severity_bar_chart_stats_for_agent(
        agent_id, username=None,
        uri=None, method=None
    ):
    data = fetch_severity_bar_chart_stats_for_agent(agent_id)

    results = {
        ApiResultKeys.GENERIC_STATUS_CODE: GenericCodes.InformationRetrieved,
        ApiResultKeys.VFENSE_STATUS_CODE: GenericCodes.InformationRetrieved,
        ApiResultKeys.DATA: data,
        ApiResultKeys.USERNAME: username,
        ApiResultKeys.URI: uri,
        ApiResultKeys.HTTP_METHOD: method
    }

    return(results)


@time_it
@results_message
def get_severity_bar_chart_stats_for_tag(
        tag_id, username=None,
        uri=None, method=None
    ):

    data = fetch_severity_bar_chart_stats_for_tag(tag_id)

    results = {
        ApiResultKeys.GENERIC_STATUS_CODE: GenericCodes.InformationRetrieved,
        ApiResultKeys.VFENSE_STATUS_CODE: GenericCodes.InformationRetrieved,
        ApiResultKeys.DATA: data,
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

    data = fetch_top_apps_needed_for_customer(customer_name, count)

    results = {
        ApiResultKeys.GENERIC_STATUS_CODE: GenericCodes.InformationRetrieved,
        ApiResultKeys.VFENSE_STATUS_CODE: GenericCodes.InformationRetrieved,
        ApiResultKeys.DATA: data,
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

    data = fetch_recently_released_apps(customer_name, count)

    results = {
        ApiResultKeys.GENERIC_STATUS_CODE: GenericCodes.InformationRetrieved,
        ApiResultKeys.VFENSE_STATUS_CODE: GenericCodes.InformationRetrieved,
        ApiResultKeys.DATA: data,
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
        ApiResultKeys.USERNAME: username,
        ApiResultKeys.URI: uri,
        ApiResultKeys.HTTP_METHOD: method
    }

    return results
