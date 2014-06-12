from functools import wraps

from vFense.core.operations import AdminOperation
from vFense.core.operations.admin_operations import AdminOperationManager
from vFense.core.user._db_model import UserKeys
from vFense.core.user.manager import UserManager
from vFense.errorz._constants import ApiResultKeys


def log_operation(action, performed_on):
    def wrapper(fn):
        def wrapped(*args, **kwargs):
            tornado_handler = args[0]
            active_user = tornado_handler.get_current_user()
            active_view = (
                UserManager(active_user).get_attribute(UserKeys.CurrentView)
            )
            operation = AdminOperation(
                active_user, action, performed_on, current_view=active_view
            )
            manager = AdminOperationManager()
            operation_id = manager.create(operation)
            if operation_id:
                results = fn(*args, **kwargs)
                vfense_code = results[ApiResultKeys.VFENSE_STATUS_CODE]
                generic_code = results[ApiResultKeys.GENERIC_STATUS_CODE]
                errors = results.get(ApiResultKeys.ERRORS, [])
                ids_created = results.get(ApiResultKeys.IDS_CREATED, [])
                ids_updated = results.get(ApiResultKeys.IDS_UPDATED, [])
                ids_removed = results.get(ApiResultKeys.IDS_REMOVED, [])
                updated_operation = AdminOperation(
                    status_message=results[ApiResultKeys.MESSAGE],
                    generic_status_code=generic_code,
                    vfense_status_code=vfense_code,
                    errors=errors, ids_created=ids_created,
                    ids_updated=ids_updated, ids_removed=ids_removed
                )
                manager.update(operation_id, updated_operation)
                return results

            else:
                results = fn(*args, **kwargs)
                return results

        return wraps(fn)(wrapped)

    return(wrapper)
