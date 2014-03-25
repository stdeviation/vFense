import logging

from vFense.core.group import *
from vFense.core.group._constants import *
from vFense.core.permissions._constants import *
from vFense.db.client import r, db_create_close

logging.config.fileConfig('/opt/TopPatch/conf/logging.config')
logger = logging.getLogger('rvapi')

@db_create_close
def validate_permission_for_user(username, customer_name, permission, conn=None):
    permission_exist = False
    try:
        is_empty = (
            r
            .table(GroupCollections.GroupsPerUser)
            .get_all(username, index=GroupsPerUserIndexes.UserName)
            .filter({GroupsPerUserKeys.CustomerName: customer_name})
            .eq_join(
                lambda group: group[GroupsPerUserKeys.GroupName],
                r.table(GroupCollections.Groups),
                index=GroupIndexes.GroupName
            )
            .zip()
            .filter(r.row[GroupKeys.Permissions].contains(permission))
            .is_empty()
            .run(conn)
        )
        if not is_empty:
            permission_exist = True

        else:
            is_admin_empty = (
                r
                .table(GroupCollections.GroupsPerUser)
                .get_all(username, index=GroupsPerUserIndexes.UserName)
                .filter({GroupsPerUserKeys.CustomerName: customer_name})
                .eq_join(
                    lambda group: group[GroupsPerUserKeys.GroupName],
                    r.table(GroupCollections.Groups),
                    index=GroupIndexes.GroupName
                )
                .zip()
                .filter(
                    r.row[GroupKeys.Permissions].contains(
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
