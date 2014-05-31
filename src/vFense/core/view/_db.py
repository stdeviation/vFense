import logging

from vFense import VFENSE_LOGGING_CONFIG
from vFense.core.view._db_model import *
from vFense.core.group._constants import *
from vFense.core.group._db_model import *
from vFense.core.user._constants import *
from vFense.core.decorators import return_status_tuple, time_it
from vFense.db.client import db_create_close, r

logging.config.fileConfig(VFENSE_LOGGING_CONFIG)
logger = logging.getLogger('rvapi')


@time_it
@db_create_close
def fetch_view(view_name, keys_to_pluck=None, conn=None):
    """Retrieve view information
    Args:
        view_name (str):   Name of the view.

    Kwargs:
        keys_to_pluck (array): list of keys you want to retreive from the db.

    Basic Usage::
        >>> from vFense.view._db import fetch_view
        >>> view_name = 'default'
        >>> fetch_view(view_name)

    Returns:
        Returns a Dict of the properties of a view
        {
            u'cpu_throttle': u'normal',
            u'package_download_url_base': u'http: //10.0.0.21/packages/',
            u'operation_ttl': 10,
            u'net_throttle': 0,
            u'view_name': u'default'
        }
    """
    data = []
    try:
        if view_name and keys_to_pluck:
            data = (
                r
                .table(ViewCollections.views)
                .get(view_name)
                .pluck(keys_to_pluck)
                .run(conn)
            )
        elif view_name and not keys_to_pluck:
            data = (
                r
                .table(ViewCollections.views)
                .get(view_name)
                .run(conn)
            )

    except Exception as e:
        logger.exception(e)

    return(data)


@time_it
@db_create_close
def fetch_view_names_for_user(username, conn=None):
    """Retrieve view information
    Args:
        view_name (str):   Name of the view.

    Kwargs:
        keys_to_pluck (array): list of keys you want to retreive from the db.

    Basic Usage::
        >>> from vFense.view._db import fetch_view
        >>> view_name = 'default'
        >>> fetch_view(view_name)

    Returns:
        Returns a list of view names
        [
            'default'
        ]
    """
    data = []
    try:
        data = list(
            r
            .table(ViewCollections.ViewsPerUser)
            .get_all(username, index=viewPerUserIndexes.UserName)
            .map(lambda x: x[ViewPerUserKeys.viewName])
            .run(conn)
        )

    except Exception as e:
        logger.exception(e)

    return(data)


@time_it
@db_create_close
def fetch_all_view_names(conn=None):
    """Retrieve all view names

    Basic Usage:
        >>> from vFense.view._db import fetch_all_view_names
        >>> fetch_all_view_names()

    Returns:
        Returns a list of view names
        >>>
        [
            'default'
        ]
    """
    data = []
    try:
        data = list(
            r
            .table(ViewCollections.views)
            .map(lambda x: x[viewKeys.viewName])
            .run(conn)
        )

    except Exception as e:
        logger.exception(e)

    return data


@time_it
@db_create_close
def fetch_views(match=None, keys_to_pluck=None, conn=None):
    """Retrieve all views or just views based on regular expressions
    Kwargs:
        match (str): Regular expression of the view name
            you are searching for.
        keys_to_pluck (array): list of keys you want to retreive from the db.

    Returns:
        Returns a List of views

    Basic Usage::
        >>> from vFense.view._db import fetch_views
        >>> fetch_views()

    Return:
        List of view properties.
        [
            {
                u'cpu_throttle': u'normal',
                u'package_download_url_base': u'http: //10.0.0.21/packages/',
                u'operation_ttl': 10,
                u'net_throttle': 0,
                u'view_name': u'default'
            },
            {
                u'cpu_throttle': u'normal',
                u'package_download_url_base': u'http: //10.0.0.21/packages/',
                u'operation_ttl': 10,
                u'net_throttle': 0,
                u'view_name': u'TopPatch'
            }
        ]
    """
    data = []
    try:
        if match and keys_to_pluck:
            data = list(
                r
                .table(ViewCollections.views)
                .filter(
                    lambda name:
                    name[viewKeys.viewName].match("(?i)" + match)
                )
                .pluck(keys_to_pluck)
                .run(conn)
            )

        elif match and not keys_to_pluck:
            data = list(
                r
                .table(ViewCollections.views)
                .filter(
                    lambda name:
                    name[viewKeys.viewName].match("(?i)" + match)
                )
                .run(conn)
            )

        elif not match and not keys_to_pluck:
            data = list(
                r
                .table(ViewCollections.views)
                .run(conn)
            )

        elif not match and keys_to_pluck:
            data = list(
                r
                .table(ViewCollections.views)
                .pluck(keys_to_pluck)
                .run(conn)
            )

    except Exception as e:
        logger.exception(e)

    return(data)


