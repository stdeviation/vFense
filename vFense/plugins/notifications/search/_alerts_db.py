from vFense.core.decorators import time_it, catch_it
from vFense.db.client import db_create_close, r
from vFense.plugins.notifications._db_model import (
    NotificationKeys, NotificationCollections
)
from vFense.search._db_base import FetchBase

class FetchAlerts(FetchBase):
    def __init__(self, sort_key=NotificationKeys.RuleName, **kwargs):
        super(FetchAlerts, self).__init__(**kwargs)
        self.sort_key = sort_key

    @time_it
    @catch_it((0, []))
    @db_create_close
    def by_id(self, notification_id, conn=None):
        """Retrive alerts by notification id
        Args:
            name (str): The regex you are searching by

        Basic Usage:
            >>> from vFense.plugins.notifications.search._db import FetchAlerts
            >>> view_name = 'default'
            >>> search = FetchAlerts(view_name='default')
            >>> search.by_id('b109c6cf-50b9-480c-959f-f895a41486a9')

        Returns:
            List of dictionairies.
        """
        merge_query = self._set_merge_query()
        base_filter = self._set_base_query()
        count = (
            base_filter
            .count()
            .run(conn)
        )
        data = (
            base_filter
            .get_all(notification_id)
            .merge(merge_query)
            .run(conn)
        )

        return(count, data)

    def _set_base_query(self):
        if self.view_name:
            base_filter = (
                r
                .table(NotificationCollections.Notifications)
                .get_all(
                    self.view_name,
                    index=NotificationKeys.ViewName
                )
            )
        else:
            base_filter = (
                r
                .table(NotificationCollections.Notifications)
            )

        return base_filter

    def _set_merge_query(self):
        merge_query = (
            lambda x:
            {
                NotificationKeys.CreatedTime: (
                    x[NotificationKeys.CreatedTime].to_epoch_time()
                ),
                NotificationKeys.ModifiedTime: (
                    x[NotificationKeys.ModifiedTime].to_epoch_time()
                ),
            }
        )
        return merge_query
