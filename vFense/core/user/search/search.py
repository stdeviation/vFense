from vFense.core.user._db_model import UserKeys
from vFense.core.user.search._db import FetchUsers
from vFense.core.decorators import time_it
from vFense.search.base import RetrieveBase

class RetrieveUsers(RetrieveBase):
    def __init__(self, sort_key=UserKeys.UserName, is_global=False, **kwargs):
        super(RetrieveUsers, self).__init__(**kwargs)
        self.is_global = is_global

        self.valid_keys_to_filter_by = (
            [
                UserKeys.UserName,
                UserKeys.FullName,
                UserKeys.Email,
            ]
        )

        valid_keys_to_sort_by = (
            [
                UserKeys.UserName,
                UserKeys.FullName,
                UserKeys.Email,
            ]
        )
        if self.sort_key not in valid_keys_to_sort_by:
            self.sort_key = UserKeys.UserName

        self.fetch_users = (
            FetchUsers(
                view_name=self.view_name, count=self.count,
                offset=self.offset, sort=self.sort,
                sort_key=self.sort_key, is_global=is_global
            )
        )


    @time_it
    def by_name(self, name):
        """Retrieve user by username.
        Args:
            name (str): The name of the user you are retrieving.

        Basic Usage:
            >>> from vFense.core.user.search.search import RetrieveUsers
            >>> search_users = RetrieveUsers(view_name='global')
            >>> search_users.by_name('global')

        Returns:
            List of dictionairies.
        """
        count, data = self.fetch_users.by_name(name)
        return self._base(count, data)

    @time_it
    def by_regex(self, name):
        """Query users by regex on a username.
        Args:
            name (str): The regex you are searching by

        Basic Usage:
            >>> from vFense.core.user.search.search import RetrieveUsers
            >>> search_users = RetrieveUsers(view_name='global')
            >>> search_users.by_name('global')

        Returns:
            List of dictionairies.
        """
        count, data = self.fetch_users.by_regex(name)
        return self._base(count, data)

    @time_it
    def all(self):
        """Retrieve all agents.
        Basic Usage:
            >>> from vFense.core.user.search.search import RetrieveUsers
            >>> search_users = (
                    RetrieveUsers(
                        view_name='global', is_global=True
                    )
                )
            >>> search_users.all()

        Returns:
        """
        count, data = self.fetch_users.all()
        return self._base(count, data)
