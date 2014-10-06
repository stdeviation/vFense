import re
from vFense import Base
from vFense.core._db_constants import DbTime
from vFense.core.operations._db_model import (
    AdminOperationKey, AgentOperationKey, OperationPerAgentKey,
    OperationPerAppKey
)
from vFense.core.operations._admin_constants import (
    AdminOperationDefaults, AdminActions
)
from vFense.core.operations._operation_per_agent_constants import (
    OperPerAgentDefaults
)
from vFense.core.operations._operation_per_app_constants import (
    OperPerAppDefaults
)
from vFense.core.operations._operation_constants import (
    OperationDefaults
)
from vFense.core._constants import CommonKeys
from vFense.core.results import ApiResultKeys
from vFense.core.status_codes import (
    GenericFailureCodes
)

class AdminOper(Base):
    """Used to represent an instance of an admin operation."""

    def __init__(
        self, created_by=None, action=None, operation_id=None,
        performed_on=None, status_message=None, generic_status_code=None,
        vfense_status_code=None, errors=None, current_view=None,
        completed_time=None, created_time=None, object_data=None,
        ids_created=None, ids_updated=None, ids_removed=None
    ):
        """
        Kwargs:
            operation_id (str): The 36 character UUID of the operation.
            created_by (str): The name of the user who created the operation.
            action (str): The action that was performed.
            performed_on (str): The object the action was performed on.
            status_message (str): The status message.
            generic_status_code (int): The generic status code.
            vfense_status_code (int): The vfense status code.
            errors (list): List of dictionaires with errors.
            current_view (str): The current view, in which the
                operation was created.
            completed_time (int): The time this operation was created.
            created_time (int): The time the operation completed.
            object_data (dict): Dictionary of data related to the object.
                example: {'name': 'Global Group', 'id': ''}
            ids_created (list): List of the ids that were generated.
            ids_updated (list): List of ids that were updated.
            ids_removed (list): List of ids that were removed.
        """
        self.operation_id = operation_id
        self.created_by = created_by
        self.action = action
        self.performed_on = performed_on
        self.status_message = status_message
        self.generic_status_code = generic_status_code
        self.vfense_status_code = vfense_status_code
        self.errors = errors
        self.current_view = current_view
        self.completed_time = completed_time
        self.created_time = created_time
        self.object_data = object_data
        self.ids_created = ids_created
        self.ids_updated = ids_updated
        self.ids_removed = ids_removed


    def fill_in_defaults(self):
        """Replace all the fields that have None as their value with
        the hardcoded default values.

        Use case(s):
            Useful when creating a new user instance and only want to fill
            in a few fields, then allow the create user functions call this
            method to fill in the rest.
        """

        if not self.ids_updated:
            self.ids_updated = AdminOperationDefaults.ids_updated()

        if not self.ids_created:
            self.ids_created = AdminOperationDefaults.ids_created()

        if not self.ids_removed:
            self.ids_removed = AdminOperationDefaults.ids_removed()

        if not self.errors:
            self.errors = AdminOperationDefaults.errors()

    def get_invalid_fields(self):
        """Check the user for any invalid fields.

        Returns:
            (list): List of key/value pair dictionaries corresponding
                to the invalid fields.

                Ex:
                    [
                        {'view_name': 'the invalid name in question'},
                        {'net_throttle': -10}
                    ]
        """
        invalid_fields = []

        if self.ids_created:
            if not isinstance(self.ids_created, list):
                invalid_fields.append(
                    {
                        AdminOperationKey.IdsCreated: self.ids_created,
                        CommonKeys.REASON: (
                            'Expecting a list and not a %s' %
                            (type(self.ids_created))
                        ),
                        ApiResultKeys.VFENSE_STATUS_CODE: (
                            GenericFailureCodes.InvalidInstanceType
                        )
                    }
                )

        if self.ids_updated:
            if not isinstance(self.ids_updated, list):
                invalid_fields.append(
                    {
                        AdminOperationKey.IdsUpdated: self.ids_updated,
                        CommonKeys.REASON: (
                            'Expecting a list and not a %s' %
                            (type(self.ids_updated))
                        ),
                        ApiResultKeys.VFENSE_STATUS_CODE: (
                            GenericFailureCodes.InvalidInstanceType
                        )
                    }
                )

        if self.ids_removed:
            if not isinstance(self.ids_removed, list):
                invalid_fields.append(
                    {
                        AdminOperationKey.IdsRemoved: self.ids_removed,
                        CommonKeys.REASON: (
                            'Expecting a list and not a %s' %
                            (type(self.ids_removed))
                        ),
                        ApiResultKeys.VFENSE_STATUS_CODE: (
                            GenericFailureCodes.InvalidInstanceType
                        )
                    }
                )

        if self.errors:
            if not isinstance(self.errors, list):
                invalid_fields.append(
                    {
                        AdminOperationKey.Errors: self.errors,
                        CommonKeys.REASON: (
                            'Expecting a list and not a %s' %
                            (type(self.errors))
                        ),
                        ApiResultKeys.VFENSE_STATUS_CODE: (
                            GenericFailureCodes.InvalidInstanceType
                        )
                    }
                )

        if self.action:
            if not self.action in AdminActions.get_admin_actions():
                invalid_fields.append(
                    {
                        AdminOperationKey.Action: self.action,
                        CommonKeys.REASON: (
                            'Invalid action %s' % (self.action)
                        ),
                        ApiResultKeys.VFENSE_STATUS_CODE: (
                            GenericFailureCodes.InvalidId
                        )
                    }
                )


        return invalid_fields

    def to_dict(self):
        """ Turn the fields into a dictionary.

        Returns:
            (dict): A dictionary with the fields.
        """

        return {
            AdminOperationKey.CreatedBy: self.created_by,
            AdminOperationKey.Action: self.action,
            AdminOperationKey.PerformedOn: self.performed_on,
            AdminOperationKey.StatusMessage: self.status_message,
            AdminOperationKey.GenericStatusCode: self.generic_status_code,
            AdminOperationKey.VfenseStatusCode: self.vfense_status_code,
            AdminOperationKey.Errors: self.errors,
            AdminOperationKey.CurrentView: self.current_view,
            AdminOperationKey.CompletedTime: self.completed_time,
            AdminOperationKey.CreatedTime: self.created_time,
            AdminOperationKey.ObjectData: self.object_data,
            AdminOperationKey.IdsCreated: self.ids_created,
            AdminOperationKey.IdsUpdated: self.ids_updated,
            AdminOperationKey.IdsRemoved: self.ids_removed,
        }



