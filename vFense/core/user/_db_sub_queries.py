from vFense.db.client import r
from vFense.core.user._db_model import UserKeys

class Merge():
    DATE = (
        {
            UserKeys.DateAdded: r.row[UserKeys.DateAdded].to_epoch_time(),
            UserKeys.DateModified: r.row[UserKeys.DateModified].to_epoch_time()
        }
    )
