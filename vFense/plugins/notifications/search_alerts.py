import logging
import logging.config
from vFense._constants import VFENSE_LOGGING_CONFIG
from vFense.core.agent._db_model import *
from vFense.core.tag._db_model import *
from vFense.db.client import db_create_close, r
from vFense.core.results import Results
from vFense.search.base import RetrieveBase
from vFense.core.operations._db_model import *
from vFense.core.results import ApiResults
from vFense.notifications import *
from vFense.rv_exceptions.broken import *


logging.config.fileConfig(VFENSE_LOGGING_CONFIG)
logger = logging.getLogger('rvapi')


class FetchAlerts(RetrieveBase):
    def __init__(self, username, view_name, uri, method):
        self.username = username
        self.view_name = view_name
        self.uri = uri
        self.method = method
        self.base_merge = (
            {
                NotificationKeys.CreatedTime: r.row[NotificationKeys.CreatedTime].to_epoch_time(),
                NotificationKeys.ModifiedTime: r.row[NotificationKeys.ModifiedTime].to_epoch_time(),
            }
        )


    @db_create_close
    def get_notification(self, notification_id, conn=None):
        try:
            data = (
                r
                .table(NotificationCollections.Notifications)
                .get_all(notification_id)
                .map(self.map_list)
                .run(conn)
            )
            results = (
                Results(
                    self.username, self.uri, self.method
                ).information_retrieved(data[0], len(data[0]))
            )
        except Exception as e:
            logger.exception(e)
            results = (
                Results(
                    self.username, self.uri, self.method
                ).something_broke(
                    notification_id,
                    'failed to get notifcation', e
                )
            )

        return(results)