class AgentOper(Base):
    """Used to represent an instance of an admin operation."""

    def __init__(
        self, created_by=None, operation_id=None, action_performed_on=None,
        agents=None, completed_time=None, created_time=None,
        operation=None, operation_status=None, updated_time=None,
        view_name=None, restart=None, tag_id=None, agent_ids=None,
        plugin=None, cpu_throttle=None, net_throttle=None,
        agents_total_count=None, agents_failed_count=None,
        agents_completed_count=None, agents_expired_count=None,
        agents_pending_results_count=None,
        agents_pending_pickup_count=None,
        agents_completed_with_errors_count=None, applications=None
    ):
        """
        Kwargs:
            created_by (str): The name of the user who created the operation.
            operation_id (str): The 36 character UUID of the operation.
            completed_time (int|float): The time this operation was created in epoch.
            created_time (int|float): The time the operation completed in epoch.
            operation (str): install, reboot, shutdown, uninstall, etc...
            operation_status (int): The status of the operation.
            action_performed_on (str): agent or tag.
            updated_time (int|float): The last time this operation was updated in epoch.
            view_name (str): The name of the view, this operation was performed on.
            restart (bool): Whether or not this operation requires a reboot.
            tag_id (str): The 36 character UUID primary key of the tag, this
                operation was performed on.
            agent_ids (list): List of agent ids, this operation was performed on.
            plugin (str): core, rv, vuln, etc... The vFense plugin, this operation
                was performed on.
            cpu_throttle (str): idle, below_normal, normal, above_normal, high
            net_throttle (int): default=0 which equals to unlimitted bandwidth.
                throttleing is done in kb.
            agents_total_count (int): Number of agents invloved in this operation.
            agents_failed_count (int): Number of agents failed in this operation.
            agents_completed_count (int): Number of agents completed this operation.
            agents_expire_count (int): Number of agents, that this operation
                has expired on.
            agents_pending_results_count (int): Number of agents, that this
                operation is pending for results.
            agents_pending_pickup_count (int): Number of agents, that this
                operation is pending to be picked up by the agent.
            agents_completed_with_errors_count (int): Number of agents, that
                this operation failed with some errors.
            applications (list): List of application ids, this operation
                affects.
        """
        self.created_by = created_by
        self.operation_id = operation_id
        self.action_performed_on = action_performed_on
        self.agents = agents
        self.completed_time = completed_time
        self.created_time = created_time
        self.operation = operation
        self.operation_status = operation_status
        self.action_performed_on = action_performed_on
        self.updated_time = updated_time
        self.view_name = view_name
        self.restart = restart
        self.tag_id = tag_id
        self.agent_ids = agent_ids
        self.plugin = plugin
        self.cpu_throttle = cpu_throttle
        self.net_throttle = net_throttle
        self.agents_total_count = agents_total_count
        self.agents_failed_count = agents_failed_count
        self.agents_completed_count = agents_completed_count
        self.agents_expired_count = agents_expired_count
        self.agents_pending_results_count = agents_pending_results_count
        self.agents_pending_pickup_count = agents_pending_pickup_count
        self.agents_completed_with_errors_count = (
            agents_completed_with_errors_count
        )
        self.applications = applications


    def fill_in_defaults(self):
        """Replace all the fields that have None as their value with
        the hardcoded default values.

        Use case(s):
            Useful when creating a new user instance and only want to fill
            in a few fields, then allow the create user functions call this
            method to fill in the rest.
        """
        if not self.updated_time:
            self.updated_time = OperationDefaults.updated_time()

        if not self.completed_time:
            self.completed_time = OperationDefaults.completed_time()

        if not self.agents:
            self.agents = OperationDefaults.agents()

        if not self.agent_ids:
            self.agent_ids = OperationDefaults.agent_ids()

        if not self.cpu_throttle:
            self.cpu_throttle = OperationDefaults.cpu_throttle()

        if not self.net_throttle:
            self.net_throttle = OperationDefaults.net_throttle()

        if not self.agents_total_count:
            self.agents_total_count = OperationDefaults.agents_total_count()

        if not self.agents_failed_count:
            self.agents_failed_count = OperationDefaults.agents_failed_count()

        if not self.agents_completed_count:
            self.agents_completed_count = (
                OperationDefaults.agents_completed_count()
            )

        if not self.agents_expired_count:
            self.agents_expired_count = (
                OperationDefaults.agents_expired_count()
            )

        if not self.agents_pending_results_count:
            self.agents_pending_results_count = (
                OperationDefaults.agents_pending_results_count()
            )

        if not self.agents_pending_pickup_count:
            self.agents_pending_pickup_count = (
                OperationDefaults.agents_pending_pickup_count()
            )

        if not self.agents_completed_with_errors_count:
            self.agents_completed_with_errors_count = (
                OperationDefaults.agents_completed_with_errors_count()
            )

    def get_invalid_fields(self):
        """Check the user for any invalid fields.

        Returns:
            (list): List of key/value pair dictionaries corresponding
                to the invalid fields.

                Ex:
                    [
                        {'view_name': 'the invalid name in question'},
                        {'net_throttle': -10}
                    ]
        """
        invalid_fields = []

        return invalid_fields

    def to_dict(self):
        """ Turn the fields into a dictionary.

        Returns:
            (dict): A dictionary with the fields.
        """

        return {
            AgentOperationKey.CreatedBy: self.created_by,
            AgentOperationKey.PerformedOn: self.action_performed_on,
            AgentOperationKey.CompletedTime: self.completed_time,
            AgentOperationKey.CreatedTime: self.created_time,
            AgentOperationKey.Operation: self.operation,
            AgentOperationKey.OperationStatus: self.operation_status,
            AgentOperationKey.ActionPerformedOn: self.action_performed_on,
            AgentOperationKey.UpdatedTime: self.updated_time,
            AgentOperationKey.ViewName: self.view_name,
            AgentOperationKey.Restart: self.restart,
            AgentOperationKey.TagId: self.tag_id,
            AgentOperationKey.AgentIds: self.agent_ids,
            AgentOperationKey.Plugin: self.plugin,
            AgentOperationKey.CpuThrottle: self.cpu_throttle,
            AgentOperationKey.NetThrottle: self.net_throttle,
            AgentOperationKey.AgentsTotalCount: self.agents_total_count,
            AgentOperationKey.AgentsFailedCount: self.agents_failed_count,
            AgentOperationKey.AgentsCompletedCount: self.agents_completed_count,
            AgentOperationKey.AgentsExpiredCount: self.agents_expired_count,
            AgentOperationKey.AgentsPendingResultsCount: (
                self.agents_pending_results_count
            ),
            AgentOperationKey.AgentsPendingPickUpCount: (
                self.agents_pending_pickup_count
            ),
            AgentOperationKey.AgentsCompletedWithErrorsCount: (
                self.agents_completed_with_errors_count
            ),
            AgentOperationKey.Applications: self.applications,
        }

    def to_dict_db(self):
        """ Turn the fields into a dictionary, with db related fields.

        Returns:
            (dict): A dictionary with the fields.

        """

        data = {
            AgentOperationKey.CreatedTime: (
                DbTime.epoch_time_to_db_time(self.created_time)
            ),
            AgentOperationKey.UpdatedTime: (
                DbTime.epoch_time_to_db_time(self.updated_time)
            ),
            AgentOperationKey.CompletedTime: (
                DbTime.epoch_time_to_db_time(self.completed_time)
            ),
        }

        combined_data = dict(self.to_dict_non_null().items() + data.items())
        return combined_data

    def to_dict_db_updated(self):
        """ Turn the fields into a dictionary, with db related fields.

        Returns:
            (dict): A dictionary with the fields.

        """

        data = {
            AgentOperationKey.UpdatedTime: (
                DbTime.epoch_time_to_db_time(self.updated_time)
            ),
        }

        combined_data = dict(self.to_dict_non_null().items() + data.items())
        return combined_data

    def to_dict_db_completed(self):
        """ Turn the fields into a dictionary, with db related fields.

        Returns:
            (dict): A dictionary with the fields.

        """

        data = {
            AgentOperationKey.CompletedTime: (
                DbTime.epoch_time_to_db_time(self.completed_time)
            ),
        }

        combined_data = dict(self.to_dict_non_null().items() + data.items())
        return combined_data


