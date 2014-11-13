from vFense.core.decorators import time_it
from vFense.search.base import RetrieveBase
from vFense.plugins.notifications.search._alerts_db import FetchAlerts

class RetrieveNotifications(RetrieveBase):
    def __init__(self, **kwargs):
        super(RetrieveNotifications, self).__init__(**kwargs)

        self.fetch = (
            FetchAlerts(
                self.view_name, self.count, self.offset,
                self.sort, self.sort_key
            )
        )

    @time_it
    def by_id(self, notification_id):
        """Retrieve a notification and all its properties by id
        Args:
            notification_id (str): The 36 character UUID of the notification
                you are retrieving.

        Basic Usage:
            >>> from vFense.plugins.notifications.search.alerts import RetrieveNotifications
            >>> view_name = 'default'
            >>> search = RetrieveNotifications(view_name='default')
            >>> search.by_id('74b70fcd-9ed5-4cfd-9779-a45d60478aa3')

        Returns:
            ApiResults Instance
        """
        count, data = self.fetch.by_id(notification_id)
        return self._base(count, data)
