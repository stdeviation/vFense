import logging
from vFense import VFENSE_LOGGING_CONFIG

from vFense.core._constants import *
from vFense.core.user._db_model import (
    UserKeys, UserCollections, UserMappedKeys
)
from vFense.core.user._constants import *
from vFense.core.group._db_model import (
    GroupCollections, GroupKeys, GroupsPerUserKeys,
    GroupsPerUserIndexes
)
from vFense.core.view._db_model import ViewMappedKeys
from vFense.core.view._constants import *
from vFense.core.permissions._constants import *
from vFense.core.decorators import return_status_tuple, time_it
from vFense.db.client import db_create_close, r

logging.config.fileConfig(VFENSE_LOGGING_CONFIG)
logger = logging.getLogger('rvapi')


@time_it
@db_create_close
def fetch_user(username, without_fields=None, conn=None):
    """Retrieve a user from the database
    Args:
        username (str): Name of the user.

    Kwargs:
        without_fields (list): List of fields you do not want to include.

    Basic Usage:
        >>> from vFense.user._db import fetch_user
        >>> username = 'admin'
        >>> fetch_user(username, without_fields=['password'])

    Returns:
        Dictionary of user properties.
        {
            u'current_view': u'default',
            u'enabled': True,
            u'full_name': u'TopPatchAgentCommunicationAccount',
            u'default_view': u'default',
            u'user_name': u'agent',
            u'email': u'admin@toppatch.com'
        }
    """
    data = {}
    try:
        if not without_fields:
            data = (
                r
                .table(UserCollections.Users)
                .get(username)
                .run(conn)
            )

        else:
            data = (
                r
                .table(UserCollections.Users)
                .get_all(username)
                .without(without_fields)
                .run(conn)
            )
            if data:
                data = data[0]
            else:
                data = {}

    except Exception as e:
        logger.exception(e)

    return(data)


@time_it
@db_create_close
def fetch_usernames(is_global=False, conn=None):
    """Retrieve a list of usernames from the database
    Kwargs:
        is_global (bool): Only search for global users.

    Basic Usage:
        >>> from vFense.user._db import fetch_usernames
        >>> is_global = True
        >>> fetch_usernames(is_global)

    Returns:
        List of usernames
    """
    data = []
    try:
        if is_global:
            data = list(
                r
                .table(UserCollections.Users)
                .filter(lambda x: x[UserKeys.Global] == False)
                .map(lambda x: x[UserKeys.UserName])
                .run(conn)
            )

        else:
            data = list(
                r
                .table(UserCollections.Users)
                .filter(lambda x: x[UserKeys.Global] == False)
                .map(lambda x: x[UserKeys.UserName])
                .run(conn)
            )

    except Exception as e:
        logger.exception(e)

    return(data)


