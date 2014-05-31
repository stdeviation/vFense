import re
from vFense.core.group._constants import GroupDefaults
from vFense.core.permissions._constants import Permissions
from vFense.errorz._constants import ApiResultKeys
from vFense.errorz.status_codes import (
    GenericCodes, GroupFailureCodes
)
from vFense.core._constants import (
    CommonKeys, DefaultStringLength, RegexPattern
)
from vFense.core.group._db_model import (
    GroupKeys
)

from vFense.core.view._db import (
    fetch_all_view_names
)

from vFense.core.view.views import (
    validate_view_names
)

class Group(object):
    """Used to represent an instance of a group."""

    def __init__(
            self, name, permissions=None,
            views=None, is_global=None
        ):
        """
        Kwargs:
            name (str): The name of the group.
            permissions (list): List of valid permissions.
            views (list): List of views.
            is_global (boolean): Is this group a global group.
            restricted (boolean): Is this a restricted group for a view.
        """
        self.name = name
        self.permissions = permissions
        self.views = views
        self.is_global = is_global


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

        if not self.is_global:
            self.is_global = GroupDefaults.IS_GLOBAL

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

        if isinstance(self.name, basestring):
            valid_symbols = re.search(
                RegexPattern.GROUP_NAME, self.name
            )
            valid_length = len(self.name) <= DefaultStringLength.GROUP_NAME

            if not valid_symbols and valid_length:
                invalid_fields.append(
                    {
                        GroupKeys.UserName: self.name,
                        CommonKeys.REASON: 'Invalid characters in username',
                        ApiResultKeys.VFENSE_STATUS_CODE: (
                            GroupFailureCodes.InvalidGroupName
                        )
                    }
                )

            elif not valid_length and valid_symbols:
                invalid_fields.append(
                    {
                        GroupKeys.UserName: self.name,
                        CommonKeys.REASON: (
                            'Groupname is too long. The groupname must be ' +
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
                        GroupKeys.UserName: self.name,
                        CommonKeys.REASON: (
                            'Groupname is too long. The groupname must be ' +
                            'less than %d characters long' %
                            (DefaultStringLength.GROUP_NAME) +
                            '\nInvalid characters in groupname'
                        ),
                        ApiResultKeys.VFENSE_STATUS_CODE: (
                            GroupFailureCodes.InvalidGroupName
                        )
                    }
                )
        else:
            invalid_fields.append(
                {
                    GroupKeys.GroupName: self.name,
                    CommonKeys.REASON: 'groupname is not a valid string',
                    ApiResultKeys.VFENSE_STATUS_CODE: (
                        GroupFailureCodes.InvalidGroupName
                    )
                }
            )

        if self.is_global:
            if not isinstance(self.is_global, bool):
                invalid_fields.append(
                    {
                        GroupKeys.Global: self.is_global,
                        CommonKeys.REASON: 'Must be a boolean value',
                        ApiResultKeys.VFENSE_STATUS_CODE: (
                            GenericCodes.InvalidValue
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
                            GenericCodes.InvalidValue
                        )
                    }
                )

            else:
                if self.permissions not in Permissions.VALID_PERMISSIONS:
                    invalid_fields.append(
                        {
                            GroupKeys.Permissions: self.permissions,
                            CommonKeys.REASON: 'Invalid permissions',
                            ApiResultKeys.VFENSE_STATUS_CODE: (
                                GenericCodes.InvalidValue
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
                            GenericCodes.InvalidValue
                        )
                    }
                )

            else:
                valid_views, _, _ = validate_view_names(self.views)
                if not valid_views:
                    invalid_fields.append(
                        {
                            GroupKeys.Views: self.views,
                            CommonKeys.REASON: 'Invalid views',
                            ApiResultKeys.VFENSE_STATUS_CODE: (
                                GenericCodes.InvalidValue
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
                }

        """

        return {
            GroupKeys.GroupName: self.name,
            GroupKeys.Global: self.is_global,
            GroupKeys.Permissions: self.permissions,
            GroupKeys.Views: self.views,
        }

    def to_dict_non_null(self):
        """ Use to get non None fields of view. Useful when
        filling out just a few fields to update the view in the db.

        Returns:
            (dict): a dictionary with the non None fields of this view.
        """
        group_dict = self.to_dict()

        return {k:group_dict[k] for k in group_dict
                if group_dict[k] != None}
