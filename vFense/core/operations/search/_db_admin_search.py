import logging, logging.config

from vFense._constants import VFENSE_LOGGING_CONFIG
from vFense.db.client import db_create_close, r
from vFense.core._constants import SortValues, DefaultQueryValues
from vFense.core.decorators import catch_it, time_it

from vFense.core.operations._db_model import (
    OperationCollections, AdminOperationKey, AdminOperationIndexes
)

logging.config.fileConfig(VFENSE_LOGGING_CONFIG)
logger = logging.getLogger('rvapi')

class FetchAdminOperations(object):
    """Agent operation database queries"""
    def __init__(
            self, view_name=None,
            count=DefaultQueryValues.COUNT,
            offset=DefaultQueryValues.OFFSET,
            sort=SortValues.ASC,
            sort_key=AdminOperationKey.CreatedTime
        ):
        """
        Kwargs:
            view_name (str): Name of the current view.
                default = None
            count (int): Maximum number of results to return.
                default = 30
            offset (int): Retrieve operations after this number. Pagination.
                default = 0
            sort (str): Sort either by asc or desc.
                default = desc
            sort_key (str): Sort by a valid field.
                examples... operation, status, created_time, updated_time,
                completed_time, and created_by.
                default = created_time

        Basic Usage:
            >>> from vFense.core.operations.search._db_agent_search import FetchAgentOperations
            >>> view_name = 'default'
            >>> operation = FetchAgentOperations(view_name)
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
    def fetch_all(self, conn=None):
        """Fetch all operations
        Basic Usage:
            >>> from vFense.core.operations.search._db_admin_search import FetchAdminOperations
            >>> view_name = 'global'
            >>> operation = FetchAgentOperations(view_name)
            >>> operation.fetch_all()
        Returns:
            List
        """
        count = 0
        data = []
        base_filter = self._set_admin_operation_base_query()
        base_time_merge = self._set_base_time_merge()
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
            .merge(base_time_merge)
            .run(conn)
        )

        return(count, data)

    def _set_admin_operation_base_query(self):
        base_filter = (
            r
            .table(OperationCollections.Admin)
        )
        if self.view_name:
            base_filter = (
                r
                .table(OperationCollections.Admin)
                .get_all(
                    self.view_name,
                    index=AdminOperationIndexes.CurrentView
                )
            )

        return base_filter

    def _set_base_time_merge(self):
        merge = (
            {
                AdminOperationKey.CreatedTime: (
                    r.row[AdminOperationKey.CreatedTime].to_epoch_time()
                ),
            }
        )

        return merge