@time_it
@db_create_close
def fetch_user_and_all_properties(username, conn=None):
    """Retrieve a user and all of its properties
        This query is beautiful :)
    Args:
        username (str): Name of the user.

    Basic Usage:
        >>> from vFense.user._db import fetch_user_and_all_properties
        >>> username = 'admin'
        >>> fetch_user_and_all_properties(username')

    Returns:
        Dictionary of user properties.
        {
            "current_view": "default",
            "views": [
                {
                    "admin": true,
                    "name": "default"
                }
            ],
            "groups": [
                {
                    "group_id": "1b74a706-34e5-482a-bedc-ffbcd688f066",
                    "group_name": "Administrator"
                }
            ],
                "default_view": "default",
                "user_name": "admin",
                "permissions": [
                    "administrator"
                ]
        }
    """
    data = {}
    map_hash = (
        {
            UserKeys.DefaultView: r.row[UserKeys.DefaultView],
            UserKeys.CurrentView: r.row[UserKeys.CurrentView],
            UserKeys.Email: r.row[UserKeys.Email],
            UserKeys.FullName: r.row[UserKeys.FullName],
            UserKeys.UserName: r.row[UserKeys.UserName],
            UserKeys.Enabled: r.row[UserKeys.Enabled],
            UserKeys.Global: r.row[UserKeys.Global],
            UserMappedKeys.Groups: (
                r
                .table(GroupCollections.GroupsPerUser)
                .get_all(username, index=GroupsPerUserIndexes.UserName)
                .coerce_to('array')
                .pluck(GroupsPerUserKeys.GroupId, GroupsPerUserKeys.GroupName)
            ),
            UserMappedKeys.Views: (
                r
                .expr(r.row[UserKeys.Views])
                .map(lambda x:
                    {
                        Permissions.ADMINISTRATOR: r.branch(
                            r
                            .table(GroupCollections.GroupsPerUser)
                            .get_all(username, index=GroupsPerUserIndexes.UserName)
                            .coerce_to('array')
                            .eq_join(lambda y:
                                y[GroupKeys.GroupName],
                                r.table(GroupCollections.Groups),
                                index=GroupsPerUserIndexes.GroupName
                            )
                            .zip()
                            .filter(
                                lambda z:
                                z[GroupKeys.Permissions]
                                .contains(Permissions.ADMINISTRATOR)
                            )
                            .filter(
                                lambda z:
                                z[GroupKeys.Views]
                                .contains(x)
                            ),
                            True,
                            False
                        ),
                        ViewMappedKeys.ViewName: x[ViewMappedKeys.ViewName]
                    }
                )
            ),
            UserMappedKeys.Permissions: (
                r
                .table(GroupCollections.GroupsPerUser)
                .get_all(username, index=GroupsPerUserIndexes.UserName)
                .coerce_to('array')
                .eq_join(lambda x:
                    x[GroupKeys.GroupName],
                    r.table(GroupCollections.Groups),
                    index=GroupsPerUserIndexes.GroupName
                )
                .zip()
                .map(lambda x: x[GroupKeys.Permissions])[0]
            )
        }
    )

    try:
        data = (
            r
            .table(UserCollections.Users)
            .get_all(username)
            .map(map_hash)
            .run(conn)
        )
        if data:
            data = data[0]

    except Exception as e:
        logger.exception(e)

    return(data)