@time_it
@db_create_close
def fetch_properties_for_view(view_name, conn=None):
    """Retrieve a view and all its properties.
    Args:
        view_name (str): Name of the view

    Returns:
        Returns a Dictionary of views

    Basic Usage::
        >>> from vFense.view._db import fetch_properties_for_view
        >>> fetch_properties_for_view()

    Return:
        Dictionary of view properties.
    """
    map_hash = (
        lambda x:
        {
            viewKeys.viewName: x[viewKeys.viewName],
            viewKeys.CpuThrottle: x[viewKeys.CpuThrottle],
            viewKeys.NetThrottle: x[viewKeys.NetThrottle],
            viewKeys.ServerQueueTTL: x[viewKeys.ServerQueueTTL],
            viewKeys.AgentQueueTTL: x[viewKeys.AgentQueueTTL],
            viewKeys.PackageUrl: x[viewKeys.PackageUrl],
            viewKeys.Users: (
                r
                .table(ViewCollections.ViewsPerUser)
                .get_all(
                    x[ViewPerUserKeys.viewName],
                    index=viewPerUserIndexes.viewName
                )
                .coerce_to('array')
                .pluck(ViewPerUserKeys.UserName)
            ),
            viewKeys.Groups: (
                r
                .table(GroupCollections.Groups)
                .get_all(
                    x[GroupKeys.viewName],
                    index=GroupIndexes.viewName
                )
                .coerce_to('array')
                .pluck(GroupKeys.GroupName, GroupKeys.GroupId)
            )
        }
    )

    data = []
    try:
        data = list(
            r
            .table(ViewCollections.views)
            .get_all(view_name)
            .map(map_hash)
            .run(conn)
        )

    except Exception as e:
        logger.exception(e)

    return(data)


