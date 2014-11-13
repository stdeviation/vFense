from vFense.db.client import db_create_close, r
from vFense.core.decorators import catch_it, time_it
from vFense.core.group._db_model import (
    GroupCollections, GroupKeys, GroupIndexes, GroupMappedKeys
)
from vFense.search._db_base import FetchBase

class FetchGroups(FetchBase):
    """Group database queries"""
    def __init__(
            self, sort_key=GroupKeys.GroupName, is_global=False, **kwargs
        ):
        super(FetchGroups, self).__init__(**kwargs)
        self.is_global = is_global

    @time_it
    @catch_it((0, []))
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

        return(count, data)

    @time_it
    @catch_it((0, []))
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

        return(count, data)

    @time_it
    @catch_it((0, []))
    @db_create_close
    def by_name(self, name, conn=None):
        """Retrieve groups by regex and all of its properties

        Basic Usage:
            >>> from vFense.group.search._db import FetchGroups
            >>> view_name = 'global'
            >>> groups = FetchGroups(view_name)
            >>> groups.by_name("glob")

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
        count = (
            base_filter
            .filter({GroupKeys.GroupName: name})
            .count()
            .run(conn)
        )

        data = list(
            base_filter
            .filter({GroupKeys.GroupName: name})
            .coerce_to('array')
            .order_by(self.sort(self.sort_key))
            .skip(self.offset)
            .limit(self.count)
            .map(map_hash)
            .run(conn)
        )

        return(count, data)

    @time_it
    @catch_it((0, []))
    @db_create_close
    def by_regex(self, name, conn=None):
        """Retrieve groups by regex and all of its properties

        Basic Usage:
            >>> from vFense.group.search._db import FetchGroups
            >>> view_name = 'global'
            >>> groups = FetchGroups(view_name)
            >>> groups.by_regex("glob")

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
                    .filter({GroupKeys.IsGlobal: False})
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
                    .filter({GroupKeys.IsGlobal: False})
                )

        return base

    def _set_map_hash(self):
        map_hash = (
            lambda x:
            {
                GroupKeys.GroupId: x[GroupKeys.GroupId],
                GroupKeys.GroupName: x[GroupKeys.GroupName],
                GroupKeys.Email: x[GroupKeys.Email],
                GroupKeys.IsGlobal: x[GroupKeys.IsGlobal],
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