@time_it
@db_create_close
def fetch_users_and_all_properties(view_name=None, conn=None):
    """Retrieve a user and all of its properties
        This query is beautiful :)
    Kwargs:
        view_name (str): Name of the view, where the users belong to.

    Basic Usage:
        >>> from vFense.user._db import fetch_users_and_all_properties
        >>> view_name = 'default'
        >>> fetch_user_and_all_properties(username')

    Returns:
        List of users and their properties.
        [
            {
                "current_view": "default",
                "views": [
                    {
                        "admin": true,
                        "name": "default"
                    }
                ],
                "groups": [
                    {
                        "group_id": "1b74a706-34e5-482a-bedc-ffbcd688f066",
                        "group_name": "Administrator"
                    }
                ],
                    "default_view": "default",
                    "user_name": "admin",
                    "permissions": [
                        "administrator"
                    ]
            }
        ]
    """
    data = []
    map_hash = (lambda x:
        {
            UserKeys.DefaultView: x[UserKeys.DefaultView],
            UserKeys.CurrentView: x[UserKeys.CurrentView],
            UserKeys.UserName: x[UserKeys.UserName],
            UserMappedKeys.Groups: (
                r
                .table(GroupCollections.GroupsPerUser)
                .get_all(x
                    [GroupsPerUserKeys.UserName],
                    index=GroupsPerUserIndexes.UserName
                )
                .coerce_to('array')
                .pluck(GroupsPerUserKeys.GroupId, GroupsPerUserKeys.GroupName)
            ),
            UserMappedKeys.Views: (
                r
                .table(ViewCollections.ViewsPerUser)
                .get_all(
                    x[ViewPerUserKeys.UserName],
                    index=ViewPerUserIndexes.UserName
                )
                .coerce_to('array')
                .map(lambda y:
                    {
                        Permissions.ADMINISTRATOR: r.branch(
                            r
                            .table(GroupCollections.GroupsPerUser)
                            .get_all(
                                y[GroupsPerUserKeys.UserName],
                                index=GroupsPerUserIndexes.UserName
                            )
                            .coerce_to('array')
                            .eq_join(lambda z:
                                z[GroupKeys.GroupName],
                                r.table(GroupCollections.Groups),
                                index=GroupsPerUserIndexes.GroupName
                            )
                            .zip()
                            .filter({GroupsPerUserKeys.UserName: y[GroupsPerUserKeys.UserName]})
                            .filter(
                                lambda a:
                                a[GroupKeys.Permissions]
                                .contains(Permissions.ADMINISTRATOR)
                            ).distinct(),
                            True,
                            False
                        ),
                        ViewPerUserKeys.ViewName: y[ViewPerUserKeys.ViewName]
                    }
                )
            ),
            UserMappedKeys.Permissions: (
                r
                .table(GroupCollections.GroupsPerUser)
                .get_all(x[GroupsPerUserKeys.UserName], index=GroupsPerUserIndexes.UserName)
                .coerce_to('array')
                .eq_join(lambda b:
                    b[GroupKeys.GroupName],
                    r.table(GroupCollections.Groups),
                    index=GroupsPerUserIndexes.GroupName
                )
                .zip()
                .map(lambda b: b[GroupKeys.Permissions])[0]
            )
        }
    )

    try:
        if view_name:
            data = list(
                r
                .table(ViewCollections.ViewsPerUser)
                .get_all(
                    view_name, index=ViewPerUserIndexes.ViewName
                )
                .pluck(ViewPerUserKeys.ViewName, ViewPerUserKeys.UserName)
                .distinct()
                .eq_join(lambda x:
                    x[UserKeys.UserName],
                    r.table(UserCollections.Users)
                )
                .zip()
                .map(map_hash)
                .run(conn)
            )

        else:
            data = list(
                r
                .table(UserCollections.Users)
                .map(map_hash)
                .run(conn)
            )

    except Exception as e:
        logger.exception(e)

    return(data)

@time_it
@db_create_close
@return_status_tuple
def user_status_toggle(username, conn=None):
    """Enable or disable a user
    Args:
        username (str): The username you are enabling or disabling

    Basic Usage:
        >>> from vFense.user._db import status_toggle
        >>> username = 'tester'
        >>> status_toggle(username)

    Returns:
        Tuple (status_code, count, error, generated ids)
        >>> (2001, 1, None, [])
    """
    try:
        toggled = (
            r
            .table(UserCollections.Users)
            .get(username)
            .update(
                {
                    UserKeys.Enabled: (
                        r.branch(
                            r.row[UserKeys.Enabled] == True,
                            False,
                            True
                        )
                    )
                }
            )
            .run(conn)
        )

    except Exception as e:
        logger.exception(e)

    return(toggled)


