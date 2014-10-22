import re
from vFense import Base
from vFense.core.user._db_model import UserKeys
from vFense.core._constants import (
    RegexPattern, DefaultStringLength, CommonKeys
)
from vFense.core.user._constants import UserDefaults
from vFense.core.results import ApiResultKeys
from vFense.core.user.status_codes import UserFailureCodes, UserCodes
from vFense.utils.security import check_password


class User(Base):
    """Used to represent an instance of a user."""

    def __init__(
            self, username=None, password=None, full_name=None, email=None,
            current_view=None, default_view=None, enabled=None,
            is_global=None, **kwargs
    ):
        """
        Args:
            username (str): The name of the user.

        Kwargs:
            password (str): The users password.
            full_name (str): The full name of the user.
            email (str): The email of the user.
            current_view (str): The view you are currently logged into.
            default_view (str): The default view of the user.
            enabled (boolean): Disable or enable this user.
            is_global (boolean):Is this user a global user.
        """
        super(User, self).__init__(**kwargs)
        self.username = username
        self.full_name = full_name
        self.email = email
        self.password = password
        self.current_view = current_view
        self.default_view = default_view
        self.enabled = enabled
        self.is_global = is_global


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

        if isinstance(self.username, basestring):
            valid_symbols = re.search(
                RegexPattern.USERNAME, self.username
            )
            valid_length = len(self.username) <= DefaultStringLength.USER_NAME

            if not valid_symbols and valid_length:
                invalid_fields.append(
                    {
                        UserKeys.UserName: self.username,
                        CommonKeys.REASON: 'Invalid characters in username',
                        ApiResultKeys.VFENSE_STATUS_CODE: (
                            UserFailureCodes.InvalidUserName
                        )
                    }
                )
            elif not valid_length and valid_symbols:
                invalid_fields.append(
                    {
                        UserKeys.UserName: self.username,
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
                        UserKeys.UserName: self.username,
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
                    UserKeys.UserName: self.username,
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
                            UserCodes.InvalidValue
                        )
                    }
                )

        if self.is_global:
            if not isinstance(self.is_global, bool):
                invalid_fields.append(
                    {
                        UserKeys.IsGlobal: self.is_global,
                        CommonKeys.REASON: 'Must be a boolean value',
                        ApiResultKeys.VFENSE_STATUS_CODE: (
                            UserCodes.InvalidValue
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
            UserKeys.UserName: self.username,
            UserKeys.CurrentView: self.current_view,
            UserKeys.DefaultView: self.default_view,
            UserKeys.Password: self.password,
            UserKeys.FullName: self.full_name,
            UserKeys.Email: self.email,
            UserKeys.IsGlobal: self.is_global,
            UserKeys.Enabled: self.enabled
        }
