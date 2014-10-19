import re
from vFense import Base
from vFense.core.group._constants import GroupDefaults
from vFense.core.permissions._constants import Permissions
from vFense.core.results import ApiResultKeys
from vFense.core.group.status_codes import (
    GroupCodes, GroupFailureCodes
)
from vFense.core._constants import (
    CommonKeys, DefaultStringLength, RegexPattern
)
from vFense.core.group._db_model import (
    GroupKeys
)

#from vFense.core.view.views import validate_view_names

class Group(Base):
    """Used to represent an instance of a group."""

    def __init__(
            self, group_name=None, permissions=None,
            views=None, is_global=None, users=None, email=None,
            group_id=None
        ):
        """
        Kwargs:
            group_name (str): The name of the group.
            permissions (list): List of valid permissions.
            views (list): List of views, this group is a part of.
            users (list): List of users in this group.
            is_global (boolean): Is this group a global group.
            email (str): The group email address.
            group_id (str): The 36 character UUID of the group.
        """
        self.group_name = group_name
        self.permissions = permissions
        self.views = views
        self.is_global = is_global
        self.users = users
        self.email = email
        self.group_id = group_id


    def fill_in_defaults(self):
        """Replace all the fields that have None as their value with
        the hardcoded default values.

        Use case(s):
            Useful when creating a new group instance and only want to fill
            in a few fields, then allow the create user functions call this
            method to fill in the rest.
        """

        if not self.permissions:
            self.permissions = GroupDefaults.PERMISSIONS

        if not self.views:
            self.views = GroupDefaults.VIEWS

        if not self.users:
            self.users = GroupDefaults.USERS

        if not self.is_global:
            self.is_global = GroupDefaults.IS_GLOBAL

        if not self.email:
            self.email = GroupDefaults.EMAIL

    def get_invalid_fields(self):
        """Check the group for any invalid fields.

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
        if self.group_name:
            if isinstance(self.group_name, basestring):
                valid_symbols = re.search(
                    RegexPattern.GROUP_NAME, self.group_name
                )
                valid_length = (
                    len(self.group_name) <= DefaultStringLength.GROUP_NAME
                )

                if not valid_symbols and valid_length:
                    invalid_fields.append(
                        {
                            GroupKeys.GroupName: self.group_name,
                            CommonKeys.REASON: (
                                'Invalid characters in group name'
                            ),
                            ApiResultKeys.VFENSE_STATUS_CODE: (
                                GroupFailureCodes.InvalidGroupName
                            )
                        }
                    )

                elif not valid_length and valid_symbols:
                    invalid_fields.append(
                        {
                            GroupKeys.UserName: self.group_name,
                            CommonKeys.REASON: (
                                'Groupname is too long. ' +
                                'The groupname must be ' +
                                'less than %d characters long' %
                                (DefaultStringLength.GROUP_NAME)
                            ),
                            ApiResultKeys.VFENSE_STATUS_CODE: (
                                GroupFailureCodes.InvalidGroupName
                            )
                        }
                    )

                elif not valid_length and not valid_symbols:
                    invalid_fields.append(
                        {
                            GroupKeys.GroupName: self.group_name,
                            CommonKeys.REASON: (
                                'Groupname is too long. ' +
                                'The groupname must be ' +
                                'less than %d characters long' %
                                (DefaultStringLength.GROUP_NAME) +
                                '\nInvalid characters in groupname'
                            ),
                            ApiResultKeys.VFENSE_STATUS_CODE: (
                                GroupFailureCodes.InvalidGroupName
                            )
                        }
                    )

        if self.is_global:
            if not isinstance(self.is_global, bool):
                invalid_fields.append(
                    {
                        GroupKeys.IsGlobal: self.is_global,
                        CommonKeys.REASON: 'Must be a boolean value',
                        ApiResultKeys.VFENSE_STATUS_CODE: (
                            GroupCodes.InvalidValue
                        )
                    }
                )

        if self.permissions:
            if not isinstance(self.permissions, list):
                invalid_fields.append(
                    {
                        GroupKeys.Permissions: self.permissions,
                        CommonKeys.REASON: 'Must be a list of permissions',
                        ApiResultKeys.VFENSE_STATUS_CODE: (
                            GroupCodes.InvalidValue
                        )
                    }
                )

            else:
                if not (
                        set(self.permissions).issubset(
                            set(Permissions.get_valid_permissions())
                        )):
                    invalid_fields.append(
                        {
                            GroupKeys.Permissions: self.permissions,
                            CommonKeys.REASON: 'Invalid permissions',
                            ApiResultKeys.VFENSE_STATUS_CODE: (
                                GroupCodes.InvalidValue
                            )
                        }
                    )

        if self.views:
            if not isinstance(self.views, list):
                invalid_fields.append(
                    {
                        GroupKeys.Views: self.views,
                        CommonKeys.REASON: 'Must be a list of views',
                        ApiResultKeys.VFENSE_STATUS_CODE: (
                            GroupCodes.InvalidValue
                        )
                    }
                )

        if self.users:
            if not isinstance(self.users, list):
                invalid_fields.append(
                    {
                        GroupKeys.Users: self.users,
                        CommonKeys.REASON: 'Must be a list of usernames',
                        ApiResultKeys.VFENSE_STATUS_CODE: (
                            GroupCodes.InvalidValue
                        )
                    }
                )

        return invalid_fields

    def to_dict(self):
        """ Turn the group fields into a dictionary.

        Returns:
            (dict): A dictionary with the fields.
        """

        return {
            GroupKeys.GroupName: self.group_name,
            GroupKeys.IsGlobal: self.is_global,
            GroupKeys.Permissions: self.permissions,
            GroupKeys.Views: self.views,
            GroupKeys.Users: self.users,
            GroupKeys.Email: self.email,
        }