@time_it
@db_create_close
def fetch_users(
    view_name=None, username=None,
    without_fields=None, conn=None
    ):
    """Retrieve all users that is in the database by view_name or
        all of the views or by regex.

    Kwargs:
        view_name (str): Name of the view, where the agent
            is located.
        username (str): Name of the user you are searching for.
            This is a regular expression match.
        without_fields (list): List of fields you do not want to include.

    Basic Usage:
        >>> from vFense.user._db import fetch_users
        >>> view_name = 'default'
        >>> username = 'al'
        >>> without_fields = ['password']
        >>> fetch_users(view_name, username, without_field)

    Returns:
        List of users:
        [
            {
                "current_view": "default",
                "email": "test@test.org",
                "full_name": "is doing it",
                "default_view": "default",
                "user_name": "alien",
                "id": "ba9682ef-7adf-4916-8002-9637485b30d8",
                "view_name": "default"
            }
        ]
    """
    data = []
    try:
        if not view_name and not username and not without_fields:
            data = list(
                r
                .table(UserCollections.Users)
                .run(conn)
            )

        elif not view_name and not username and without_fields:
            data = list(
                r
                .table(UserCollections.Users)
                .without(without_fields)
                .run(conn)
            )

        elif not view_name and username and without_fields:
            data = list(
                r
                .table(ViewCollections.ViewsPerUser)
                .filter(
                    lambda x:
                    x[ViewPerUserKeys.UserName].match("(?i)" + username)
                )
                .eq_join(
                    lambda x:
                    x[ViewPerUserKeys.UserName],
                    r.table(UserCollections.Users)
                )
                .zip()
                .without(without_fields)
                .run(conn)
            )

        elif view_name and username and without_fields:
            data = list(
                r
                .table(ViewCollections.ViewsPerUser)
                .get_all(
                    view_name, index=ViewPerUserIndexes.ViewName
                )
                .filter(
                    lambda x:
                    x[ViewPerUserKeys.UserName].match("(?i)" + username)
                )
                .eq_join(
                    lambda x:
                    x[ViewPerUserKeys.UserName],
                    r.table(UserCollections.Users)
                )
                .zip()
                .without(without_fields)
                .run(conn)
            )

        elif view_name and not username and not without_fields:
            data = list(
                r
                .table(ViewCollections.ViewsPerUser)
                .get_all(
                    view_name, index=ViewPerUserIndexes.ViewName
                )
                .eq_join(
                    lambda x:
                    x[ViewPerUserKeys.UserName],
                    r.table(UserCollections.Users)
                )
                .zip()
                .run(conn)
            )

        elif view_name and not username and without_fields:
            data = list(
                r
                .table(ViewCollections.ViewsPerUser)
                .get_all(
                    view_name, index=ViewPerUserIndexes.ViewName
                )
                .eq_join(
                    lambda x:
                    x[ViewPerUserKeys.UserName],
                    r.table(UserCollections.Users)
                )
                .zip()
                .without(without_fields)
                .run(conn)
            )

        elif view_name and username and not without_fields:
            data = list(
                r
                .table(ViewCollections.ViewsPerUser)
                .get_all(
                    view_name, index=ViewPerUserIndexes.ViewName
                )
                .filter(
                    lambda x:
                    x[ViewPerUserKeys.UserName].match("(?i)" + username)
                )
                .eq_join(
                    lambda x:
                    x[ViewPerUserKeys.UserName],
                    r.table(UserCollections.Users)
                )
                .zip()
                .run(conn)
            )

    except Exception as e:
        logger.exception(e)

    return(data)


@time_it
@db_create_close
@return_status_tuple
def insert_user(user_data, conn=None):
    """ Insert a new user and its properties into the database
        This function should not be called directly.
    Args:
        user_data(list|dict): Can either be a list of dictionaries or a dictionary
            of the data you are inserting.

    Basic Usage:
        >>> from vFense.user._db import insert_user_data
        >>> user_data = {'view_name': 'vFense', 'needs_reboot': 'no'}
        >>> insert_user_data(user_data)

    Returns:
        Tuple (status_code, count, error, generated ids)
        >>> (2001, 1, None, [])
    """
    data = {}
    try:
        data = (
            r
            .table(UserCollections.Users)
            .insert(user_data)
            .run(conn)
        )

    except Exception as e:
        logger.exception(e)

    return(data)


@time_it
@db_create_close
@return_status_tuple
def update_user(username, user_data, conn=None):
    """Update  user's properties
    Args:
        username (str): username of the user you are updating
        user_data (list|dict): Dictionary of the data you are updating

    Basic Usage::
        >>> from vFense.user._db import update_user
        >>> username = 'admin'
        >>> data = {'production_level': 'Development', 'needs_reboot': 'no'}
        >>> update_user(username, data)

    Returns:
        Tuple (status_code, count, error, generated ids)
        >>> (2001, 1, None, [])
    """
    data = {}
    try:
        data = (
            r
            .table(UserCollections.Users)
            .get(username)
            .update(user_data)
            .run(conn)
        )

    except Exception as e:
        logger.exception(e)

    return(data)