@time_it
@db_create_close
def fetch_properties_for_all_views(username=None, conn=None):
    """Retrieve all views or retrieve all views that user has
        access to.
    Kwargs:
        user_name (str): Name of the username,

    Returns:
        Returns a List of views

    Basic Usage::
        >>> from vFense.view._db import fetch_properties_for_all_views
        >>> fetch_properties_for_all_views()

    Return:
        List of view properties.
        [
            {
                u'cpu_throttle': u'normal',
                u'package_download_url_base': u'http: //10.0.0.21/packages/',
                u'operation_ttl': 10,
                u'net_throttle': 0,
                u'view_name': u'default'
            },
            {
                u'cpu_throttle': u'normal',
                u'package_download_url_base': u'http: //10.0.0.21/packages/',
                u'operation_ttl': 10,
                u'net_throttle': 0,
                u'view_name': u'TopPatch'
            }
        ]
    """
    map_hash = (
        lambda x:
        {
            viewKeys.viewName: x[viewKeys.viewName],
            viewKeys.CpuThrottle: x[viewKeys.CpuThrottle],
            viewKeys.NetThrottle: x[viewKeys.NetThrottle],
            viewKeys.ServerQueueTTL: x[viewKeys.ServerQueueTTL],
            viewKeys.AgentQueueTTL: x[viewKeys.AgentQueueTTL],
            viewKeys.PackageUrl: x[viewKeys.PackageUrl],
            viewKeys.Users: (
                r
                .table(ViewCollections.ViewsPerUser)
                .get_all(
                    x[ViewPerUserKeys.viewName],
                    index=viewPerUserIndexes.viewName
                )
                .coerce_to('array')
                .pluck(ViewPerUserKeys.UserName)
            ),
            viewKeys.Groups: (
                r
                .table(GroupCollections.Groups)
                .get_all(
                    x[GroupKeys.viewName],
                    index=GroupIndexes.viewName
                )
                .coerce_to('array')
                .pluck(GroupKeys.GroupName, GroupKeys.GroupId)
            )
        }
    )

    data = []
    try:
        if username:
            data = list(
                r
                .table(ViewCollections.ViewsPerUser)
                .filter(
                    {
                        ViewPerUserKeys.UserName: username
                    }
                )
                .eq_join(
                    lambda x:
                    x[viewKeys.viewName],
                    r.table(ViewCollections.views)
                )
                .zip()
                .map(map_hash)
                .run(conn)
            )

        else:
            data = list(
                r
                .table(ViewCollections.views)
                .map(map_hash)
                .run(conn)
            )


    except Exception as e:
        logger.exception(e)

    return(data)



@time_it
@db_create_close
def fetch_users_for_view(view_name, keys_to_pluck=None, conn=None):
    """Retrieve all the users for a view
    Args:
        view_name (str):  Name of the view.

    Kwargs:
        keys_to_pluck (list):  list of keys you want to retreive from the db.

    Basic Usage:
        >>> from vFense.view._db import fetch_users_for_view
        >>> view_name = 'default'
        >>> fetch_users_for_view(view_name)

    Returns:
        Returns a List of users for a view

        [
            {
                u'user_name': u'alien',
                u'id': u'ba9682ef-7adf-4916-8002-9637485b30d8',
                u'view_name': u'default'
            },
            {
                u'user_name': u'admin',
                u'id': u'6bd86dcd-43fc-424e-88f1-684ce2189d88',
                u'view_name': u'default'
            }
        ]
    """
    data = []
    try:
        if view_name and keys_to_pluck:
            data = list(
                r
                .table(ViewCollections.ViewsPerUser)
                .get_all(
                    view_name,
                    index=viewPerUserIndexes.viewName
                )
                .pluck(keys_to_pluck)
                .run(conn)
            )
        elif view_name and not keys_to_pluck:
            data = list(
                r
                .table(ViewCollections.ViewsPerUser)
                .get_all(
                    view_name,
                    index=viewPerUserIndexes.viewName
                )
                .run(conn)
            )

    except Exception as e:
        logger.exception(e)

    return(data)


@time_it
@db_create_close
def fetch_views_for_user(username, keys_to_pluck=None, conn=None):
    """Retrieve all the views for a user
    Args:
        username (str):  Name of the user.

    Kwargs:
        keys_to_pluck (list):  list of keys you want to retreive from the db.

    Basic Usage::
        >>> from vFense.view._db import fetch_views_for_user
        >>> view_name = 'default'
        >>> fetch_views_for_user(username)

    Returns:
        Returns a List of views for a user.
        [
            {
                u'user_name': u'admin',
                u'id': u'6bd86dcd-43fc-424e-88f1-684ce2189d88',
                u'view_name': u'default'
            }
        ]
    """
    data = []
    try:
        if username and keys_to_pluck:
            data = list(
                r
                .table(ViewCollections.ViewsPerUser)
                .get_all(username, index=viewPerUserIndexes.UserName)
                .pluck(keys_to_pluck)
                .run(conn)
            )
        elif username and not keys_to_pluck:
            data = list(
                r
                .table(ViewCollections.ViewsPerUser)
                .get_all(username, index=viewPerUserIndexes.UserName)
                .run(conn)
            )

    except Exception as e:
        logger.exception(e)

    return(data)


