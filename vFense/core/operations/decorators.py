from functools import wraps

from vFense.core.operations import AdminOperation
from vFense.core.operations.admin_operations import AdminOperationManager
from vFense.core.user._db_model import UserKeys
from vFense.core.user.manager import UserManager
from vFense.core.results import ApiResultKeys


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
                rcopy = results.copy()
                vfense_code = rcopy[ApiResultKeys.VFENSE_STATUS_CODE]
                generic_code = rcopy[ApiResultKeys.GENERIC_STATUS_CODE]
                errors = rcopy.get(ApiResultKeys.ERRORS, [])
                ids_created = rcopy.get(ApiResultKeys.GENERATED_IDS, [])
                ids_updated = rcopy.get(ApiResultKeys.UPDATED_IDS, [])
                ids_removed = rcopy.get(ApiResultKeys.DELETED_IDS, [])
                updated_operation = AdminOperationManager(
                    status_message=rcopy[ApiResultKeys.MESSAGE],
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
