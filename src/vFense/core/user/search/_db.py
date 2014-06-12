#!/usr/bin/env python

import logging
import logging.config
from vFense import VFENSE_LOGGING_CONFIG
from vFense.db.client import db_create_close, r
from vFense.core._constants import SortValues, DefaultQueryValues

from vFense.core.user._db_model import (
    UserCollections, UserKeys, UserMappedKeys, UserIndexes
)

from vFense.core.group._db_model import (
    GroupCollections, GroupKeys, GroupIndexes
)

from vFense.core.view._db_model import (
    ViewCollections, ViewKeys, ViewIndexes, ViewMappedKeys
)

from vFense.core.permissions._constants import (
    Permissions
)


logging.config.fileConfig(VFENSE_LOGGING_CONFIG)
logger = logging.getLogger('rvapi')

class FetchUsers(object):
    """Agent operation database queries"""
    def __init__(
            self, view_name=None,
            count=DefaultQueryValues.COUNT,
            offset=DefaultQueryValues.OFFSET,
            sort=SortValues.ASC,
            sort_key=UserKeys.UserName,
            is_global=False
        ):
        """
        Kwargs:
            view_name (str): Name of the current view.
                default = None
            count (int): Maximum number of results to return.
                default = 30
            offset (int): Retrieve operations after this number. Pagination.
                default = 0
            sort (str): Sort either by asc or desc.
                default = desc
            sort_key (str): Sort by a valid field.
                examples... operation, status, created_time, updated_time,
                completed_time, and created_by.
                default = created_time

        Basic Usage:
            >>> from vFense.core.operations.search._db_agent_search import FetchAgentOperations
            >>> view_name = 'default'
            >>> operation = FetchAgentOperations(view_name)
        """

        self.view_name = view_name
        self.count = count
        self.offset = offset
        self.sort_key = sort_key
        self.is_global = is_global

        if sort == SortValues.ASC:
            self.sort = r.asc
        else:
            self.sort = r.desc


    @db_create_close
    def fetch_all(self, conn=None):
        """Retrieve a user and all of its properties
            This query is beautiful :)

        Basic Usage:
            >>> from vFense.user.search._db import FetchUsers
            >>> view_name = 'global'
            >>> users = FetchUsers(view_name)
            >>> users.fetch_all()

        Returns:
            List of users and their properties.
        """
        count = 0
        data = []
        base_filter = self._set_base_query()
        map_hash = self._set_map_hash()

        try:
            count = (
                base_filter
                .count()
                .run(conn)
            )

            data = list(
                base_filter
                .order_by(self.sort(self.sort_key))
                .skip(self.offset)
                .limit(self.count)
                .map(map_hash)
                .run(conn)
            )

        except Exception as e:
            logger.exception(e)

        return(count, data)


    @db_create_close
    def fetch_by_name(self, username, conn=None):
        """Retrieve a user and all of its properties
            This query is beautiful :)

        Basic Usage:
            >>> from vFense.user.search._db import FetchUsers
            >>> view_name = 'global'
            >>> users = FetchUsers(view_name)
            >>> users.fetch_by_name("glob")

        Returns:
            List of users and their properties.
        """
        count = 0
        data = []
        base_filter = self._set_base_query()
        map_hash = self._set_map_hash()

        try:
            count = (
                base_filter
                .filter(
                    lambda x:
                    x[UserKeys.UserName].match("(?i)^"+name)
                )
                .count()
                .run(conn)
            )

            data = list(
                base_filter
                .filter(
                    lambda x:
                    x[UserKeys.UserName].match("(?i)^"+name)
                )
                .order_by(self.sort(self.sort_key))
                .skip(self.offset)
                .limit(self.count)
                .map(map_hash)
                .run(conn)
            )

        except Exception as e:
            logger.exception(e)

        return(count, data)

    def _set_base_query(self):
        if self.view_name:
            if self.is_global:
                base = (
                    r
                    .table(UserCollections.Users)
                    .get_all(self.view_name, index=UserIndexes.Views)
                )
            else:
                base = (
                    r
                    .table(UserCollections.Users)
                    .get_all(self.view_name, index=UserIndexes.Views)
                    .filter({UserKeys.Global: False})
                )
        else:
            if self.is_global:
                base = (
                    r
                    .table(UserCollections.Users)
                )
            else:
                base = (
                    r
                    .table(UserCollections.Users)
                    .filter({UserKeys.Global: False})
                )

        return base

    def _set_map_hash(self):
        map_hash = (
            lambda x:
            {
                UserKeys.DefaultView: x[UserKeys.DefaultView],
                UserKeys.CurrentView: x[UserKeys.CurrentView],
                UserKeys.Email: x[UserKeys.Email],
                UserKeys.FullName: x[UserKeys.FullName],
                UserKeys.UserName: x[UserKeys.UserName],
                UserKeys.Enabled: x[UserKeys.Enabled],
                UserKeys.Global: x[UserKeys.Global],
                UserMappedKeys.Groups: (
                    r
                    .table(GroupCollections.Groups)
                    .get_all(x[UserKeys.UserName], index=GroupIndexes.Users)
                    .coerce_to('array')
                    .pluck(
                        GroupKeys.GroupId,
                        GroupKeys.GroupName,
                        GroupKeys.Permissions,
                        GroupKeys.Views
                    )
                ),
                UserKeys.Views: (
                    r
                    .expr(x[UserKeys.Views])
                    .map(
                        lambda y:
                        {
                            Permissions.ADMINISTRATOR: (
                                r
                                .branch(
                                    r
                                    .table(GroupCollections.Groups)
                                    .get_all(
                                        x[UserKeys.UserName],
                                        index=GroupIndexes.Users
                                    )
                                    .coerce_to('array')
                                    .filter(
                                        lambda z:
                                        z[GroupKeys.Views]
                                        .contains(y)
                                    )
                                    .filter(
                                        lambda z:
                                        z[GroupKeys.Permissions]
                                        .contains(Permissions.ADMINISTRATOR)
                                    )
                                    .is_empty(),
                                False,
                                True
                                )
                            ),
                            ViewMappedKeys.ViewName: y
                        }
                    )
                )
            }
        )

        return map_hash