@time_it
@db_create_close
def users_exists_in_view(username, view_name, conn=None):
    """Verify if username is part of view
    Args:
        username:  Name of the user.
        view_name:  Name of the view.

    Basic Usage:
        >>> from vFense.core.view._db import users_exists_in_view
        >>> username = 'admin'
        >>> view_name = 'default'
        >>> users_exists_in_view(username, view_name)

    Return:
        Boolean

    """
    exist = False
    try:
        empty = (
            r
            .table(ViewCollections.ViewsPerUser)
            .get_all(view_name, index=viewPerUserIndexes.viewName)
            .filter({ViewPerUserKeys.UserName: username})
            .is_empty()
            .run(conn)
        )
        if not empty:
            exist = True

    except Exception as e:
        logger.exception(e)

    return(exist)


@time_it
@db_create_close
def users_exists_in_views(view_names, conn=None):
    """Verify if users exists in these views.
    Args:
        view_names (list):  List of the view names.

    Basic Usage:
        >>> from vFense.core.view._db import users_exists_in_views
        >>> view_names = ['default', 'test']
        >>> users_exists_in_views(view_names)

    Return:
        Tuple (Boolean, [views_with_users], [views_without_users])
        (True, ['default'], ['tester'])

    """
    exist = False
    users_exist = []
    users_not_exist = []
    results = (exist, users_exist, users_not_exist)
    try:
        for view_name in view_names:
            empty = (
                r
                .table(ViewCollections.ViewsPerUser)
                .get_all(
                    view_name,
                    index=viewPerUserIndexes.viewName
                )
                .is_empty()
                .run(conn)
            )

            if not empty:
                users_exist.append(view_name)
                exist = True

            else:
                users_not_exist.append(view_name)

        results = (exist, users_exist, users_not_exist)

    except Exception as e:
        logger.exception(e)

    return(results)


@time_it
@db_create_close
@return_status_tuple
def insert_view(view_data, conn=None):
    """Insert a new view into the database
    Args:
        view_data (list|dict): Can either be a list of dictionaries or a dictionary
        of the data you are inserting.

    Basic Usage:
        >>> from vFense.view._db import insert_view
        >>> view_data = {'view_name': 'vFense', 'operation_queue_ttl': 10}
        >>> insert_view(data)

    Return:
        Tuple (status_code, count, error, generated ids)
        >>> (2001, 1, None, [])
    """
    data = {}
    try:
        data = (
                r
                .table(ViewCollections.views)
                .insert(view_data)
                .run(conn)
                )

    except Exception as e:
        logger.exception(e)

    return(data)


@time_it
@db_create_close
@return_status_tuple
def update_view(view_name, view_data, conn=None):
    """Update verious fields of a view
    Args:
        view_name(str): view_name.
        view_data(dict): Dictionary of the data you are updating.

    Basic Usage::
        >>> from vFense.view._db import update_view
        >>> view_name = 'default'
        >>> view_data = {'operation_queue_ttl': 10}
        >>> update_view(view_data)

    Return:
        Tuple (status_code, count, error, generated ids)
        >>> (2001, 1, None, [])
    """
    data = {}
    try:
        data = (
            r
            .table(ViewCollections.views)
            .get(view_name)
            .update(view_data)
            .run(conn)
        )

    except Exception as e:
        logger.exception(e)

    return data


@time_it
@db_create_close
@return_status_tuple
def insert_user_per_view(user_data, conn=None):
    """Add a view to a user, this function should not be called directly.
    Args:
        user_data(list|dict): Can either be a list of dictionaries or a
        dictionary of the data you are inserting.

    Basic Usage:
        >>> from vFense.view._db import insert_user_per_view
        >>> user_data = {'view_name': 'vFense', 'needs_reboot': 'no'}
        >>> insert_user_per_view(user_data)

    Return:
        Tuple (status_code, count, error, generated ids)
        >>> (2001, 1, None, [])
    """
    data = {}
    try:
        data = (
            r
            .table(ViewCollections.ViewsPerUser)
            .insert(user_data)
            .run(conn)
        )

    except Exception as e:
        logger.exception(e)

    return(data)


