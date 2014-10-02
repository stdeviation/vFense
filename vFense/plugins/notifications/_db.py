#!/usr/bin/env python
import logging

from vFense import VFENSE_LOGGING_CONFIG
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
    AgentsCollection, AgentKeys, AgentIndexes
)
from vFense.core.tag._db_model import (
    TagsCollection, TagKeys, TagsIndexes
)
from vFense.db.client import db_create_close, r
from vFense.plugins.notifications._db_model import (
    NotificationCollections, NotificationIndexes
)
from vFense.core.decorators import return_status_tuple, time_it


logging.config.fileConfig(VFENSE_LOGGING_CONFIG)
logger = logging.getLogger('rvapi')


@db_create_close
def notification_rule_exists(rule_id, conn=None):
    rule_exists = None
    try:
        rule_exists = (
            r
            .table(NotificationCollections.Notifications)
            .get(rule_id)
            .run(conn)
        )

    except Exception as e:
        logger.exception(e)

    return rule_exists


@db_create_close
def fetch_all_notifications(view_name, conn=None):
    data = []
    try:
        data = list(
            r
            .table(NotificationCollections.Notifications)
            .get_all(view_name, index=NotificationIndexes.ViewName)
            .run(conn)
        )

    except Exception as e:
        logger.exception(e)

    return data

@db_create_close
def fetch_valid_fields(view_name, conn=None):
    data = {}
    try:
        agents = list(
            r
            .table(AgentsCollection)
            .get_all(view_name, index=AgentIndexes.ViewName)
            .pluck(AgentKeys.AgentId, AgentKeys.ComputerName)
            .run(conn)
        )
        tags = list(
            r
            .table(TagsCollection)
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

    except Exception as e:
        logger.exception(e)

    return data


@db_create_close
@return_status_tuple
def delete_notification_rule(self, rule_id, conn=None):
    data = {}
    try:
        data = (
            r
            .table(NotificationCollections.Notifications)
            .get(rule_id)
            .delete()
            .run(conn)
        )

    except Exception as e:
        logger.exception(e)

    return data
