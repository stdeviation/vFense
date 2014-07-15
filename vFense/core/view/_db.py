import logging

from vFense import VFENSE_LOGGING_CONFIG
from vFense.core.view._db_model import (
    ViewCollections, ViewKeys, ViewIndexes
)
from vFense.core.group._db_model import (
    GroupCollections, GroupKeys, GroupIndexes
)
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
                .table(ViewCollections.Views)
                .get(view_name)
                .pluck(keys_to_pluck)
                .run(conn)
            )
        elif view_name and not keys_to_pluck:
            data = (
                r
                .table(ViewCollections.Views)
                .get(view_name)
                .run(conn)
            )

    except Exception as e:
        logger.exception(e)

    return data

@time_it
@db_create_close
def fetch_all_current_tokens(conn=None):
    """Retrieve a list of all current tokens

    Basic Usage::
        >>> from vFense.view._db import fetch_all_current_tokens
        >>> fetch_all_current_tokens()

    Returns:
        Returns a list of tokens.
    """
    data = []
    try:
        data = list(
            r
            .table(ViewCollections.Views)
            .map(
                lambda token:
                token[ViewKeys.Token]
            )
            .run(conn)
        )

    except Exception as e:
        logger.exception(e)

    return data

@time_it
@db_create_close
def fetch_view_for_token(token, conn=None):
    """Retrieve the view associated for this token.
    Args:
        token (str): Base64 token, that the agent uses to authenticate.

    Basic Usage::
        >>> from vFense.view._db import fetch_view_for_token
        >>> fetch_view_for_token(token)

    Returns:
        Returns True or False
    """
    view_name = None
    try:
        data = list(
            r
            .table(ViewCollections.Views)
            .filter(
                lambda x:
                (x[ViewKeys.Token] ==  token)
                |
                (x[ViewKeys.PreviousTokens].contains(token))
            )
            .run(conn)
        )
        if data:
            view_name = data[ViewKeys.ViewName]


    except Exception as e:
        logger.exception(e)

    return view_name


@time_it
@db_create_close
def token_exist_in_current(token, conn=None):
    """Retrieve a list of all current tokens
    Args:
        token (str): Base64 token, that the agent uses to authenticate.

    Basic Usage::
        >>> from vFense.view._db import token_exist_in_current
        >>> token_exist_in_current(token)

    Returns:
        Returns True or False
    """
    exist = False
    try:
        is_empty = (
            r
            .table(ViewCollections.Views)
            .get_all(token, index=ViewIndexes.Token)
            .is_empty()
            .run(conn)
        )
        if not is_empty:
            exist = True

    except Exception as e:
        logger.exception(e)

    return exist

@time_it
@db_create_close
def token_exist_in_previous(token, conn=None):
    """Verify if the token existed previously.
    Args:
        token (str): Base64 token, that the agent uses to authenticate.

    Basic Usage::
        >>> from vFense.view._db import token_exist_in_previous
        >>> token_exist_in_previous(token)

    Returns:
        Returns True or False
    """
    exist = False
    try:
        is_empty = (
            r
            .table(ViewCollections.Views)
            .get_all(token, index=ViewIndexes.PreviousTokens)
            .is_empty()
            .run(conn)
        )
        if not is_empty:
            exist = True

    except Exception as e:
        logger.exception(e)

    return exist

@time_it
@db_create_close
def fetch_all_previous_tokens(conn=None):
    """Retrieve a list of all current tokens

    Basic Usage::
        >>> from vFense.view._db import fetch_all_previous_tokens
        >>> fetch_all_previous_tokens()

    Returns:
        Returns a list of tokens.
    """
    data = []
    try:
        data = list(
            r
            .table(ViewCollections.Views)
            .map(
                lambda token:
                token[ViewKeys.PreviousTokens]
            )
            .run(conn)
        )

    except Exception as e:
        logger.exception(e)

    return data


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
            .table(ViewCollections.Views)
            .map(lambda x: x[ViewKeys.ViewName])
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
                .table(ViewCollections.Views)
                .filter(
                    lambda name:
                    name[ViewKeys.ViewName].match("(?i)" + match)
                )
                .pluck(keys_to_pluck)
                .run(conn)
            )

        elif match and not keys_to_pluck:
            data = list(
                r
                .table(ViewCollections.Views)
                .filter(
                    lambda name:
                    name[ViewKeys.ViewName].match("(?i)" + match)
                )
                .run(conn)
            )

        elif not match and not keys_to_pluck:
            data = list(
                r
                .table(ViewCollections.Views)
                .run(conn)
            )

        elif not match and keys_to_pluck:
            data = list(
                r
                .table(ViewCollections.Views)
                .pluck(keys_to_pluck)
                .run(conn)
            )

    except Exception as e:
        logger.exception(e)

    return data


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
            ViewKeys.ViewName: x[ViewKeys.ViewName],
            ViewKeys.CpuThrottle: x[ViewKeys.CpuThrottle],
            ViewKeys.NetThrottle: x[ViewKeys.NetThrottle],
            ViewKeys.ServerQueueTTL: x[ViewKeys.ServerQueueTTL],
            ViewKeys.AgentQueueTTL: x[ViewKeys.AgentQueueTTL],
            ViewKeys.PackageUrl: x[ViewKeys.PackageUrl],
            ViewKeys.Users: x[ViewKeys.Users],
            ViewKeys.Groups: (
                r
                .table(GroupCollections.Groups)
                .get_all(
                    x[GroupKeys.ViewName],
                    index=GroupIndexes.ViewName
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
            .table(ViewCollections.Views)
            .get_all(view_name)
            .map(map_hash)
            .run(conn)
        )

    except Exception as e:
        logger.exception(e)

    return data

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
            .table(ViewCollections.Views)
            .insert(view_data)
            .run(conn)
        )

    except Exception as e:
        logger.exception(e)

    return data


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
            .table(ViewCollections.Views)
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
                    .table(ViewCollections.Views)
                    .get(view_name)
                    .update(
                        lambda x:
                        {
                            ViewKeys.Users: (
                                x[ViewKeys.Users]
                                .set_difference([username])
                            )
                        }
                    )
                )
                .run(conn)
            )

        else:
            data = (
                r
                .table(ViewCollections.Views)
                .update(
                    lambda x:
                    {
                        ViewKeys.Users: (
                            x[ViewKeys.Users].set_difference([username])
                        )
                    }
                )
                .run(conn)
            )

    except Exception as e:
        logger.exception(e)

    return data


