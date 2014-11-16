from functools import wraps

from vFense.core.operations import AdminOperation
from vFense.core.operations.admin_operations import AdminOperationManager
from vFense.core.user.manager import UserManager

def log_operation(action, performed_on):
    def wrapper(fn):
        def wrapped(*args, **kwargs):
            tornado_handler = args[0]
            active_user = tornado_handler.get_current_user()
            active_view = UserManager(active_user).properties.current_view
            operation = AdminOperation(
                active_user, action, performed_on, current_view=active_view
            )
            manager = AdminOperationManager()
            operation_id = manager.create(operation)
            if operation_id:
                results = fn(*args, **kwargs)
                updated_oper = AdminOperation()
                updated_oper.vfense_status_code = results.vfense_status_code
                updated_oper.generic_status_code = results.generic_status_code
                updated_oper.errors = results.errors
                updated_oper.ids_created = results.generated_ids
                updated_oper.ids_updated = results.updated_ids
                updated_oper.ids_removed = results.deleted_ids
                manager.update(operation_id, updated_oper)
                return results

            else:
                results = fn(*args, **kwargs)
                return results

        return wraps(fn)(wrapped)

    return(wrapper)
