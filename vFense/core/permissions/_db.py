import logging

from vFense._constants import VFENSE_LOGGING_CONFIG
from vFense.core.group._db_model import (
    GroupCollections, GroupKeys, GroupIndexes
)
from vFense.core.permissions._constants import Permissions
from vFense.db.client import r, db_create_close
from vFense.core.decorators import time_it, catch_it

logging.config.fileConfig(VFENSE_LOGGING_CONFIG)
logger = logging.getLogger('rvapi')

@time_it
@catch_it(False)
@db_create_close
def validate_permission_for_user(username, view_name, permission, conn=None):
    """Check if permission is valid for this user.
    Args:
        username (str); The name of the user.
        view_name (str): The name of the current view.
        permission (str): The permission you are verifying against.

    Basic Usage:
        >>> from vFense.core.permissions._db import validate_permission_for_user
        >>> validate_permission_for_user('global_admin', 'global', 'install')
        >>> True

    Returns:
        Boolean True or False
    """
    permission_exist = False
    is_empty = (
        r
        .table(GroupCollections.Groups)
        .get_all(username, index=GroupIndexes.Users)
        .filter(lambda x: x[GroupKeys.Views].contains(view_name))
        .filter(lambda x: x[GroupKeys.Permissions].contains(permission))
        .is_empty()
        .run(conn)
    )
    if not is_empty:
        permission_exist = True

    else:
        is_admin_empty = (
            r
            .table(GroupCollections.Groups)
            .get_all(username, index=GroupIndexes.Users)
            .filter(lambda x: x[GroupKeys.Views].contains(view_name))
            .filter(
                lambda x: x[GroupKeys.Permissions].contains(
                    Permissions.ADMINISTRATOR
                )
            )
            .is_empty()
            .run(conn)
        )

        if not is_admin_empty:
            permission_exist = True

    return permission_exist