@time_it
@db_create_close
@return_status_tuple
def delete_users_in_view(usernames, view_name, conn=None):
    """Remove users from a view.
    Args:
        usernames (list): List of usernames you want
            to remove from the view.
        view_name (str): The name of the view,
            you want to remove the user from.

    Basic Usage::
        >>> from vFense.view._db delete_users_in_view
        >>> usernames = ['tester1', 'tester2']
        >>> view_name = ['Tester']
        >>> delete_users_in_view(usernames, view_name)

    Return:
        Tuple (status_code, count, error, generated ids)
        >>> (2001, 1, None, [])
    """
    data = {}
    try:
        data = (
            r
            .table(ViewCollections.Views)
            .get_all(view_name)
            .update(
                lambda x:
                {
                    ViewKeys.Users: (
                        x[ViewKeys.Users].set_difference(usernames)
                    )
                }
            )
            .run(conn)
        )

    except Exception as e:
        logger.exception(e)

    return data


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
            .table(ViewCollections.Views)
            .get(view_name)
            .delete()
            .run(conn)
        )

    except Exception as e:
        logger.exception(e)

    return data


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
                .table(ViewCollections.Views)
                .get(view_name)
                .delete()
            )
            .run(conn)
        )

    except Exception as e:
        logger.exception(e)

    return data

@time_it
@db_create_close
@return_status_tuple
def update_usernames_for_view(usernames, view, conn=None):
    """Update the usernames for views
    Args:
        usernames (list): List of usernames that you are updating
        view (str): The name of the view, you are adding the users too.

    Basic Usage::
        >>> from vFense.user._db import update_usernames_for_views
        >>> usernames = ['admin', 'shaolin']
        >>> views = 'foo'
        >>> update_usernames_for_views(views, usernames)

    Returns:
        Tuple (status_code, count, error, generated ids)
        >>> (2001, 1, None, [])
    """
    data = {}
    try:
        data = (
            r
            .table(ViewCollections.Views)
            .get(view)
            .update(
                lambda y:
                {
                    ViewKeys.Users: (
                        y[ViewKeys.Users].set_union(usernames)
                    )
                }
            )
            .run(conn)
        )

    except Exception as e:
        logger.exception(e)

    return data

@time_it
@db_create_close
@return_status_tuple
def update_usernames_for_views(views, usernames, conn=None):
    """Update the usernames for views
    Args:
        views (list): list of views to add to the user.
        usernames (list): List of usernames that you are updating

    Basic Usage::
        >>> from vFense.user._db import update_usernames_for_views
        >>> usernames = ['admin', 'shaolin']
        >>> views = ['foo', 'bar']
        >>> update_usernames_for_views(views, usernames)

    Returns:
        Tuple (status_code, count, error, generated ids)
        >>> (2001, 1, None, [])
    """
    data = {}
    try:
        data = (
            r
            .expr(views)
            .for_each(
                lambda x:
                r
                .table(ViewCollections.Views)
                .get(x)
                .update(
                    lambda y:
                    {
                        ViewKeys.Users: (
                            y[ViewKeys.Users].set_union(usernames)
                        )
                    }
                )
            )
            .run(conn)
        )

    except Exception as e:
        logger.exception(e)

    return data


@time_it
@db_create_close
@return_status_tuple
def update_children_for_view(view, child, conn=None):
    """Update the children for views
    Args:
        view (string): The view you are updating.
        child (string): Adding a child to the current children

    Basic Usage::
        >>> from vFense.user._db import update_children_for_view
        >>> children = 'shaolin'
        >>> views = 'foo'
        >>> update_children_for_view(views, children)

    Returns:
        Tuple (status_code, count, error, generated ids)
        >>> (2001, 1, None, [])
    """
    data = {}
    try:
        data = (
            r
            .table(ViewCollections.Views)
            .get(view)
            .update(
                {
                    ViewKeys.Children: (
                        r.row[ViewKeys.Children].set_insert(child)
                    )
                }
            )
            .run(conn)
        )

    except Exception as e:
        logger.exception(e)

    return data
