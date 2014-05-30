import logging
from vFense import VFENSE_LOGGING_CONFIG
from vFense.core.decorators import time_it
from vFense.errorz._constants import ApiResultKeys
from vFense.errorz.status_codes import (
    GroupCodes, GenericCodes, GenericFailureCodes,
    GroupFailureCodes, DbCodes
)
from vFense.core.group._db import (
    fetch_group,fetch_usernames_in_group
)

logging.config.fileConfig(VFENSE_LOGGING_CONFIG)
logger = logging.getLogger('rvapi')

class GroupManager(object):
    def __init__(self, group_id):
        self.group_id = group_id
        self.properties = self._group_attributes()
        self.users = self._users()

    @time_it
    def _group_attributes(self):
        """Retrieve a group from the database
        Basic Usage:
            >>> from vFense.group.groups import get_group
            >>> group_id = '8757b79c-7321-4446-8882-65457f28c78b'
            >>> get_group(group_id)

        Returns:
             Returns a Dict of the properties of a group
            {
                u'group_name': u'Administrator',
                u'customer_name': u'default',
                u'id': u'8757b79c-7321-4446-8882-65457f28c78b',
                u'Permissions': [
                    u'administrator'
               ]
            }
        """
        data = fetch_group(self.group_id)
        return data

    @time_it
    def _users(self):
        """Retrieve a group from the database
        Basic Usage:
            >>> from vFense.group.groups import get_group
            >>> group_id = '8757b79c-7321-4446-8882-65457f28c78b'
            >>> get_group(group_id)

        Returns:
             Returns a Dict of the properties of a group
            {
                u'group_name': u'Administrator',
                u'customer_name': u'default',
                u'id': u'8757b79c-7321-4446-8882-65457f28c78b',
                u'Permissions': [
                    u'administrator'
               ]
            }
        """
        data = fetch_usernames_in_group(self.group_id)
        return data

    @time_it
    def create_group(
            group_name, view_name, permissions, is_global=False,
            user_name=None, uri=None, method=None
        ):
        """Create a group in vFense
        Args:
            group_name (str): The name of the group.
            view_name (str): The name of the view you are adding this group too.
            permissions (list): List of permissions, this group has.

        Kwargs:
            is_global (bool): Global group or local to the view.
                default = False

        Basic Usage:
            >>> from vFense.group.groups import create_group
            >>> group_name = 'Linux Admins'
            >>> view_name = 'default'
            >>> permissions = ['administrator']
            >>> create_group(group_name, view_name, permissions)

        Returns:
            Returns the results in a dictionary
            {
                'rv_status_code': 1010,
                'message': "None - create group [u'8757b79c-7321-4446-8882-65457f28c78b'] was created",
                'data': {
                    'Permissions': [
                        'administrator'
                    ],
                    'group_name': 'Linux Admins',
                    'view_name': 'default'
                }
            }
        """

        status = create_group.func_name + ' - '
        generated_ids = []
        valid_group_name = (
            re.search(RegexPattern.GROUP_NAME, group_name)
        )
        valid_group_length = (
            len(group_name) <= DefaultStringLength.GROUP_NAME
        )
        group_data = (
            {
                GroupKeys.ViewName: view_name,
                GroupKeys.Views: [view_name],
                GroupKeys.GroupName: group_name,
                GroupKeys.Permissions: permissions,
                GroupKeys.Global: is_global,
            }
        )
        group_exist = fetch_group_by_name(group_name, view_name)
        permissions_valid = (
            set(permissions).issubset(set(Permissions.VALID_PERMISSIONS))
        )
        if (not group_exist and permissions_valid and
            valid_group_length and valid_group_name):

            status_code, status_count, error, generated_ids = (
                insert_group(group_data)
            )

            if status_code == DbCodes.Inserted:
                msg = 'group %s created' % (group_name)
                generic_status_code = GenericCodes.ObjectCreated
                vfense_status_code = GroupCodes.GroupCreated

        elif not group_exist and not permissions_valid:
            msg = 'invalid permissions %s' % (permissions)
            status_code = DbCodes.Errors
            generic_status_code = GenericCodes.InvalidPermission
            vfense_status_code = GroupFailureCodes.InvalidPermissions


        elif group_exist:
            msg = 'group %s exists' % (group_name)
            status_code = DbCodes.Unchanged
            generic_status_code = GenericCodes.ObjectExists
            vfense_status_code = GroupFailureCodes.GroupIdExists


        elif not valid_group_length or not valid_group_name:
            status_code = DbCodes.Errors
            msg = (
                'group name is not within the 36 character range '+
                'or contains unsupported characters :%s' %
                (group_name)
            )
            generic_status_code = GenericCodes.InvalidId
            vfense_status_code = GroupFailureCodes.InvalidGroupName

        results = {
            ApiResultKeys.DB_STATUS_CODE: status_code,
            ApiResultKeys.GENERIC_STATUS_CODE: generic_status_code,
            ApiResultKeys.VFENSE_STATUS_CODE: vfense_status_code,
            ApiResultKeys.GENERATED_IDS: generated_ids,
            ApiResultKeys.MESSAGE: status + msg,
            ApiResultKeys.DATA: group_data,
            ApiResultKeys.USERNAME: user_name,
            ApiResultKeys.URI: uri,
            ApiResultKeys.HTTP_METHOD: method
        }

        return results