@time_it
@db_create_close
@return_status_tuple
def delete_user_in_views(username, view_names=None, conn=None):
    """Remove a view from a user or remove all views for a user.
    Args:
        username (str): Name of the user.

    Kwargs:
        view_names (list): List of view_names.

    Basic Usage::
        >>> from vFense.view._db delete_user_in_views
        >>> username = 'agent_api'
        >>> delete_user_in_views(username)

    Return:
        Tuple (status_code, count, error, generated ids)
        >>> (2001, 1, None, [])
    """
    data = {}
    try:
        if view_names:
            data = (
                r
                .expr(view_names)
                .for_each(
                    lambda view_name:
                    r
                    .table(ViewCollections.ViewsPerUser)
                    .filter(
                        {
                            ViewPerUserKeys.UserName: username,
                            ViewPerUserKeys.viewName: view_name
                        }
                    )
                    .delete()
                )
                .run(conn)
            )

        else:
            data = (
                r
                .table(ViewCollections.ViewsPerUser)
                .filter(
                    {
                        ViewPerUserKeys.UserName: username,
                    }
                )
                .delete()
                .run(conn)
            )

    except Exception as e:
        logger.exception(e)

    return(data)


@time_it
@db_create_close
@return_status_tuple
def delete_users_in_view(usernames, view_name, conn=None):
    """Remove users from a view.
    Args:
        username (list): List of usernames you want
            to remove from the view.
        view_name (str): The name of the view,
            you want to remove the user from.

    Basic Usage::
        >>> from vFense.view._db delete_users_in_view
        >>> username = ['tester1', 'tester2']
        >>> view_name = ['Tester']
        >>> delete_users_in_view(username)

    Return:
        Tuple (status_code, count, error, generated ids)
        >>> (2001, 1, None, [])
    """
    data = {}
    try:
        data = (
            r
            .expr(usernames)
            .for_each(
                lambda username:
                r
                .table(ViewCollections.ViewsPerUser)
                .filter(
                    {
                        ViewPerUserKeys.UserName: username,
                        ViewPerUserKeys.viewName: view_name
                    }
                )
                .delete()
            )
            .run(conn)
        )

    except Exception as e:
        logger.exception(e)

    return(data)


@time_it
@db_create_close
@return_status_tuple
def delete_view(view_name, conn=None):
    """Delete a view from the database.
    Args:
        view_name: Name of the view

    Basic Usage::
        >>> from vFense.view._db delete_view
        >>> view_name = 'test'
        >>> delete_view(view_name)

    Return:
        Tuple (status_code, count, error, generated ids)
        >>> (2001, 1, None, [])
    """
    data = {}
    try:
        data = (
            r
            .table(ViewCollections.views)
            .get(view_name)
            .delete()
            .run(conn)
        )

    except Exception as e:
        logger.exception(e)

    return(data)


@time_it
@db_create_close
@return_status_tuple
def delete_views(view_names, conn=None):
    """Delete a view from the database.
    Args:
        view_name: Name of the view

    Basic Usage::
        >>> from vFense.view._db delete_views
        >>> view_names = ['test', 'foo']
        >>> delete_views(view_names)

    Return:
        Tuple (status_code, count, error, generated ids)
        >>> (2001, 1, None, [])
    """
    data = {}
    try:
        data = (
            r
            .expr(view_names)
            .for_each(
                lambda view_name:
                r
                .table(ViewCollections.views)
                .get(view_name)
                .delete()
            )
            .run(conn)
        )

    except Exception as e:
        logger.exception(e)

    return(data)
