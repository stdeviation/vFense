import logging
from vFense import VFENSE_LOGGING_CONFIG
from vFense.core.decorators import time_it
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
