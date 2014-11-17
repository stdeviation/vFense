from vFense.db.client import r
from vFense.core.view._db_model import ViewKeys

class ViewMerge():
    VIEWS = (
        {
            ViewKeys.DateModified: (
                r.row[ViewKeys.DateModified].to_epoch_time()
            ),
            ViewKeys.DateAdded: (
                r.row[ViewKeys.DateAdded].to_epoch_time()
            )
        }
    )