class OperPerAgent(Base):
    """Used to represent an instance of an admin operation."""

    def __init__(
        self, operation_id=None, agent_id=None, picked_up_time=None, id=None,
        expired_time=None, completed_time=None, view_name=None, status=None,
        tag_id=None, errors=None, apps_total_count=0, apps_pending_count=0,
        apps_failed_count=0, apps_completed_count=0
    ):
        """
        Kwargs:
            agent_id (str): The 36 character UUID primary key of the agent, this
                operation was performed on.
            operation_id (str): The 36 character UUID of the operation.
            picked_up_time (int|float): The time the operation was picked up
                by the agent in epoch.
            expired_time (int|float): The time the operation was expired
                by the agent in epoch.
            completed_time (int|float): The time this operation was created in epoch.
            view_name (str): The name of the view, this operation was performed on.
            status (int): The status of the operation.
            tag_id (str): The 36 character UUID primary key of the tag, this
                operation was performed on.
            errors (list): List of error messages.
            apps_total_count (int): Number of applications to be installed or
                uninstalled on this agent.
            apps_pending_count (int): Number of applications still pending
                results from the agent.
            apps_failed_count (int): Number of applications that failed
                to either install or uninstall on this agent.
            apps_completed_count (int): Number of applications that were
                successfully installed.
        """
        self.id = id
        self.operation_id = operation_id
        self.agent_id = agent_id
        self.picked_up_time = picked_up_time
        self.expired_time = expired_time
        self.completed_time = completed_time
        self.view_name = view_name
        self.status = status
        self.tag_id = tag_id
        self.errors = errors
        self.apps_total_count = apps_total_count
        self.apps_pending_count = apps_pending_count
        self.apps_failed_count = apps_failed_count
        self.apps_completed_count = apps_completed_count


    def fill_in_defaults(self):
        """Replace all the fields that have None as their value with
        the hardcoded default values.

        Use case(s):
            Useful when creating a new user instance and only want to fill
            in a few fields, then allow the create user functions call this
            method to fill in the rest.
        """
        if not self.picked_up_time:
            self.picked_up_time = OperPerAgentDefaults.picked_up_time()

        if not self.expired_time:
            self.expired_time = OperPerAgentDefaults.expired_time()

        if not self.completed_time:
            self.completed_time = OperPerAgentDefaults.completed_time()

        if not self.errors:
            self.errors = OperPerAgentDefaults.errors()

        if not self.apps_total_count:
            self.apps_total_count = OperPerAgentDefaults.apps_total_count()

        if not self.apps_pending_count:
            self.apps_pending_count = OperPerAgentDefaults.apps_pending_count()

        if not self.apps_failed_count:
            self.apps_failed_count = OperPerAgentDefaults.apps_failed_count()

        if not self.apps_completed_count:
            self.apps_completed_count = (
                OperPerAgentDefaults.apps_completed_count()
            )

    def get_invalid_fields(self):
        """Check the user for any invalid fields.

        Returns:
            (list): List of key/value pair dictionaries corresponding
                to the invalid fields.

                Ex:
                    [
                        {'view_name': 'the invalid name in question'},
                        {'net_throttle': -10}
                    ]
        """
        invalid_fields = []

        return invalid_fields

    def to_dict(self):
        """ Turn the fields into a dictionary.

        Returns:
            (dict): A dictionary with the fields.
        """

        return {
            OperationPerAgentKey.OperationId: self.operation_id,
            OperationPerAgentKey.AgentId: self.agent_id,
            OperationPerAgentKey.CompletedTime: self.completed_time,
            OperationPerAgentKey.PickedUpTime: self.picked_up_time,
            OperationPerAgentKey.ExpiredTime: self.expired_time,
            OperationPerAgentKey.ViewName: self.view_name,
            OperationPerAgentKey.TagId: self.tag_id,
            OperationPerAgentKey.Errors: self.errors,
            OperationPerAgentKey.Status: self.status,
            OperationPerAgentKey.AppsTotalCount: self.agents_total_count,
            OperationPerAgentKey.AppsPendingCount: self.apps_pending_count,
            OperationPerAgentKey.AppsFailedCount: self.apps_failed_count,
            OperationPerAgentKey.AppsCompletedCount: self.apps_completed_count,
        }

    def to_dict_db(self):
        """ Turn the fields into a dictionary, with db related fields.

        Returns:
            (dict): A dictionary with the fields.

        """

        data = {
            OperationPerAgentKey.PickedUpTime: (
                DbTime.epoch_time_to_db_time(self.picked_up_time)
            ),
            OperationPerAgentKey.ExpiredTime: (
                DbTime.epoch_time_to_db_time(self.expired_time)
            ),
            OperationPerAgentKey.CompletedTime: (
                DbTime.epoch_time_to_db_time(self.completed_time)
            ),
        }

        combined_data = dict(self.to_dict_non_null().items() + data.items())
        return combined_data

    def to_dict_db_updated(self):
        """ Turn the fields into a dictionary, with db related fields.

        Returns:
            (dict): A dictionary with the fields.

        """
        data = self.to_dict_non_null()
        if data.get(OperationPerAgentKey.PickedUpTime, None):
            data[OperationPerAgentKey.PickedUpTime] = (
                DbTime.epoch_time_to_db_time(self.picked_up_time)
            )

        if data.get(OperationPerAgentKey.ExpiredTime, None):
            data[OperationPerAgentKey.ExpiredTime] = (
                DbTime.epoch_time_to_db_time(self.expired_time)
            )

        if data.get(OperationPerAgentKey.CompletedTime, None):
            data[OperationPerAgentKey.CompletedTime] = (
                DbTime.epoch_time_to_db_time(self.completed_time)
            )

        return data

