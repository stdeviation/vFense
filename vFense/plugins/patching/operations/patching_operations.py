from vFense.core.operations import OperPerAgent, OperPerApp
from vFense.core.operations.agent_operations import AgentOperationManager
from vFense.core.operations._db_agent import update_operation_per_agent, \
    group_operations_per_app_by_results, update_operation_per_app, \
    update_errors_and_pending_count, update_failed_and_pending_count, \
    update_completed_and_pending_count, insert_agent_into_agent_operations, \
    insert_app_into_agent_operations

from vFense.core.status_codes import DbCodes
from vFense.core.operations.status_codes import (
    AgentOperationCodes, OperationPerAgentCodes
)


class PatchingOperation(AgentOperationManager):
    """Creates the operations for the patching plugin."""

    def add_agent_to_install_operation(
            self, agent_id, operation_id, applications
        ):
        """Add an install operation for an agent
        Args:
            agent_id (str): the agent id.
            operation_id (str): the operation id.
            applications (list): List of application dictionairies.

        Basic Usage:
            >>> from vFense.core.operations.agent_operations import AgentOperation
            >>> username = 'admin'
            >>> view_name = 'default'
            >>> oper = AgentOperation(username, view_name)
            >>> operation_id = '5dc03727-de89-460d-b2a7-7f766c83d2f1'
            >>> agent_id = '38c1c67e-436f-4652-8cae-f1a2ac2dd4a2'
            >>> applications = [
                    {
                        'app_id': '70d462913faad1ecaa85eda4c448a607164fe39414c8be44405e7ab4f7f8467c',
                        'app_name': 'linux-firmware'
                    }
                ]
            >>> oper.add_agent_to_install_operation(
                    agent_id, operation_id, applications
                )

        Returns:
            Boolean
        """
        completed = False
        operation = OperPerAgent()
        operation.fill_in_defaults()
        operation.agent_id = agent_id
        operation.operation_id = operation_id
        operation.apps_total_count = len(applications)
        operation.apps_pending_count = len(applications)
        operation.status = OperationPerAgentCodes.PendingPickUp
        operation.view_name = self.view_name

        status_code, count, errors, generated_ids = (
            insert_agent_into_agent_operations(operation.to_dict_db())
        )
        if status_code == DbCodes.Inserted:
            apps = []
            for app in applications:
                app_operation = OperPerApp()
                app_operation.fill_in_defaults()
                app_operation.agent_id = agent_id
                app_operation.app_id = app.app_id
                app_operation.app_name = app.app_name
                app_operation.app_version = app.app_version
                app_operation.results = AgentOperationCodes.ResultsPending
                app_operation.view_name = self.view_name
                apps.append(app_operation.to_dict_db())

            status_code, count, errors, generated_ids = (
                insert_app_into_agent_operations(apps)
            )
            if status_code == DbCodes.Inserted:
                completed = True

        return completed

    def update_app_results(
            self, operation_id, agent_id, app_id,
            status=AgentOperationCodes.ResultsReceived,
            errors=None, apps_removed=None
        ):
        """Update the results for an application.
        Args:
            operation_id (str): The operation id.
            agent_id (str): The agent id.
            app_id (str): The application id.

        Kwargs:
            status (int): The operation status code.
                default = 6002
            errors (str): The error message.
                default = None.
            apps_removed (list): list of dictionaries
                of the app name and app version
                default = None.

        Basic Usage:
            >>> from vFense.core.operations.agent_operations import AgentOperation
            >>> username = 'admin'
            >>> view_name = 'default'
            >>> oper = AgentOperation(username, view_name)
            >>> operation_id = '5dc03727-de89-460d-b2a7-7f766c83d2f1'
            >>> agent_id = '38c1c67e-436f-4652-8cae-f1a2ac2dd4a2'
            >>> app_id = '70d462913faad1ecaa85eda4c448a607164fe39414c8be44405e7ab4f7f8467c'
            >>> status_code = 6006
            >>> oper.update_operation_results(
                    operation_id, agent_id, app_id, status_code
                )

        Returns:
            Boolean
        """
        completed = False
        if not apps_removed:
            apps_removed = []
        operation_data = OperPerApp()
        operation_data.results_received_time = self.now
        operation_data.apps_removed = apps_removed
        operation_data.errors = errors
        operation_data.results = status
        status_code, count, errors, generated_ids = (
            update_operation_per_app(
                operation_id, agent_id, app_id, operation_data.to_dict_db()
            )
        )

        if status_code == DbCodes.Replaced or status_code == DbCodes.Unchanged:
            self._update_app_stats(operation_id, agent_id, app_id)
            completed = True

        return completed

    def _update_app_stats(self, operation_id, agent_id, app_id):

        """Update the total counts based on the status code.
        Args:
            operation_id (str): The operation id.
            agent_id (str): The agent id.
            app_id (str): The application id.

        Basic Usage:
            >>> from vFense.core.operations.agent_operations import AgentOperation
            >>> username = 'admin'
            >>> view_name = 'default'
            >>> oper = AgentOperation(username, view_name)
            >>> operation_id = '5dc03727-de89-460d-b2a7-7f766c83d2f1'
            >>> agent_id = '38c1c67e-436f-4652-8cae-f1a2ac2dd4a2'
            >>> app_id = '70d462913faad1ecaa85eda4c448a607164fe39414c8be44405e7ab4f7f8467c'
            >>> oper._update_app_stats(
                    operation_id, agent_id, app_id,
                )

        Returns:
            Boolean
        """

        completed = False
        pending_count, completed_count, failed_count = (
            group_operations_per_app_by_results(
                operation_id, agent_id
            )
        )

        operation_data = OperPerAgent()
        operation_data.completed_count = completed_count
        operation_data.failed_count = failed_count
        operation_data.pending_count = pending_count

        status_code, count, errors, generated_ids = (
            update_operation_per_agent(
                operation_id, agent_id, operation_data.to_dict_db()
            )
        )

        if status_code == DbCodes.Replaced or status_code == DbCodes.Unchanged:
            self._update_agent_stats_by_app_stats(
                operation_id, agent_id, completed_count,
                failed_count, pending_count
            )
            completed = True

        return completed

    def _update_agent_stats_by_app_stats(
            self, operation_id, agent_id,
            completed_count, failed_count,
            pending_count
        ):
        """Update the total counts based on the status code.
        Args:
            operation_id (str): the operation id.
            agent_id (str): the agent id.
            completed_count (int): the completed count.
            failed_count (int): the failed count.
            pending_count (int): the pending count.

        Basic Usage:
            >>> from vFense.core.operations.agent_operations import AgentOperation
            >>> username = 'admin'
            >>> view_name = 'default'
            >>> oper = AgentOperation(username, view_name)
            >>> operation_id = '5dc03727-de89-460d-b2a7-7f766c83d2f1'
            >>> agent_id = '38c1c67e-436f-4652-8cae-f1a2ac2dd4a2'
            >>> completed_count = 1
            >>> pending_count = 0
            >>> failed_count = 0
            >>> oper._update_agent_stats_by_app_stats(
                    operation_id, agent_id, completed_count,
                    failed_count, pending_count
                )

        Returns:
            Boolean
        """
        completed = False
        total_count = completed_count + failed_count + pending_count
        if total_count == completed_count:
            status_code, count, errors, generated_ids = (
                update_completed_and_pending_count(operation_id, self.db_time)
            )

            if (status_code == DbCodes.Replaced or
                    status_code == DbCodes.Unchanged):
                self._update_completed_time_on_agents(operation_id, agent_id)
                self._update_operation_status_code(operation_id)
                completed = True

        elif total_count == failed_count:
            status_code, count, errors, generated_ids = (
                update_failed_and_pending_count(operation_id, self.db_time)
            )

            if (status_code == DbCodes.Replaced or
                    status_code == DbCodes.Unchanged):
                self._update_completed_time_on_agents(operation_id, agent_id)
                self._update_operation_status_code(operation_id)
                completed = True

        elif total_count == (failed_count + completed_count):
            status_code, count, errors, generated_ids = (
                update_errors_and_pending_count(operation_id, self.db_time)
            )

            if (status_code == DbCodes.Replaced or
                    status_code == DbCodes.Unchanged):
                self._update_completed_time_on_agents(operation_id, agent_id)
                self._update_operation_status_code(operation_id)
                completed = True

        return completed
