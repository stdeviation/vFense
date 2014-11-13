from vFense.db.client import db_create_close, r
from vFense.core.decorators import catch_it, time_it
from vFense.core.operations._db_model import (
    OperationCollections, AdminOperationKey, AdminOperationIndexes
)
from vFense.search._db_base import FetchBase

class FetchAdminOperations(FetchBase):
    def __init__(self, sort_key=AdminOperationKey.CreatedTime, **kwargs):
        super(FetchAdminOperations, self).__init__(**kwargs)

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
