from vFense.core.view._db_model import ViewKeys
from vFense.core.view.search._db import FetchViews
from vFense.core.decorators import time_it
from vFense.search.base import RetrieveBase

class RetrieveViews(RetrieveBase):
    def __init__(
        self, parent_view=None, is_global=False,
        sort_key=ViewKeys.ViewName, **kwargs
        ):
        super(RetrieveViews, self).__init__(**kwargs)
        self.parent_view = parent_view
        self.is_global = is_global
        self.sort_key = sort_key

        self.valid_keys_to_filter_by = (
            [
                ViewKeys.ViewName,
            ]
        )

        valid_keys_to_sort_by = (
            [
                ViewKeys.ViewName,
            ]
        )
        if self.sort_key not in valid_keys_to_sort_by:
            self.sort_key = ViewKeys.ViewName

        self.fetch_views = (
            FetchViews(
                parent_view=self.parent_view, count=self.count,
                offset=self.offset, sort=self.sort, sort_key=self.sort_key,
                is_global=self.is_global
            )
        )

    @time_it
    def by_regex(self, name):
        """Query views by regex.
        Args:
            name (str): The regex you are searching by

        Basic Usage:
            >>> from vFense.core.views.search.search import RetrieveViews
            >>> search_views = RetrieveViews()
            >>> search_views.by_regex('global')

        Returns:
            List of dictionairies.
        """
        count, data = self.fetch_views.by_regex(name)
        return self._base(count, data)

    @time_it
    def by_name(self, name):
        """Get view by name.
        Args:
            name (str): The regex you are searching by

        Basic Usage:
            >>> from vFense.core.views.search.search import RetrieveViews
            >>> search_views = RetrieveViews()
            >>> search_views.by_name('global')

        Returns:
            List of dictionairies.
        """
        count, data = self.fetch_views.by_name(name)
        return self._base(count, data)

    @time_it
    def all(self):
        """Retrieve all views.
        Basic Usage:
            >>> from vFense.core.view.search.search import RetrieveViews
            >>> search_views = RetrieveViews()
            >>> search_views.all()

        Returns:
        """
        count, data = self.fetch_views.all()
        return self._base(count, data)

    @time_it
    def for_user(self, name):
        """Get all views for a user.
        Args:
            name (str): The name of the user of the
                views you are searching for.

        Basic Usage:
            >>> from vFense.core.views.search.search import RetrieveViews
            >>> search_views = RetrieveViews(is_global=True)
            >>> search_views.for_user('global_admin')

        Returns:
            List of dictionairies.
        """
        count, data = self.fetch_views.for_user(name)
        return self._base(count, data)