@time_it
@db_create_close
@return_status_tuple
def update_views_for_user(username, views, conn=None):
    """Update  user's properties
    Args:
        username (str): username of the user you are updating
        views (list): list of views to add to the user.

    Basic Usage::
        >>> from vFense.user._db import update_views_for_user
        >>> username = 'admin'
        >>> views = ['foo', 'bar']
        >>> update_views_for_user(username, view)

    Returns:
        Tuple (status_code, count, error, generated ids)
        >>> (2001, 1, None, [])
    """
    data = {}
    try:
        data = (
            r
            .table(UserCollections.Users)
            .get(username)
            .update(
                {
                    UserKeys.Views: (
                        r.row[UserKeys.Views].set_union(views)
                    )
                }
            )
            .run(conn)
        )

    except Exception as e:
        logger.exception(e)

    return(data)

@time_it
@db_create_close
@return_status_tuple
def update_views_for_users(usernames, views, conn=None):
    """Update  user's properties
    Args:
        usernames (list): List of usernames that you are updating
        views (list): list of views to add to the user.

    Basic Usage::
        >>> from vFense.user._db import update_views_for_users
        >>> usernames = ['admin', 'shaolin']
        >>> views = ['foo', 'bar']
        >>> update_views_for_users(usernames, views)

    Returns:
        Tuple (status_code, count, error, generated ids)
        >>> (2001, 1, None, [])
    """
    data = {}
    try:
        data = (
            r
            .expr(usernames)
            .for_each(
                lambda x:
                r
                .table(UserCollections.Users)
                .get(x)
                .update(
                    {
                        UserKeys.Views: (
                            r.row[UserKeys.Views].set_union(views)
                        )
                    }
                )
            )
            .run(conn)
        )

    except Exception as e:
        logger.exception(e)

    return(data)


@time_it
@db_create_close
@return_status_tuple
def delete_user(username, conn=None):
    """ Delete a user and all of its properties
    Args:
        username (str): username of the user you are deleteing.

    Basic Usage::
        >>> from vFense.user._db import delete_user
        >>> username = 'admin'
        >>> delete_user(username)

    Returns:
        Tuple (status_code, count, error, generated ids)
        >>> (2001, 1, None, [])
    """
    data = {}
    try:
        data = (
            r
            .table(UserCollections.Users)
            .get(username)
            .delete()
            .run(conn)
        )

    except Exception as e:
        logger.exception(e)

    return(data)


@time_it
@db_create_close
@return_status_tuple
def delete_users(usernames, conn=None):
    """ Delete a user and all of its properties
    Args:
        usernames (list): username of the user you are deleteing.

    Basic Usage:
        >>> from vFense.user._db import delete_users
        >>> usernames = ['admin', 'foo', 'bar']
        >>> delete_users(usernames)

    Returns:
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
                .table(UserCollections.Users)
                .get(username)
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
def delete_views_in_user(username, view_names, conn=None):
    """Remove a view from a user or remove all views for a user.
    Args:
        username (str): Name of the user.
        view_names (list): List of view_names.

    Basic Usage:
        >>> from vFense.view._db delete_views_in_user
        >>> username = 'agent_api'
        >>> view_names = ['Foo Bar', 'Test 1']
        >>> delete_views_in_user(username, view_names)

    Returns:
        Tuple (status_code, count, error, generated ids)
        >>> (2001, 1, None, [])
    """
    data = {}
    try:
        data = (
            r
            .table(UserCollections.Users)
            .get(username)
            .update(
                {
                    UserKeys.Views: (
                        r.row[UserKeys.Views].set_difference(view_names)
                    )
                }
            )
            .run(conn)
        )

    except Exception as e:
        logger.exception(e)

    return(data)
