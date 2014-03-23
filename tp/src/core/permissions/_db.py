
from vFense.core.groups import *
from vFense.db.client import r, db_create_close

@db_create_close
def fetch_all_permissions_for_user(username, conn=None):
    try:
        permissions = (
            r
            .table(GroupsPerUserCollection)
            .get_all(
                username, index=GroupsPerUserIndexes.UserName
            )
            .map(GroupsPerUserKeys.