class OperPerApp(Base):
    """Used to represent an instance of an operation per app."""

    def __init__(
        self, operation_id=None, agent_id=None, app_id=None, id=None,
        app_name=None, app_version=None, apps_removed=None, view_name=None,
        results=None, results_received_time=None, errors=None
    ):
        """
        Kwargs:
            operation_id (str): The 36 character UUID of the operation.
            agent_id (str): The 36 character UUID primary key of the agent, this
                operation was performed on.
            app_id (str): the 64 character hexdigest application id.
            app_name (str): The name of the application.
            app_version (str): The version of the application.
            apps_removed (list): List of applications removed.
            view_name (str): The name of the view, this operation was performed on.
            results (list): List of results.
            results_received_time (int|float): The time the results of the
                application was returnd by the agent in epoch.
            errors (list): List of error messages.
        """
        self.id = id
        self.operation_id = operation_id
        self.agent_id = agent_id
        self.app_id = app_id
        self.app_name = app_name
        self.app_version = app_version
        self.apps_removed = apps_removed
        self.view_name = view_name
        self.results = results
        self.results_received_time = results_received_time
        self.errors = errors


    def fill_in_defaults(self):
        """Replace all the fields that have None as their value with
        the hardcoded default values.

        Use case(s):
            Useful when creating a new user instance and only want to fill
            in a few fields, then allow the create user functions call this
            method to fill in the rest.
        """
        if not self.results_received_time:
            self.results_received_time = (
                OperPerAppDefaults.results_received_time()
            )

        if not self.apps_removed:
            self.apps_removed = OperPerAppDefaults.apps_removed()

        if not self.errors:
            self.errors = OperPerAppDefaults.errors()

        if not self.results:
            self.results = OperPerAppDefaults.results()


    def get_invalid_fields(self):
        """Check the user for any invalid fields.

        Returns:
            (list): List of key/value pair dictionaries corresponding
                to the invalid fields.

                Ex:
                    [
                        {'view_name': 'the invalid name in question'},
                        {'net_throttle': -10}
                    ]
        """
        invalid_fields = []

        return invalid_fields

    def to_dict(self):
        """ Turn the fields into a dictionary.

        Returns:
            (dict): A dictionary with the fields.
        """

        return {
            OperationPerAppKey.OperationId: self.operation_id,
            OperationPerAppKey.AgentId: self.agent_id,
            OperationPerAppKey.ResultsReceivedTime: self.results_received_time,
            OperationPerAppKey.ViewName: self.view_name,
            OperationPerAppKey.AppName: self.app_name,
            OperationPerAppKey.AppsRemoved: self.apps_removed,
            OperationPerAppKey.AppVersion: self.app_version,
            OperationPerAppKey.AppId: self.app_id,
            OperationPerAppKey.Results: self.results,
            OperationPerAppKey.Errors: self.errors,
        }

    def to_dict_db(self):
        """ Turn the fields into a dictionary, with db related fields.

        Returns:
            (dict): A dictionary with the fields.

        """

        data = {
            OperationPerAppKey.ResultsReceivedTime: (
                DbTime.epoch_time_to_db_time(self.results_received_time)
            ),
        }

        combined_data = dict(self.to_dict_non_null().items() + data.items())
        return combined_data
