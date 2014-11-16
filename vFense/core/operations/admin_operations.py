import logging
import logging.config
from time import time

from vFense._constants import VFENSE_LOGGING_CONFIG
from vFense.core.operations._db_model import (
    AdminOperationKey
)
from vFense.core._db_constants import DbTime

from vFense.core.operations._db_admin import (
    fetch_admin_operation, insert_admin_operation, update_admin_operation
)

from vFense.core.status_codes import DbCodes

logging.config.fileConfig(VFENSE_LOGGING_CONFIG)
logger = logging.getLogger('vfense_api')

class AdminOperationManager(object):
    """This is what creates operations for an agent or multiple agents.

    """
    def __init__(self):
        """
        Args:
            username (str): the name of the user who created the operation.
            view_name (str): the name of the view this user is part of.

        Basic Usage:
            >>> from vFense.core.operations.admin_operations import AdminOperationManager
            >>> oper = AdminOperationManager()
        """
        self.now = time()
        self.db_time = DbTime.now()
        self.INIT_COUNT = 0


    def create(self, operation):
        """Create the operation and return the operation_id.
        Args:
            operation (AdminOperation): AdminOperation instance.

        Basic Usage:
            >>> from vFense.core.operations.admin_operations import AdminOperationManager
            >>> username = 'global_admin'
            >>> view_name = 'global'
            >>> action = 'create user'
            >>> performed_on = 'user'
            >>> oper = AdminOperation(
                username=username, current_view=view_name,
                action=action, performed_on=performed_on
            )
            >>> oper_manager = AdminOperationManager()
            >>> oper.create(oper)

        Returns:
            String The 36 character UUID of the operation that was created.
            6c0209d5-b350-48b7-808a-158ddacb6940
        """
        operation.fill_in_defaults()
        operation.created_time = self.now
        operation.comepleted_time = 0
        status_code, _, _, generated_ids = (
            insert_admin_operation(operation.to_dict_db())
        )
        if status_code == DbCodes.Inserted:
            operation.operation_id = generated_ids[0]


        return operation.operation_id


    def update(self, operation_id, operation):
        """Update the operation with the results.
        Args:
            operation_id (str): The UUID of the operation.
            operation (AdminOperation): AdminOperation instance.

        Basic Usage:
            >>> from vFense.core.operations import AdminOperationManager
            >>> from vFense.core.operations.admin_operations import AdminOperationManagerManager
            >>> username = 'global_admin'
            >>> view_name = 'global'
            >>> oper = AdminOperationManager(username, view_name)
            >>> action = 'create user'
            >>> performed_on = 'user'
            >>> operation_id = oper.create(action, performed_on)
            >>> oper = AdminOperationManager(
                status_message="user foo created successfully',
                generic_status_code=1008, vfense_status_code=12008,
                ids_created=['foo']
            )
            >>> oper.update(operation_id, oper)

        Returns:
            String The 36 character UUID of the operation that was created.
            6c0209d5-b350-48b7-808a-158ddacb6940
        """
        completed = False
        status_code, _, _, generated_ids = (
            update_admin_operation(operation_id, operation.to_dict_db())
        )
        if status_code == DbCodes.Replaced:
            completed = True

        return completed

