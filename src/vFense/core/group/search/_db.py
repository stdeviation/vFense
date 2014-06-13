#!/usr/bin/env python

import logging
import logging.config
from vFense import VFENSE_LOGGING_CONFIG
from vFense.db.client import db_create_close, r
from vFense.core._constants import SortValues, DefaultQueryValues

from vFense.core.group._db_model import (
    GroupCollections, GroupKeys, GroupIndexes, GroupMappedKeys
)


logging.config.fileConfig(VFENSE_LOGGING_CONFIG)
logger = logging.getLogger('rvapi')

class FetchGroups(object):
    """Group database queries"""
    def __init__(
            self, view_name=None,
            count=DefaultQueryValues.COUNT,
            offset=DefaultQueryValues.OFFSET,
            sort=SortValues.ASC,
            sort_key=GroupKeys.GroupName,
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
                default = group_name

        Basic Usage:
            >>> from vFense.core.group.search._db import FetchGroups
            >>> view_name = 'default'
            >>> operation = FetchGroups(view_name)
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
    def by_id(self, group_id, conn=None):
        """Retrieve all users and all of its properties

        Basic Usage:
            >>> from vFense.group.search._db import FetchGroups
            >>> view_name = 'global'
            >>> groups = FetchGroups(view_name)
            >>> groups.by_id('96f02bcf-2ada-465c-b175-0e5163b36e1c')

        Returns:
            Tuple
            (count, group_data)
        >>>
        [
            1,
            [
                {
                    "users": [
                        {
                            "user_name": "global_admin"
                        }
                    ],
                    "views": [
                        {
                            "view_name": "global"
                        }
                    ],
                    "global": true,
                    "email": null,
                    "group_name": "Global Administrator",
                    "id": "d3120f76-a7f4-4708-ab84-da219c4503aa",
                    "permissions": [
                        "administrator"
                    ]
                }
            ]
        ]
        """
        count = 0
        data = []
        base_filter = (
            r
            .table(GroupCollections.Groups)
        )
        map_hash = self._set_map_hash()

        try:
            count = (
                base_filter
                .get_all(group_id)
                .count()
                .run(conn)
            )

            data = list(
                base_filter
                .get_all(group_id)
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
    def all(self, conn=None):
        """Retrieve all users and all of its properties

        Basic Usage:
            >>> from vFense.group.search._db import FetchGroups
            >>> view_name = 'global'
            >>> groups = FetchGroups(view_name)
            >>> groups.fetch_all()

        Returns:
            Tuple
            (count, group_data)
        >>>
        [
            2,
            [
                {
                    "users": [
                        {
                            "user_name": "global_admin"
                        }
                    ],
                    "views": [
                        {
                            "view_name": "global"
                        }
                    ],
                    "global": true,
                    "email": null,
                    "group_name": "Global Administrator",
                    "id": "d3120f76-a7f4-4708-ab84-da219c4503aa",
                    "permissions": [
                        "administrator"
                    ]
                }
            ]
        ]
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
    def by_name(self, name, conn=None):
        """Retrieve groups by regex and all of its properties

        Basic Usage:
            >>> from vFense.group.search._db import FetchGroups
            >>> view_name = 'global'
            >>> groups = FetchGroups(view_name)
            >>> groups.fetch_by_name("glob")

        Returns:
            Tuple
            (count, group_data)
        >>>
        [
            2,
            [
                {
                    "users": [
                        {
                            "user_name": "global_admin"
                        }
                    ],
                    "views": [
                        {
                            "view_name": "global"
                        }
                    ],
                    "global": true,
                    "email": null,
                    "group_name": "Global Administrator",
                    "id": "d3120f76-a7f4-4708-ab84-da219c4503aa",
                    "permissions": [
                        "administrator"
                    ]
                }
            ]
        ]
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
                    x[GroupKeys.GroupName].match("(?i)^"+name)
                )
                .count()
                .run(conn)
            )

            data = list(
                base_filter
                .filter(
                    lambda x:
                    x[GroupKeys.GroupName].match("(?i)^"+name)
                )
                .coerce_to('array')
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
                    .table(GroupCollections.Groups)
                    .get_all(self.view_name, index=GroupIndexes.Views)
                )
            else:
                base = (
                    r
                    .table(GroupCollections.Groups)
                    .get_all(self.view_name, index=GroupIndexes.Views)
                    .filter({GroupKeys.Global: False})
                )
        else:
            if self.is_global:
                base = (
                    r
                    .table(GroupCollections.Groups)
                )
            else:
                base = (
                    r
                    .table(GroupCollections.Groups)
                    .filter({GroupKeys.Global: False})
                )

        return base

    def _set_map_hash(self):
        map_hash = (
            lambda x:
            {
                GroupKeys.GroupId: x[GroupKeys.GroupId],
                GroupKeys.GroupName: x[GroupKeys.GroupName],
                GroupKeys.Email: x[GroupKeys.Email],
                GroupKeys.Global: x[GroupKeys.Global],
                GroupKeys.Permissions: x[GroupKeys.Permissions],
                GroupKeys.Users: (
                    r
                    .expr(x[GroupKeys.Users])
                    .map(
                        lambda y:
                        {
                            GroupMappedKeys.UserName: y
                        }
                    )
                ),
                GroupKeys.Views: (
                    r
                    .expr(x[GroupKeys.Views])
                    .map(
                        lambda y:
                        {
                            GroupMappedKeys.ViewName: y
                        }
                    )
                )
            }
        )

        return map_hash
