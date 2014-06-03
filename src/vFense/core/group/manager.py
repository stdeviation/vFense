import logging
from vFense import VFENSE_LOGGING_CONFIG
from vFense.core.decorators import time_it
from vFense.errorz._constants import ApiResultKeys
from vFense.errorz.status_codes import (
    GroupCodes, GenericCodes, GenericFailureCodes,
    GroupFailureCodes, DbCodes
)
from vFense.core.group import Group
from vFense.core.group._db import (
    fetch_group, fetch_usernames_in_group,
    insert_group
)

from vFense.core.group._constants import GroupDefaults
from vFense.core.permissions._constants import Permissions

from vFense.core._constants import (
    CommonKeys, DefaultStringLength, RegexPattern
)
from vFense.core.group._db_model import (
    GroupKeys
)

logging.config.fileConfig(VFENSE_LOGGING_CONFIG)
logger = logging.getLogger('rvapi')

class GroupManager(object):
    def __init__(self, group_id=None):
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
    def create(self, group):
        """Create a group in vFense
        Args:
            group_name (Group): Instance of a group.

        Basic Usage:
            >>> from vFense.group import Group
            >>> from vFense.group.manager import GroupManager
            >>> name = 'Linux Admins'
            >>> view = 'default'
            >>> permissions = ['administrator']
            >>> is_global = True
            >>> restricted = False
            >>> group = Group(name, permissions, view, is_global, restricted)
            >>> manager = GroupManager()
            >>> manager.create(group)

        Returns:
            Returns the results in a dictionary
        """

        status = self.create.func_name + ' - '
        generated_ids = []
        group_data = group.to_dict()
        group_exist = self.properties
        invalid_fields = group.get_invalid_fields()
        if not invalid_fields and not group_exist:
            status_code, status_count, error, generated_ids = (
                insert_group(group_data)
            )

            if status_code == DbCodes.Inserted:
                msg = 'group %s created' % (group.name)
                generic_status_code = GenericCodes.ObjectCreated
                vfense_status_code = GroupCodes.GroupCreated

        elif group_exist:
            msg = 'group %s exists' % (group.name)
            status_code = DbCodes.Unchanged
            generic_status_code = GenericCodes.ObjectExists
            vfense_status_code = GroupFailureCodes.GroupIdExists


        results = {
            ApiResultKeys.ERRORS: invalid_fields,
            ApiResultKeys.GENERIC_STATUS_CODE: generic_status_code,
            ApiResultKeys.VFENSE_STATUS_CODE: vfense_status_code,
            ApiResultKeys.GENERATED_IDS: generated_ids,
            ApiResultKeys.MESSAGE: status + msg,
            ApiResultKeys.DATA: group_data,
        }

        return results

