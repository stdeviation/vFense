#!/usr/bin/env python
from vFense.db.client import db_create_close, r
from vFense.core.decorators import catch_it, time_it

from vFense.core.group._db_model import (
    GroupCollections, GroupKeys, GroupIndexes
)

from vFense.core.view._db_model import (
    ViewCollections, ViewKeys, ViewMappedKeys
)
from vFense.search._db_base import FetchBase

class FetchViews(FetchBase):
    """View database queries"""
    def __init__(
            self, parent_view=None, sort_key=GroupKeys.GroupName,
            is_global=False, **kwargs
        ):
        """
        Kwargs:
            parent_view (str): Name of the parent view.
                default = None
            is_global (bool): Search for only global views or local.
                default=False
            sort_key (str): Sort by a valid field.
                examples... view_name,
                default = view_name

        Basic Usage:
            >>> from vFense.core.view.search._db import FetchViews
            >>> view_name = 'default'
            >>> operation = FetchViews(view_name)
        """
        super(FetchViews, self).__init__(**kwargs)
        self.parent_view = parent_view
        self.sort_key = sort_key
        self.is_global = is_global

    @time_it
    @catch_it((0, []))
    @db_create_close
    def all(self, conn=None):
        """Retrieve all views and all of its properties

        Basic Usage:
            >>> from vFense.view.search._db import FetchViews
            >>> view_name = 'global'
            >>> views = FetchViews(view_name)
            >>> views.all()

        Returns:
            Tuple
            (count, view_data)
        >>>
        [
            1,
            [
                {
                    "cpu_throttle": "normal",
                    "agent_queue_ttl": 10,
                    "view_name": "global",
                    "server_queue_ttl": 10,
                    "package_download_url_base": "https://10.0.0.15/packages/",
                    "groups": [
                        {
                            "group_id": "5695a03a-6abe-4700-a125-276081b6bcd4"
                            "group_name": "Global Administrator"
                        },
                        {
                            "group_id": "c2d65279-1ae7-4d0c-9ed1-3f469e02d995",
                            "group_name": "Global Read Only"
                        }
                    ],
                    "net_throttle": 0,
                    "users": [
                        {
                            "user_name": "global_admin"
                        },
                        {
                            "user_name": "global_agent"
                        }
                    ]
                }
            ]
        ]
        """
        count = 0
        data = []
        base_filter = self._set_base_query()
        merge_hash = self._set_merge_hash()
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
            .merge(merge_hash)
            .run(conn)
        )

        return(count, data)

    @time_it
    @catch_it((0, []))
    @db_create_close
    def by_name(self, view_name, conn=None):
        """Retrieve view by view name and all of its properties

        Basic Usage:
            >>> from vFense.view.search._db import FetchViews
            >>> view_name = 'global'
            >>> views = FetchViews()
            >>> views.by_name(view_name)

        Returns:
            Tuple
            (count, group_data)
        >>>
        [
            1,
            [
                {
                    "cpu_throttle": "normal",
                    "agent_queue_ttl": 10,
                    "view_name": "global",
                    "server_queue_ttl": 10,
                    "package_download_url_base": "https://10.0.0.15/packages/",
                    "groups": [
                        {
                            "group_id": "5695a03a-6abe-4700-a125-276081b6bcd4"
                            "group_name": "Global Administrator"
                        },
                        {
                            "group_id": "c2d65279-1ae7-4d0c-9ed1-3f469e02d995",
                            "group_name": "Global Read Only"
                        }
                    ],
                    "net_throttle": 0,
                    "users": [
                        {
                            "user_name": "global_admin"
                        },
                        {
                            "user_name": "global_agent"
                        }
                    ]
                }
            ]
        ]
        """
        count = 0
        data = []
        base_filter = self._set_base_query()
        merge_hash = self._set_merge_hash()
        count = (
            base_filter
            .filter({ViewKeys.ViewName: view_name})
            .count()
            .run(conn)
        )

        data = list(
            base_filter
            .filter({ViewKeys.ViewName: view_name})
            .coerce_to('array')
            .order_by(self.sort(self.sort_key))
            .skip(self.offset)
            .limit(self.count)
            .merge(merge_hash)
            .run(conn)
        )

        return(count, data)

    @time_it
    @catch_it((0, []))
    @db_create_close
    def by_regex(self, name, conn=None):
        """Retrieve views by regex and all of its properties

        Basic Usage:
            >>> from vFense.view.search._db import FetchViews
            >>> view_name = 'global'
            >>> views = FetchViews(view_name)
            >>> views.by_regex("glob")

        Returns:
            Tuple
            (count, group_data)
        >>>
        [
            1,
            [
                {
                    "cpu_throttle": "normal",
                    "agent_queue_ttl": 10,
                    "view_name": "global",
                    "server_queue_ttl": 10,
                    "package_download_url_base": "https://10.0.0.15/packages/",
                    "groups": [
                        {
                            "group_id": "5695a03a-6abe-4700-a125-276081b6bcd4"
                            "group_name": "Global Administrator"
                        },
                        {
                            "group_id": "c2d65279-1ae7-4d0c-9ed1-3f469e02d995",
                            "group_name": "Global Read Only"
                        }
                    ],
                    "net_throttle": 0,
                    "users": [
                        {
                            "user_name": "global_admin"
                        },
                        {
                            "user_name": "global_agent"
                        }
                    ]
                }
            ]
        ]
        """
        count = 0
        data = []
        base_filter = self._set_base_query()
        merge_hash = self._set_merge_hash()

        count = (
            base_filter
            .filter(
                lambda x:
                x[ViewKeys.ViewName].match("(?i)^"+name)
            )
            .count()
            .run(conn)
        )

        data = list(
            base_filter
            .filter(
                lambda x:
                x[ViewKeys.ViewName].match("(?i)^"+name)
            )
            .coerce_to('array')
            .order_by(self.sort(self.sort_key))
            .skip(self.offset)
            .limit(self.count)
            .merge(merge_hash)
            .run(conn)
        )

        return(count, data)

    @time_it
    @catch_it((0, []))
    @db_create_close
    def for_user(self, name, conn=None):
        """Retrieve views for user and all of its properties

        Basic Usage:
            >>> from vFense.view.search._db import FetchViews
            >>> user = 'global_admin'
            >>> views = FetchViews()
            >>> views.for_user("glob")

        Returns:
            Tuple
            (count, group_data)
        >>>
        [
            1,
            [
                {
                    "cpu_throttle": "normal",
                    "agent_queue_ttl": 10,
                    "view_name": "global",
                    "server_queue_ttl": 10,
                    "package_download_url_base": "https://10.0.0.15/packages/",
                    "groups": [
                        {
                            "group_id": "5695a03a-6abe-4700-a125-276081b6bcd4"
                            "group_name": "Global Administrator"
                        },
                        {
                            "group_id": "c2d65279-1ae7-4d0c-9ed1-3f469e02d995",
                            "group_name": "Global Read Only"
                        }
                    ],
                    "net_throttle": 0,
                    "users": [
                        {
                            "user_name": "global_admin"
                        },
                        {
                            "user_name": "global_agent"
                        }
                    ]
                }
            ]
        ]
        """
        count = 0
        data = []
        base_filter = self._set_base_query()
        merge_hash = self._set_merge_hash()
        count = (
            base_filter
            .filter(
                lambda x:
                x[ViewKeys.Users].contains(name)
            )
            .count()
            .run(conn)
        )

        data = list(
            base_filter
            .filter(
                lambda x:
                x[ViewKeys.Users].contains(name)
            )
            .coerce_to('array')
            .order_by(self.sort(self.sort_key))
            .skip(self.offset)
            .limit(self.count)
            .merge(merge_hash)
            .run(conn)
        )

        return(count, data)

    def _set_base_query(self):
        if self.parent_view:
            base = (
                r
                .table(ViewCollections.Views)
                .filter(
                    lambda x:
                    (x[ViewKeys.Ancestors].contains(self.parent_view))
                    |
                    (x[ViewKeys.ViewName] == self.parent_view)
                )
            )
        else:
            base = (
                r
                .table(ViewCollections.Views)
            )

        return base

    def _set_merge_hash(self):
        merge_hash = (
            lambda x:
            {
                ViewKeys.Users: (
                    r
                    .expr(x[ViewKeys.Users])
                    .map(
                        lambda y:
                        {
                            ViewMappedKeys.UserName: y
                        }
                    )
                ),
                ViewMappedKeys.Groups: (
                    r
                    .table(GroupCollections.Groups)
                    .get_all(x[ViewKeys.ViewName], index=GroupIndexes.Views)
                    .coerce_to('array')
                    .pluck(GroupKeys.GroupId, GroupKeys.GroupName)
                )
            }
        )

        return merge_hash
