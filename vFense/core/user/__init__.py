import re
from time import time
from vFense import Base
from vFense.core._db_constants import DbTime
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
            self, user_name=None, password=None, full_name=None, email=None,
            current_view=None, default_view=None, enabled=None,
            is_global=None, views=None, date_added=None, date_modified=None,
            **kwargs
    ):
        """
        Args:
            user_name (str): The name of the user.

        Kwargs:
            password (str): The users password.
            full_name (str): The full name of the user.
            email (str): The email of the user.
            current_view (str): The view you are currently logged into.
            default_view (str): The default view of the user.
            enabled (boolean): Disable or enable this user.
            is_global (boolean): Is this user a global user.
            views (list): List of views this user belongs too.
            date_added (epoch_time): time in epoch.
            date_modified (epoch_time): time in epoch.
        """
        super(User, self).__init__(**kwargs)
        self.user_name = user_name
        self.full_name = full_name
        self.email = email
        self.password = password
        self.current_view = current_view
        self.default_view = default_view
        self.enabled = enabled
        self.is_global = is_global
        self.views = views
        self.date_added = date_added
        self.date_modified = date_modified


    def fill_in_defaults(self):
        """Replace all the fields that have None as their value with
        the hardcoded default values.

        Use case(s):
            Useful when creating a new user instance and only want to fill
            in a few fields, then allow the create user functions call this
            method to fill in the rest.
        """
        now = time()

        if not self.full_name:
            self.full_name = UserDefaults.full_name()

        if not self.email:
            self.email = UserDefaults.email()

        if not self.enabled:
            self.enabled = UserDefaults.enabled()

        if not self.is_global:
            self.is_global = UserDefaults.is_global()

        if not self.views:
            self.views = UserDefaults.views()

        if not self.date_added:
            self.date_added = now

        if not self.date_modified:
            self.date_modified = now

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

        if isinstance(self.user_name, basestring):
            valid_symbols = re.search(
                RegexPattern.USERNAME, self.user_name
            )
            valid_length = len(self.user_name) <= DefaultStringLength.USER_NAME

            if not valid_symbols and valid_length:
                invalid_fields.append(
                    {
                        UserKeys.UserName: self.user_name,
                        CommonKeys.REASON: 'Invalid characters in user_name',
                        ApiResultKeys.VFENSE_STATUS_CODE: (
                            UserFailureCodes.Invaliduser_name
                        )
                    }
                )
            elif not valid_length and valid_symbols:
                invalid_fields.append(
                    {
                        UserKeys.user_name: self.user_name,
                        CommonKeys.REASON: (
                            'user_name is too long. The user_name must be ' +
                            'less than %d characters long' %
                            (DefaultStringLength.USER_NAME)
                        ),
                        ApiResultKeys.VFENSE_STATUS_CODE: (
                            UserFailureCodes.Invaliduser_name
                        )
                    }
                )
            elif not valid_length and not valid_symbols:
                invalid_fields.append(
                    {
                        UserKeys.user_name: self.user_name,
                        CommonKeys.REASON: (
                            'user_name is too long. The user_name must be ' +
                            'less than %d characters long' %
                            (DefaultStringLength.USER_NAME) +
                            '\nInvalid characters in user_name'
                        ),
                        ApiResultKeys.VFENSE_STATUS_CODE: (
                            UserFailureCodes.Invaliduser_name
                        )
                    }
                )
        else:
            invalid_fields.append(
                {
                    UserKeys.user_name: self.user_name,
                    CommonKeys.REASON: 'user_name is not a valid string',
                    ApiResultKeys.VFENSE_STATUS_CODE: (
                        UserFailureCodes.Invaliduser_name
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
        if self.views:
            if not isinstance(self.views, list):
                invalid_fields.append(
                    {
                        UserKeys.Views: self.views,
                        CommonKeys.REASON: (
                            'Invalid type in views {0}'
                            .format(type(self.views))
                        ),
                        ApiResultKeys.VFENSE_STATUS_CODE: (
                            UserFailureCodes.InvalidInstanceType
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
            UserKeys.UserName: self.user_name,
            UserKeys.CurrentView: self.current_view,
            UserKeys.DefaultView: self.default_view,
            UserKeys.Password: self.password,
            UserKeys.FullName: self.full_name,
            UserKeys.Email: self.email,
            UserKeys.IsGlobal: self.is_global,
            UserKeys.Enabled: self.enabled,
            UserKeys.Views: self.views,
            UserKeys.DateAdded: self.date_added,
            UserKeys.DateModified: self.date_modified,
        }

    def to_dict_db(self):
        """ Turn the fields into a dictionary, with db related fields.

        Returns:
            (dict): A dictionary with the fields.

        """
        data = {
            UserKeys.DateAdded: (
                DbTime.epoch_time_to_db_time(self.date_added)
            ),
            UserKeys.DateModified: (
                DbTime.epoch_time_to_db_time(self.date_modified)
            ),
        }

        combined_data = dict(self.to_dict_non_null().items() + data.items())
        return combined_data

    def to_dict_db_update(self):
        """ Turn the fields into a dictionary, with db related fields.

        Returns:
            (dict): A dictionary with the fields.

        """
        if not self.date_modified:
            self.date_modified = time()

        data = {
            UserKeys.DateModified: (
                DbTime.epoch_time_to_db_time(self.date_modified)
            ),
        }

        combined_data = dict(self.to_dict_non_null().items() + data.items())
        combined_data.pop(UserKeys.UserName, None)
        return combined_data
