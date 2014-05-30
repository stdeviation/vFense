import logging
import logging.config
from vFense import VFENSE_LOGGING_CONFIG
from vFense.db.client import *

from vFense.server.hierarchy import *
#from server.hierarchy.group import *
#from server.hierarchy.user import *
#from server.hierarchy.view import *

logging.config.fileConfig(VFENSE_LOGGING_CONFIG)
logger = logging.getLogger('rvapi')

_main_db = 'vFense'


@db_create_close
def initialization(conn=None):

    _create_tables(conn)
    _create_indices(conn)


def _create_tables(conn):

    tables = r.db(_main_db).table_list().run(conn)

    if Collection.Users not in tables:
        _create_users_table(conn)

    if Collection.Groups not in tables:
        _create_groups_table(conn)

    if Collection.Views not in tables:
        _create_views_table(conn)

#    if Collection.GroupsPerView not in tables:
#        _create_GPC_table(conn)

    if Collection.GroupsPerUser not in tables:
        _create_GPU_table(conn)

    if Collection.UsersPerView not in tables:
        _create_UPC_table(conn)


def _create_indices(conn):

    _create_groups_indices(conn)
    # _create_GPC_indices(conn)
    _create_GPU_indices(conn)
    _create_UPC_indices(conn)

def _create_UPC_table(conn=None):

    try:

        r.db(_main_db).table_create(
            Collection.UsersPerView
        ).run(conn)

    except Exception as e:

        logger.error(
            "Unable to create %s table." % Collection.UsersPerView
        )
        logger.exception(e)

def _create_UPC_indices(conn):

    try:

        indices = r.table(Collection.UsersPerView).index_list().run(conn)

        if UsersPerViewKey.UserId not in indices:
            r.table(
                Collection.UsersPerView
            ).index_create(UsersPerViewKey.UserId).run(conn)

        if UsersPerViewKey.ViewId not in indices:
            r.table(
                Collection.UsersPerView
            ).index_create(UsersPerViewKey.ViewId).run(conn)

        if UsersPerViewKey.UserAndViewId not in indices:
            r.table(
                Collection.UsersPerView
            ).index_create(
                UsersPerViewKey.UserAndViewId,
                lambda row:
                [
                    row[UsersPerViewKey.UserId],
                    row[UsersPerViewKey.ViewId]
                ]
            ).run(conn)

    except Exception as e:

        logger.error(
            "Unable to create indices for %s table." % Collection.UsersPerView
        )
        logger.exception(e)


def _create_GPU_table(conn=None):

    try:

        r.db(_main_db).table_create(
            Collection.GroupsPerUser
        ).run(conn)

    except Exception as e:

        logger.error(
            "Unable to create %s table." % Collection.GroupsPerUser
        )
        logger.exception(e)


def _create_GPU_indices(conn=None):

    try:

        indices = r.table(Collection.GroupsPerUser).index_list().run(conn)

        if GroupsPerUserKey.UserId not in indices:
            r.table(
                Collection.GroupsPerUser
            ).index_create(GroupsPerUserKey.UserId).run(conn)

        if GroupsPerUserKey.GroupIdAndViewId not in indices:
            r.table(
                Collection.GroupsPerUser
            ).index_create(
                GroupsPerUserKey.GroupIdAndViewId,
                lambda row:
                [
                    row[GroupsPerUserKey.GroupId],
                    row[GroupsPerUserKey.ViewId]
                ]
            ).run(conn)

        if GroupsPerUserKey.UserIdAndViewId not in indices:
            r.table(
                Collection.GroupsPerUser
            ).index_create(
                GroupsPerUserKey.UserIdAndViewId,
                lambda row:
                [
                    row[GroupsPerUserKey.UserId],
                    row[GroupsPerUserKey.ViewId]
                ]
            ).run(conn)

        if GroupsPerUserKey.GroupUserAndViewId not in indices:
            r.table(
                Collection.GroupsPerUser
            ).index_create(
                GroupsPerUserKey.GroupUserAndViewId,
                lambda row:
                [
                    row[GroupsPerUserKey.GroupId],
                    row[GroupsPerUserKey.UserId],
                    row[GroupsPerUserKey.ViewId]
                ]
            ).run(conn)

    except Exception as e:

        logger.error(
            "Unable to create indices for %s table." % Collection.GroupsPerUser
        )
        logger.exception(e)

def _create_GPC_table(conn=None):

    try:

        r.db(_main_db).table_create(
            Collection.GroupsPerView
        ).run(conn)

    except Exception as e:

        logger.error(
            "Unable to create %s table." % Collection.GroupsPerView
        )
        logger.exception(e)


def _create_GPC_indices(conn=None):

    try:

        indices = r.table(Collection.GroupsPerView).index_list().run(conn)

        if GroupsPerViewKey.GroupId not in indices:
            r.table(
                Collection.GroupsPerView
            ).index_create(GroupsPerViewKey.GroupId).run(conn)

        if GroupsPerViewKey.ViewId not in indices:
            r.table(
                Collection.GroupsPerView
            ).index_create(GroupsPerViewKey.ViewId).run(conn)

        if GroupsPerViewKey.GroupAndViewId not in indices:
            r.table(
                Collection.GroupsPerView
            ).index_create(
                GroupsPerViewKey.GroupAndViewId,
                lambda row:
                [
                    row[GroupsPerViewKey.GroupId],
                    row[GroupsPerViewKey.ViewId]
                ]
            ).run(conn)

    except Exception as e:

        logger.error(
            "Unable to create indices for table  %s." % Collection.GroupsPerView
        )
        logger.exception(e)

def _create_groups_table(conn=None):

    try:

        r.db(_main_db).table_create(Collection.Groups).run(conn)

    except Exception as e:

        logger.error("Unable to create %s table." % Collection.Groups)
        logger.exception(e)


def _create_groups_indices(conn=None):

    try:

        indices = r.table(Collection.Groups).index_list().run(conn)

        if GroupKey.GroupName not in indices:
            r.table(
                Collection.Groups
            ).index_create(GroupKey.GroupName).run(conn)

        if GroupKey.ViewId not in indices:
            r.table(
                Collection.Groups
            ).index_create(GroupKey.ViewId).run(conn)

        if GroupKey.GroupNameAndViewId not in indices:
            r.table(
                Collection.Groups
            ).index_create(
                GroupKey.GroupNameAndViewId,
                lambda row:
                [
                    row[GroupKey.GroupName],
                    row[GroupKey.ViewId]
                ]
            ).run(conn)

    except Exception as e:

        logger.error("Unable to create indices for table %s." % Collection.Groups)
        logger.exception(e)

def _create_views_table(conn=None):

    try:

        r.db(_main_db).table_create(
            Collection.Views,
            primary_key=ViewKey.ViewName
        ).run(conn)

    except Exception as e:

        logger.error("Unable to create %s table." % Collection.Views)
        logger.exception(e)


def _create_users_table(conn=None):

    try:
        r.db(_main_db).table_create(
            Collection.Users,
            primary_key=UserKey.UserName
        ).run(conn)

    except Exception as e:

        logger.error("Unable to create %s table." % Collection.Users)
        logger.exception(e)
