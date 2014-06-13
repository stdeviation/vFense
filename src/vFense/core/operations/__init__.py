import re
from vFense.core.operations._db_model import (
    AdminOperationKey
)
from vFense.core.operations._admin_constants import (
    AdminOperationDefaults, AdminActions
)
from vFense.core._constants import CommonKeys
from vFense.errorz._constants import ApiResultKeys
from vFense.errorz.status_codes import UserFailureCodes, GenericCodes
from vFense.errorz.status_codes import (
    GenericFailureCodes
)

class AdminOperation(object):
    """Used to represent an instance of an admin operation."""

    def __init__(
        self, created_by=None, action=None,
        performed_on=None, status_message=None, generic_status_code=None,
        vfense_status_code=None, errors=None, current_view=None,
        completed_time=None, created_time=None, object_data=None,
        ids_created=None, ids_updated=None, ids_removed=None
    ):
        """
        Kwargs:
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
            self.ids_updated = AdminOperationDefaults.IDS_UPDATED

        if not self.ids_created:
            self.ids_created = AdminOperationDefaults.IDS_CREATED

        if not self.ids_removed:
            self.ids_removed = AdminOperationDefaults.IDS_REMOVED

        if not self.errors:
            self.errors = AdminOperationDefaults.ERRORS

        if not self.object_data:
            self.object_data = AdminOperationDefaults.OBJECT_DATA

        if not self.bject_data:
            self.object_data = AdminOperationDefaults.OBJECT_DATA

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

        if self.object_data:
            if not isinstance(self.object_data, list):
                invalid_fields.append(
                    {
                        AdminOperationKey.ObjectData: self.object_data,
                        CommonKeys.REASON: (
                            'Expecting a list and not a %s' %
                            (type(self.object_data))
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
        """ Turn the view fields into a dictionary.

        Returns:
            (dict): A dictionary with the fields corresponding to the
                view.

                Ex:
                {
                    "agent_queue_ttl": 100 ,
                    "cpu_throttle":  "high" ,
                    "view_name":  "default" ,
                    "net_throttle": 100 ,
                    "package_download_url_base": https://192.168.8.14/packages/,
                    "server_queue_ttl": 100
                }

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

    def to_dict_non_null(self):
        """ Use to get non None fields of view. Useful when
        filling out just a few fields to update the view in the db.

        Returns:
            (dict): a dictionary with the non None fields of this view.
        """
        user_dict = self.to_dict()

        return {k:user_dict[k] for k in user_dict
                if user_dict[k] != None}
