from vFense.db.client import db_create_close, r
from vFense.core.decorators import catch_it, time_it
from vFense.core.user._db_model import (
    UserCollections, UserKeys, UserMappedKeys, UserIndexes
)
from vFense.core.group._db_model import (
    GroupCollections, GroupKeys, GroupIndexes
)
from vFense.core.view._db_model import ViewKeys
from vFense.core.permissions._constants import Permissions
from vFense.search._db_base import FetchBase

class FetchUsers(FetchBase):
    """Agent operation database queries"""
    def __init__(self, sort_key=UserKeys.UserName, is_global=False, **kwargs):
        super(FetchUsers, self).__init__(**kwargs)
        self.is_global = is_global

    @time_it
    @catch_it((0, []))
    @db_create_close
    def all(self, conn=None):
        """Retrieve all user and all of its properties

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
            .without(UserKeys.Password)
            .run(conn)
        )

        return(count, data)

    @time_it
    @catch_it((0, []))
    @db_create_close
    def by_regex(self, username, conn=None):
        """Retrieve users by regex and all of its properties

        Basic Usage:
            >>> from vFense.user.search._db import FetchUsers
            >>> view_name = 'global'
            >>> users = FetchUsers(view_name)
            >>> users.fetch_by_regex("glob")

        Returns:
            List of users and their properties.
        """
        count = 0
        data = []
        base_filter = self._set_base_query()
        merge_hash = self._set_merge_hash()
        count = (
            base_filter
            .filter(
                lambda x:
                x[UserKeys.UserName].match("(?i)^"+username)
            )
            .count()
            .run(conn)
        )

        data = list(
            base_filter
            .filter(
                lambda x:
                x[UserKeys.UserName].match("(?i)^"+username)
            )
            .coerce_to('array')
            .order_by(self.sort(self.sort_key))
            .skip(self.offset)
            .limit(self.count)
            .merge(merge_hash)
            .without(UserKeys.Password)
            .run(conn)
        )

        return(count, data)

    @time_it
    @catch_it((0, []))
    @db_create_close
    def by_name(self, username, conn=None):
        """Retrieve user by name and all of its properties

        Basic Usage:
            >>> from vFense.user.search._db import FetchUsers
            >>> view_name = 'global'
            >>> users = FetchUsers(view_name)
            >>> users.fetch_by_name("global_admin")

        Returns:
            List of users and their properties.
        """
        count = 0
        data = []
        base_filter = self._set_base_query()
        merge_hash = self._set_merge_hash()
        count = (
            base_filter
            .filter({UserKeys.UserName: username})
            .count()
            .run(conn)
        )

        data = list(
            base_filter
            .filter({UserKeys.UserName: username})
            .coerce_to('array')
            .order_by(self.sort(self.sort_key))
            .skip(self.offset)
            .limit(self.count)
            .merge(merge_hash)
            .without(UserKeys.Password)
            .run(conn)
        )

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
                    .filter({UserKeys.IsGlobal: False})
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
                    .filter({UserKeys.IsGlobal: False})
                )

        return base

    def _set_merge_hash(self):
        merge_hash = (
            lambda x:
            {
                UserKeys.DateAdded: x[UserKeys.DateAdded].to_epoch_time(),
                UserKeys.DateModified: (
                    x[UserKeys.DateModified].to_epoch_time()
                ),
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
                            ViewKeys.ViewName: y
                        }
                    )
                )
            }
        )

        return merge_hash
