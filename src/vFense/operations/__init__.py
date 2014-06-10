import re
from vFense.operations._db_model import (
    AdminOperationKey
)
from vFense.errorz._constants import ApiResultKeys
from vFense.errorz.status_codes import UserFailureCodes, GenericCodes
class AdminOperation(object):
    """Used to represent an instance of a user."""

    def __init__(
        self, operation_id=None, created_by=None, action=None,
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

        if not self.full_name:
            self.full_name = UserDefaults.FULL_NAME

        if not self.email:
            self.email = UserDefaults.EMAIL

        if not self.enabled:
            self.enabled = UserDefaults.ENABLED

        if not self.is_global:
            self.is_global = UserDefaults.IS_GLOBAL

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

        if isinstance(self.name, basestring):
            valid_symbols = re.search(
                RegexPattern.USERNAME, self.name
            )
            valid_length = len(self.name) <= DefaultStringLength.USER_NAME

            if not valid_symbols and valid_length:
                invalid_fields.append(
                    {
                        UserKeys.UserName: self.name,
                        CommonKeys.REASON: 'Invalid characters in username',
                        ApiResultKeys.VFENSE_STATUS_CODE: (
                            UserFailureCodes.InvalidUserName
                        )
                    }
                )
            elif not valid_length and valid_symbols:
                invalid_fields.append(
                    {
                        UserKeys.UserName: self.name,
                        CommonKeys.REASON: (
                            'Username is too long. The username must be ' +
                            'less than %d characters long' %
                            (DefaultStringLength.USER_NAME)
                        ),
                        ApiResultKeys.VFENSE_STATUS_CODE: (
                            UserFailureCodes.InvalidUserName
                        )
                    }
                )
            elif not valid_length and not valid_symbols:
                invalid_fields.append(
                    {
                        UserKeys.UserName: self.name,
                        CommonKeys.REASON: (
                            'Username is too long. The username must be ' +
                            'less than %d characters long' %
                            (DefaultStringLength.USER_NAME) +
                            '\nInvalid characters in username'
                        ),
                        ApiResultKeys.VFENSE_STATUS_CODE: (
                            UserFailureCodes.InvalidUserName
                        )
                    }
                )
        else:
            invalid_fields.append(
                {
                    UserKeys.UserName: self.name,
                    CommonKeys.REASON: 'username is not a valid string',
                    ApiResultKeys.VFENSE_STATUS_CODE: (
                        UserFailureCodes.InvalidUserName
                    )
                }
            )

        if self.enabled:
            if not isinstance(self.enabled, bool):
                invalid_fields.append(
                    {
                        UserKeys.Enabled: self.enabled,
                        CommonKeys.REASON: 'Must be a boolean value',
                        ApiResultKeys.VFENSE_STATUS_CODE: (
                            GenericCodes.InvalidValue
                        )
                    }
                )

        if self.is_global:
            if not isinstance(self.is_global, bool):
                invalid_fields.append(
                    {
                        UserKeys.Global: self.is_global,
                        CommonKeys.REASON: 'Must be a boolean value',
                        ApiResultKeys.VFENSE_STATUS_CODE: (
                            GenericCodes.InvalidValue
                        )
                    }
                )

        if self.password and isinstance(self.password, basestring):
            valid_passwd, _ = check_password(self.password)
            if not valid_passwd:
                invalid_fields.append(
                    {
                        UserKeys.Password: self.password,
                        CommonKeys.REASON: (
                            'Password does not meet the minimum requirements'
                        ),
                        ApiResultKeys.VFENSE_STATUS_CODE: (
                            UserFailureCodes.InvalidPassword
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
            UserKeys.UserName: self.name,
            UserKeys.CurrentView: self.current_view,
            UserKeys.DefaultView: self.default_view,
            UserKeys.Password: self.password,
            UserKeys.FullName: self.full_name,
            UserKeys.Email: self.email,
            UserKeys.Global: self.is_global,
            UserKeys.Enabled: self.enabled
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
