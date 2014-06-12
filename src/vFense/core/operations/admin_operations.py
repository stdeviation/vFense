#!/usr/bin/env python

from vFense import logging
from time import time
from vFense.core.operations import AdminOperation
from vFense.core.operations._db_model import (
    AdminOperationKey
)
from vFense.core.operations._constants import vFenseObjects, OperationErrors
from vFense.core._db_constants import DbTime

from vFense.core.operations._db_admin import (
    fetch_admin_operation, insert_admin_operation,
    update_admin_operation
)

from vFense.errorz.status_codes import (
    DbCodes
)

class AdminOperationManager(object):
    """This is what creates operations for an agent or multiple agents.

    """
    def __init__(self):
        """
        Args:
            username (str): the name of the user who created the operation.
            view_name (str): the name of the view this user is part of.

        Basic Usage:
            >>> from vFense.core.operations.admin_operations import AdminOperation
            >>> oper = AdminOperation()
        """
        self.now = time()
        self.db_time = DbTime.time_now()
        self.INIT_COUNT = 0


    def create(self, operation):
        """Create the operation and return the operation_id.
        Args:
            operation (AdminOperation): AdminOperation instance.

        Basic Usage:
            >>> from vFense.core.operations.admin_operations import AdminOperation
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
        operation_id = None
        operation.fill_in_defaults()
        data = operation.to_dict()
        data[AdminOperationKey.CreatedTime] = self.db_time
        data[AdminOperationKey.CompletedTime] = (
            DbTime.begining_of_time()
        )

        status_code, _, _, generated_ids = (
            insert_admin_operation(data)
        )
        if status_code == DbCodes.Inserted:
            operation_id = generated_ids[0]


        return operation_id


    def update(self, operation_id, operation):
        """Update the operation with the results.
        Args:
            operation_id (str): The UUID of the operation.
            operation (AdminOperation): AdminOperation instance.

        Basic Usage:
            >>> from vFense.core.operations import AdminOperation
            >>> from vFense.core.operations.admin_operations import AdminOperationManager
            >>> username = 'global_admin'
            >>> view_name = 'global'
            >>> oper = AdminOperation(username, view_name)
            >>> action = 'create user'
            >>> performed_on = 'user'
            >>> operation_id = oper.create(action, performed_on)
            >>> oper = AdminOperation(
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
        data = operation.to_dict_non_null()
        status_code, _, _, generated_ids = (
            update_admin_operation(data)
        )
        if status_code == DbCodes.Replaced:
            completed = True

        return completed

