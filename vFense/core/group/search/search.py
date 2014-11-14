from vFense.core.group._db_model import GroupKeys
from vFense.core.group.search._db import FetchGroups
from vFense.core.decorators import time_it
from vFense.search.base import RetrieveBase

class RetrieveGroups(RetrieveBase):
    def __init__(self, sort_key=GroupKeys.GroupName,
                 is_global=False, **kwargs):
        super(RetrieveGroups, self).__init__(**kwargs)
        self.is_global = is_global

        self.valid_keys_to_filter_by = (
            [
                GroupKeys.GroupName, GroupKeys.Email,
            ]
        )

        valid_keys_to_sort_by = (
            [
                GroupKeys.GroupName, GroupKeys.Email,
            ]
        )
        if sort_key not in valid_keys_to_sort_by:
            self.sort_key = GroupKeys.GroupName

        self.fetch = (
            FetchGroups(
                view_name=self.view_name, count=self.count,
                offset=self.offset, sort=self.sort, sort_key=self.sort_key,
                is_global=is_global
            )
        )

    @time_it
    def by_id(self, group_id):
        """Retrieve group by group id
        Args:
            group_id (str): The 36 character UUID of the group.

        Basic Usage:
            >>> from vFense.core.groups.search.search import RetrieveGroups
            >>> search_groups = RetrieveGroups(view_name='global')
            >>> search_groups.by_name('global')

        Returns:
            List of dictionairies.
        """
        count, data = self.fetch.by_id(group_id)
        return self._base(count, data)

    @time_it
    def by_name(self, name):
        """Query groups by group name.
        Args:
            name (str): The name of the group you are searching for.

        Basic Usage:
            >>> from vFense.core.groups.search.search import RetrieveGroups
            >>> search_groups = RetrieveGroups(view_name='global')
            >>> search_groups.by_name('global')

        Returns:
            List of dictionairies.
        """
        count, data = self.fetch.by_name(name)
        return self._base(count, data)

    @time_it
    def by_regex(self, name):
        """Query groups by regex on group name.
        Args:
            name (str): The regex you are searching by

        Basic Usage:
            >>> from vFense.core.groups.search.search import RetrieveGroups
            >>> search_groups = RetrieveGroups(view_name='global')
            >>> search_groups.by_name('global')

        Returns:
            List of dictionairies.
        """
        count, data = self.fetch.by_regex(name)
        return self._base(count, data)

    @time_it
    def all(self):
        """Retrieve all groups.
        Basic Usage:
            >>> from vFense.core.group.search.search import RetrieveGroups
            >>> search_groups = (
                    RetrieveGroups(
                        view_name='global', is_global=True
                    )
                )
            >>> search_groups.all()

        Returns:
        """
        count, data = self.fetch.all()
        return self._base(count, data)
