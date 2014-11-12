import logging
import logging.config
from vFense._constants import VFENSE_LOGGING_CONFIG
from vFense.core._constants import SortValues, DefaultQueryValues
from vFense.core.agent._db_model import *
from vFense.core.tag._db_model import *
from vFense.db.client import db_create_close, r
from vFense.plugins.notifications._db_model import (
    NotificationKeys, NotificationCollections
)


logging.config.fileConfig(VFENSE_LOGGING_CONFIG)
logger = logging.getLogger('rvapi')


class FetchAlerts(object):
    def __init__(
        self, view_name=None,
        count=DefaultQueryValues.COUNT,
        offset=DefaultQueryValues.OFFSET,
        sort=SortValues.ASC,
        sort_key=AgentKeys.ComputerName
        ):
        """
        Kwargs:
            view_name (str): Fetch all agents in this view.
            count (int): The number of results to return.
            offset (int): The next set of results beginning at offset.
            sort (str): asc or desc.
            sort_key (str): The key you are going to sort the results by.
        """
        self.view_name = view_name
        self.count = count
        self.offset = offset
        self.sort_key = sort_key

        if sort == SortValues.ASC:
            self.sort = r.asc
        else:
            self.sort = r.desc

    @time_it
    @catch_it((0, []))
    @db_create_close
    def get_notification(self, notification_id, conn=None):
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
