import logging

from vFense import VFENSE_LOGGING_CONFIG
from vFense.core.group._db_model import (
    GroupCollections, GroupKeys, GroupIndexes
)
from vFense.core.permissions._constants import Permissions
from vFense.db.client import r, db_create_close
from vFense.core.decorators import time_it

logging.config.fileConfig(VFENSE_LOGGING_CONFIG)
logger = logging.getLogger('rvapi')

@time_it
@db_create_close
def validate_permission_for_user(username, view_name, permission, conn=None):
    permission_exist = False
    try:
        is_empty = (
            r
            .table(GroupCollections.Groups)
            .get_all(username, index=GroupIndexes.Users)
            .filter(
                lambda x: x[GroupKeys.Views].contains(view_name)
            )
            .filter(
                lambda x: x[GroupKeys.Permissions].contains(permission)
            )
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
                .filter(
                    lambda x: x[GroupKeys.Views].contains(view_name)
                )
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

    except Exception as e:
        logger.exception(e)

    return(permission_exist)

