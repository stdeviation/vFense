#!/usr/bin/env python
import logging

from vFense._constants import VFENSE_LOGGING_CONFIG
from vFense.core.user._db_model import (
    UserCollections, UserKeys
)
from vFense.core.group._db_model import (
    GroupCollections, GroupIndexes, GroupKeys
)
from vFense.core.view._db_model import (
    ViewCollections, ViewKeys
)
from vFense.core.agent._db_model import (
    AgentCollections, AgentKeys, AgentIndexes
)
from vFense.core.tag._db_model import (
    TagCollections, TagKeys, TagsIndexes
)
from vFense.db.client import db_create_close, r
from vFense.plugins.notifications._db_model import (
    NotificationCollections, NotificationIndexes
)
from vFense.core.decorators import time_it, catch_it

from vFense.core._db import (
    insert_data_in_table, delete_data_in_table,
    update_data_in_table
)



logging.config.fileConfig(VFENSE_LOGGING_CONFIG)
logger = logging.getLogger('rvapi')


@time_it
@catch_it({})
@db_create_close
def fetch_notification_rule(rule_id, conn=None):
    data = (
        r
        .table(NotificationCollections.Notifications)
        .get(rule_id)
        .run(conn)
    )

    return data

@time_it
@catch_it(False)
@db_create_close
def notification_rule_exists(rule_id, conn=None):
    is_empty = (
        r
        .table(NotificationCollections.Notifications)
        .get_all(rule_id)
        .run(conn)
    )
    if not is_empty:
        exist = True
    else:
        exist = False

    return exist

@time_it
@catch_it([])
@db_create_close
def fetch_all_notifications(view_name, conn=None):
    data = list(
        r
        .table(NotificationCollections.Notifications)
        .get_all(view_name, index=NotificationIndexes.ViewName)
        .run(conn)
    )

    return data

@time_it
@catch_it({})
@db_create_close
def fetch_valid_fields(view_name, conn=None):
    agents = list(
        r
        .table(AgentCollections.Agents)
        .get_all(view_name, index=AgentIndexes.ViewName)
        .pluck(AgentKeys.AgentId, AgentKeys.ComputerName)
        .run(conn)
    )
    tags = list(
        r
        .table(TagCollections.Tags)
        .get_all(view_name, index=TagsIndexes.ViewName)
        .pluck(TagKeys.TagId, TagKeys.TagName)
        .run(conn)
    )
    users = list(
        r
        .table(UserCollections.Users)
        .pluck(UserKeys.UserName)
        .run(conn)
    )
    groups = list(
        r
        .table(GroupCollections.Groups)
        .get_all(view_name, index=GroupIndexes.Views)
        .pluck(GroupKeys.GroupName)
        .run(conn)
    )
    views = list(
        r
        .table(ViewCollections.Views)
        .pluck(ViewKeys.ViewName)
        .run(conn)
    )
    data = {
        'tags': tags,
        'agents': agents,
        'users': users,
        'groups': groups,
        'views': views,
    }

    return data

@time_it
def delete_rule(rule_id):
    """ Delete a notification rule and its properties in the database
        This function should not be called directly.
    Args:
        rule_id (str): the notification rule UUID

    Basic Usage:
        >>> from vFense.plugins.notifications._db import delete_rule
        >>> rule_id = '38226b0e-a482-4cb8-b135-0a0057b913f2'
        >>> delete_rule(rule_id)

    Return:
        Tuple (status_code, count, error, generated ids)
        >>> (2001, 1, None, [])
    """
    data = (
        delete_data_in_table(
            rule_id, NotificationCollections.Notifications
        )
    )

    return data

@time_it
def insert_rule(rule_data):
    """ Insert a notification rule and its properties into the database
        This function should not be called directly.
    Args:
        rule_data (list|dict): Dictionary of the data you are inserting.

    Basic Usage:
        >>> from vFense.plugins.notifications._db import insert_rule
        >>> rule_data = {'rule_name': 'vFense', 'rule_description': 'no'}
        >>> insert_rule(rule_data)

    Return:
        Tuple (status_code, count, error, generated ids)
        >>> (2001, 1, None, [])
    """
    data = (
        insert_data_in_table(
            rule_data, NotificationCollections.Notifications
        )
    )

    return data

@time_it
def update_rule(rule_id, rule_data):
    """ Update a notification rule and its properties into the database
        This function should not be called directly.
    Args:
        rule_id (str): the notification rule UUID
        rule_data (list|dict): Dictionary of the data you are updating.

    Basic Usage:
        >>> from vFense.plugins.notifications._db import update_rule
        >>> rule_id = '38226b0e-a482-4cb8-b135-0a0057b913f2'
        >>> rule_data = {'rule_name': 'vFense', 'rule_description': 'no'}
        >>> update_rule(rule_id, rule_data)

    Return:
        Tuple (status_code, count, error, generated ids)
        >>> (2001, 1, None, [])
    """
    data = (
        update_data_in_table(
            rule_id, rule_data, NotificationCollections.Notifications
        )
    )

    return data
