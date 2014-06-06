import logging, logging.config
from vFense import VFENSE_LOGGING_CONFIG

from vFense.core.group._db_model import *
from vFense.core.group._constants import *
from vFense.core.decorators import return_status_tuple, time_it
from vFense.db.client import db_create_close, r

logging.config.fileConfig(VFENSE_LOGGING_CONFIG)
logger = logging.getLogger('rvapi')


@db_create_close
def fetch_group(group_id, conn=None):
    """Retrieve a group from the database
    Args:
        group_id: 36 Character UUID.

    Basic Usage:
        >>> from vFense.group._db import fetch_group
        >>> group_id = 'a7d4690e-5851-4d92-9626-07e16acaea1f'
        >>> fetch_group(group_id)

    Returns:
        Returns a Dict of the properties of a group
        {
            u'group_name': u'Administrator',
            u'view_name': u'default',
            u'id': u'8757b79c-7321-4446-8882-65457f28c78b',
            u'Permissions': [
                u'administrator'
            ]
        }
    """
    data = {}
    try:
        data = (
            r
            .table(GroupCollections.Groups)
            .get(group_id)
            .run(conn)
        )

    except Exception as e:
        logger.exception(e)

    return(data)


@db_create_close
def fetch_group_properties(group_id, conn=None):
    """Retrieve a group and all of its properties.
    Args:
        group_id: 36 Character UUID.

    Basic Usage:
        >>> from vFense.group._db import fetch_group_properties
        >>> group_id = 'a7d4690e-5851-4d92-9626-07e16acaea1f'
        >>> fetch_group_properties(group_id)

    Returns:
        Returns a Dict of the properties of a group
        {
            "users": [
                {
                    "user_name": "admin"
                },
                {
                    "user_name": "agent_api"
                }
            ],
            "permissions": [
                "administrator"
            ],
            "group_name": "Administrator",
            "id": "1b74a706-34e5-482a-bedc-ffbcd688f066",
            "view_name": "default"
        }
    """
    map_hash = (lambda x:
        {
            GroupKeys.GroupId: x[GroupKeys.GroupId],
            GroupKeys.GroupName: x[GroupKeys.GroupName],
            GroupKeys.ViewName: x[GroupKeys.ViewName],
            GroupKeys.Permissions: x[GroupKeys.Permissions],
            GroupKeys.Users: (
                r
                .table(GroupCollections.GroupsPerUser)
                .get_all(group_id, index=GroupsPerUserIndexes.GroupId)
                .coerce_to('array')
                .pluck(GroupsPerUserKeys.UserName)
            )
        }
    )
    data = {}
    try:
        data = (
            r
            .table(GroupCollections.Groups)
            .get_all(group_id)
            .map(map_hash)
            .run(conn)
        )
        if data:
            data = data[0]

    except Exception as e:
        logger.exception(e)

    return(data)

@db_create_close
def fetch_properties_for_all_groups(view_name=None, conn=None):
    """Retrieve properties for all groupcs.
    Kwargs:
        view_name: Name of the view, which the group is part of.

    Basic Usage:
        >>> from vFense.group._db import fetch_properties_for_all_groups
        >>> view_name = 'test'
        >>> fetch_properties_for_all_groups(view_name)

    Returns:
        Returns a List of a groups and their properties.
        [
            {
                "users": [
                    {
                        "user_name": "admin"
                    },
                    {
                        "user_name": "agent_api"
                    }
                ],
                "permissions": [
                    "install",
                    "uninstall"
                ],
                "group_name": "JR ADMIN",
                "id": "2171dff9-cf6d-4deb-9da3-18434acbd1c7",
                "view_name": "Test"
            },
        ]
    """
    map_hash = (lambda x:
        {
            GroupKeys.GroupId: x[GroupKeys.GroupId],
            GroupKeys.GroupName: x[GroupKeys.GroupName],
            GroupKeys.ViewName: x[GroupKeys.ViewName],
            GroupKeys.Permissions: x[GroupKeys.Permissions],
            GroupKeys.Users: (
                r
                .table(GroupCollections.GroupsPerUser)
                .get_all(
                    x[GroupKeys.GroupId],
                    index=GroupsPerUserIndexes.GroupId
                )
                .coerce_to('array')
                .pluck(GroupsPerUserKeys.UserName)
            )
        }
    )
    data = {}
    try:
        if view_name:
            data = list(
                r
                .table(GroupCollections.Groups)
                .get_all(view_name, index=GroupsPerUserIndexes.ViewName)
                .map(map_hash)
                .run(conn)
            )

        else:
            data = list(
                r
                .table(GroupCollections.Groups)
                .map(map_hash)
                .run(conn)
            )

    except Exception as e:
        logger.exception(e)

    return(data)


@time_it
@db_create_close
def fetch_group_by_name(
    group_name, view_name,
    fields_to_pluck=None, conn=None):
    """Retrieve a group by its name from the database
    Args:
        group_name (str): Name of group.
        view_name (str): name of the view, that the group belongs to.

    Kwargs:
        fields_to_pluck (list): List of fields you want to retrieve.

    Basic Usage:
        >>> from vFense.group._db import fetch_group_by_name
        >>> group_name = 'Administrator'
        >>> view_name = 'default'
        >>> fetch_group_by_name(group_name, view_name)

    Returns:
        Returns a Dict of the properties of a view
        {
            u'group_name': u'Administrator',
            u'view_name': u'default',
            u'id': u'8757b79c-7321-4446-8882-65457f28c78b',
            u'Permissions': [
                u'administrator'
            ]
        }
    """
    try:
        if fields_to_pluck:
            data = list(
                r
                .table(GroupCollections.Groups)
                .get_all(group_name, index=GroupIndexes.GroupName)
                .filter(
                    lambda x: x[GroupKeys.Views].contains(view_name)
                )
                .pluck(fields_to_pluck)
                .run(conn)
            )
        else:
            data = list(
                r
                .table(GroupCollections.Groups)
                .get_all(group_name, index=GroupIndexes.GroupName)
                .filter(
                    lambda x: x[GroupKeys.Views].contains(view_name)
                )
                .run(conn)
            )

        if len(data) == 1:
            data = data[0]

    except Exception as e:
        logger.exception(e)
        data = {}

    return(data)


@time_it
@db_create_close
def fetch_users_in_group(group_id, fields_to_pluck=None, conn=None):
    """Fetch all users for group_id
    Args:
        group_id (str): 36 Character UUID

    Kwargs:
        fields_to_pluck (list): List of fields you want to
        pluck from the database.

    Basic Usage:
        >>> from vFense.group._db import fetch_users_in_group
        >>> group_id = 'a7d4690e-5851-4d92-9626-07e16acaea1f'
        >>> fetch_users_in_group(group_id, [GroupsPerUserKeys.UserName])

    Returns:
        Returns a list of users
        [
            {
                u'user_name': u'testing123'
            },
            {
                u'user_name': u'tester'
            },
            {
                u'user_name': u'testing'
            }
        ]
    """
    data = []
    try:
        if fields_to_pluck:
            data = list(
                r
                .table(GroupCollections.GroupsPerUser)
                .get_all(group_id, index=GroupsPerUserIndexes.GroupId)
                .pluck(fields_to_pluck)
                .run(conn)
            )
        else:
            data = list(
                r
                .table(GroupCollections.GroupsPerUser)
                .get_all(group_id, index=GroupsPerUserIndexes.GroupId)
                .run(conn)
            )

    except Exception as e:
        logger.exception(e)

    return(data)



@time_it
@db_create_close
def fetch_usernames_in_group(group_id, conn=None):
    """Fetch all users for group_id
    Args:
        group_id (str): 36 Character UUID

    Kwargs:
        fields_to_pluck (list): List of fields you want to
        pluck from the database.

    Basic Usage:
        >>> from vFense.group._db import fetch_usernames_in_group
        >>> group_id = 'a7d4690e-5851-4d92-9626-07e16acaea1f'
        >>> fetch_usernames_in_group(group_id)

    Returns:
        Returns a list of users
        [
            'testing123'
            'tester'
            'testing'
        ]
    """
    data = []
    try:
        data = list(
            r
            .table(GroupCollections.Groups)
            .get(group_id)
            .run(conn)
        )
        if data:
            data = data[GroupKeys.Users]

    except Exception as e:
        logger.exception(e)

    return data


@time_it
@db_create_close
def fetch_groups_for_user(username, fields_to_pluck=None, conn=None):
    """Retrieve all groups for a user by username
    Args:
        username (str): Get all groups for which this user is part of.

    Kwargs:
        fields_to_pluck (list): List of fields you want to pluck
        from the database

    Basic Usage:
        >>> from vFense.group._db import fetch_groups_for_user
        >>> username = 'alien'
        >>> fetch_groups_for_user(username)

    Returns:
        Returns a list of groups that the user belongs to.
        [
            {
                u'group_name': u'FooLah',
                u'group_id': u'0834e656-27a5-4b13-ba56-635797d0d1fc',
                u'user_name': u'alien',
                u'id': u'ee54820c-cb4e-46a1-9d11-73afe8c4c4e3',
                u'view_name': u'default'
            },
            {
                u'group_name': u'Administrator',
                u'group_id': u'8757b79c-7321-4446-8882-65457f28c78b',
                u'user_name': u'alien',
                u'id': u'6bd51a04-fcec-46a7-bbe1-48c6221115ec',
                u'view_name': u'default'
            }
        ]
    """
    data = []
    try:
        if username and not fields_to_pluck:
            data = list(
                r
                .table(GroupCollections.GroupsPerUser)
                .get_all(username, index=GroupsPerUserIndexes.UserName)
                .run(conn)
            )

        elif username and fields_to_pluck:
            data = list(
                r
                .table(GroupCollections.GroupsPerUser)
                .get_all(username, index=GroupsPerUserIndexes.UserName)
                .pluck(fields_to_pluck)
                .run(conn)
            )

    except Exception as e:
        logger.exception(e)

    return(data)

@time_it
@db_create_close
def fetch_groupids_for_user(username, conn=None):
    """Retrieve a list of group ids that the user belongs to.
    Args:
        username (str): Get all groups for which this user is part of.

    Basic Usage:
        >>> from vFense.group._db import fetch_groupids_for_user
        >>> username = 'alien'
        >>> fetch_groupids_for_user(username)

    Returns:
        Returns a list of group ids that the user belongs to.
        ['']
    """
    data = []
    try:
        data = list(
            r
            .table(GroupCollections.Groups)
            .get_all(username, index=GroupIndexes.Users)
            .map(lambda group_id: group_id[GroupKeys.GroupId])
            .run(conn)
        )

    except Exception as e:
        logger.exception(e)

    return data


@time_it
@db_create_close
def user_exist_in_group(username, group_id, conn=None):
    """Return True if and user is part of group_id
    Args:
        username (str): username.
        group_id (str): 36 Character UUID

    Basic Usage:
        >>> from vFense.group._db import user_exist_in_group
        >>> username = 'alien'
        >>> group_id = '0834e656-27a5-4b13-ba56-635797d0d1fc'
        >>> user_exist_in_group(username, group_id)

    Returns:
        Returns a boolean True or False
    """
    exist = False
    try:
        is_empty = (
            r
            .table(GroupCollections.Groups)
            .get_all(group_id)
            .filter(
                lambda x: x[GroupKeys.Users].contains(username)
            )
            .is_empty()
            .run(conn)
        )

        if not is_empty:
            exist = True

    except Exception as e:
        logger.exception(e)

    return(exist)


@time_it
@db_create_close
def usernames_exist_in_group_id(usernames, group_id, conn=None):
    """Return True if and user is part of group_id
    Args:
        usernames (list): List of usernames.
        group_id (str): 36 Character UUID

    Basic Usage:
        >>> from vFense.group._db import users_exist_in_group
        >>> usernames = ['alien', 'tester']
        >>> group_id = '0834e656-27a5-4b13-ba56-635797d0d1fc'
        >>> users_exist_in_group(usernames, group_id)

    Returns:
        Returns a boolean True or False
    """
    exist = False
    try:
        for username in usernames:
            is_empty = (
                r
                .table(GroupCollections.GroupsPerUser)
                .get_all(username, index=GroupsPerUserIndexes.UserName)
                .filter({GroupsPerUserKeys.GroupId: group_id})
                .is_empty()
                .run(conn)
            )
            if not is_empty:
                exist = True

    except Exception as e:
        logger.exception(e)

    return(exist)


@time_it
@db_create_close
def users_exist_in_group_ids(group_ids, conn=None):
    """Return True if and user is part of group_id
    Args:
        group_ids (list): List of group ids.

    Basic Usage:
        >>> from vFense.group._db import users_exist_in_group_ids
        >>> group_ids = ['0834e656-27a5-4b13-ba56-635797d0d1fc']
        >>> users_exist_in_group(group_ids)

    Returns:
        Returns a boolean True or False
    """
    exist = False
    try:
        for group_id in group_ids:
            is_empty = (
                r
                .table(GroupCollections.GroupsPerUser)
                .get_all(group_id, index=GroupsPerUserIndexes.GroupId)
                .is_empty()
                .run(conn)
            )
            if not is_empty:
                exist = True

    except Exception as e:
        logger.exception(e)

    return(exist)


@time_it
@db_create_close
def fetch_groups(
    view_name=None, groupname=None,
    fields_to_pluck=None, conn=None
    ):
    """Retrieve all groups that is in the database by view_name or
        all of the groups or by regex.

    Kwargs:
        view_name (str):  Name of the view,
        groupname (str):  Name of the group you are searching for.
            This is a regular expression match.
        fields_to_pluck (list):  List of fields you want to pluck
        from the database

    Basic Usage:
        >>> from vFense.group._db import fetch_groups
        >>> view_name = 'default'
        >>> groupname = 'fo'
        >>> fetch_groups(view_name, groupname)

    Returns:
        Returns a Dict of the properties of a group
        [
            {
                u'group_name': u'FooLee',
                u'view_name': u'default',
                u'id': u'5215a906-4b05-46fa-b0fc-4f55f974ebbc',
                u'Permissions': [
                    u'shutdown',
                    u'reboot'
                ]

            },
            {
                u'group_name': u'FooLah',
                u'view_name': u'default',
                u'id': u'1fbdd995-1a6b-4dc8-80a4-9ed23e32864e',
                u'Permissions': [
                    u'install',
                    u'uninstall'
                ]
            }
        ]
    """
    data = []
    try:
        if not view_name and not groupname and not fields_to_pluck:
            data = list(
                r
                .table(GroupCollections.Groups)
                .run(conn)
            )

        elif not view_name and not groupname and fields_to_pluck:
            data = list(
                r
                .table(GroupCollections.Groups)
                .pluck(fields_to_pluck)
                .run(conn)
            )

        elif not view_name and groupname and not fields_to_pluck:
            data = list(
                r
                .table(GroupCollections.Groups)
                .filter(
                    lambda x:
                    x[GroupKeys.GroupName].match("(?i)" + groupname)
                )
                .run(conn)
            )

        elif not view_name and groupname and fields_to_pluck:
            data = list(
                r
                .table(GroupCollections.Groups)
                .filter(
                    lambda x:
                    x[GroupKeys.GroupName].match("(?i)" + groupname)
                )
                .pluck(fields_to_pluck)
                .run(conn)
            )

        elif view_name and not groupname and not fields_to_pluck:
            data = list(
                r
                .table(GroupCollections.Groups)
                .get_all(
                    view_name, index=GroupIndexes.ViewName
                )
                .run(conn)
            )

        elif view_name and not groupname and fields_to_pluck:
            data = list(
                r
                .table(GroupCollections.Groups)
                .get_all(
                    view_name, index=GroupIndexes.ViewName
                )
                .pluck(fields_to_pluck)
                .run(conn)
            )

        elif view_name and groupname and not fields_to_pluck:
            data = list(
                r
                .table(GroupCollections.Groups)
                .get_all(
                    view_name, index=GroupIndexes.ViewName
                )
                .filter(
                    lambda x:
                    x[GroupKeys.GroupName].match("(?i)" + groupname)
                )
                .run(conn)
            )

        elif view_name and groupname and fields_to_pluck:
            data = list(
                r
                .table(GroupCollections.Groups)
                .get_all(
                    view_name, index=GroupIndexes.ViewName
                )
                .filter(
                    lambda x:
                    x[GroupKeys.GroupName].match("(?i)" + groupname)
                )
                .pluck(fields_to_pluck)
                .run(conn)
            )

    except Exception as e:
        logger.exception(e)

    return(data)


@time_it
@db_create_close
@return_status_tuple
def insert_group(group_data, conn=None):
    """ Insert a new group into the database
    Args:
        group_data (list|dict): Can either be a list of dictionaries or a dictionary
        of the data you are inserting.

    Basic Usage:
        >>> from vFense.group._db import insert_group
        >>> group_data = {'view_name': 'vFense', 'needs_reboot': 'no'}
        >>> insert_group(group_data)

    Return:
        Tuple (status_code, count, error, generated ids)
        >>> (2001, 1, None, [])
    """
    data = {}
    try:
        data = (
            r
            .table(GroupCollections.Groups)
            .insert(group_data)
            .run(conn)
        )

    except Exception as e:
        logger.exception(e)

    return(data)


@time_it
@db_create_close
@return_status_tuple
def insert_group_per_user(group_data, conn=None):
    """Add a group to a user, this function should not be called directly.
    Args:
        group_data (list|dict): Can either be a list of dictionaries or a dictionary
        of the data you are inserting.

    Basic Usage:
        >>> from vFense.group._db import insert_group_per_user
        >>> group_data = {'view_name': 'vFense', 'needs_reboot': 'no'}
        >>> insert_group_per_user(group_data)

    Return:
        Tuple (status_code, count, error, generated ids)
        >>> (2001, 1, None, [])
    """
    data = {}
    try:
        data = (
            r
            .table(GroupCollections.GroupsPerUser)
            .insert(group_data)
            .run(conn)
        )

    except Exception as e:
        logger.exception(e)

    return(data)


@time_it
@db_create_close
@return_status_tuple
def update_group(group_id, group_data, conn=None):
    """Update verious fields of a group
    Args:
        group_idi (str): group id  of the group you are updateing.

    Basic Usage::
        >>> from vFense.group._db import update_group
        >>> group_id = 'd081a343-cc6c-4f08-81d9-62a116fda025'
        >>> data = {'production_level': 'Development', 'needs_reboot': 'no'}
        >>> update_group(group_id)

    Return:
        Tuple (status_code, count, error, generated ids)
        >>> (2001, 1, None, [])
    """
    data = {}
    try:
        data = (
            r
            .table(GroupCollections.Groups)
            .get(group_id)
            .update(group_data)
            .run(conn)
        )

    except Exception as e:
        logger.exception(e)

    return(data)


@time_it
@db_create_close
@return_status_tuple
def delete_user_in_groups(username, group_ids, conn=None):
    """Remove a group from a user or remove all groups for a user.
    Args:
        username (str): Name of the user.
        group_ids (list): List of group_ids.

    Basic Usage:
        >>> from vFense.view._db import delete_groups_in_user
        >>> username = 'agent_api'
        >>> group_ids = [
            u'6c724340-265a-434e-97ed-7951b2844fdb',
            u'a5f07b40-ef18-4a23-918f-95e463e0a7c9'
        ]
        >>> delete_groups_in_user(username, group_ids)

    Returns:
        Tuple (status_code, count, error, generated ids)
        >>> (2001, 1, None, [])
    """
    data = {}
    try:
        data = (
            r
            .table(GroupCollections.Groups)
            .get_all(username, index=GroupIndexes.Users)
            .update(
                {
                    GroupKeys.Users: (
                        r.row[GroupKeys.Users].set_difference([username])
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
def delete_users_in_group(group_id, usernames, conn=None):
    """Remove a group from a user or remove all groups for a user.
    Args:
        group_id (str): 36 character group UUID
        usernames (list): List of the usernames.

    Basic Usage::
        >>> from vFense.group._db delete_users_from_group
        >>> usernames = ['user names goes here']
        >>> group_id = 'fc88f36c-d911-4a8b-aad3-3728b3d1a607'
        >>> delete_users_from_group(group_id, usernames)

    Return:
        Tuple (status_code, count, error, generated ids)
        >>> (2001, 1, None, [])
    """
    data = {}
    try:
        data = (
            r
            .table(GroupCollections.Groups)
            .get(group_id)
            .update(
                lambda x:
                {
                    GroupKeys.Users: (
                        x[GroupKeys.Users].set_difference(usernames)
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
def delete_views_in_group(group_id, views, conn=None):
    """Remove a group from a user or remove all groups for a user.
    Args:
        group_id (str): 36 character group UUID
        views (list): List of views.

    Basic Usage::
        >>> from vFense.group._db delete_views_in_group
        >>> views = ['Name of view goes here']
        >>> delete_views_in_group(group_id, views)

    Return:
        Tuple (status_code, count, error, generated ids)
        >>> (2001, 1, None, [])
    """
    data = {}
    try:
        data = (
            r
            .table(GroupCollections.Groups)
            .get(group_id)
            .update(
                lambda x:
                {
                    GroupKeys.Views: (
                        x[GroupKeys.Views].set_difference(views)
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
def delete_groups_from_view(view, conn=None):
    """Remove a group from a user or remove all groups for a user.
    Args:
        view (str): Name of view to remove group from.

    Basic Usage::
        >>> from vFense.group._db delete_groups_from_view
        >>> view = 'Name of view goes here'
        >>> delete_groups_from_view(view)

    Return:
        Tuple (status_code, count, error, generated ids)
        >>> (2001, 1, None, [])
    """
    data = {}
    try:
        data = (
            r
            .table(GroupCollections.Groups)
            .get_all(view, index=GroupIndexes.Views)
            .update(
                lambda x:
                {
                    GroupKeys.Views: (
                        x[GroupKeys.Views].set_difference(views)
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
def add_users_to_group(group_id, usernames, conn=None):
    """Add users to a group
    Args:
        group_id (str): 36 character group UUID
        usernames (list): List of the usernames.

    Basic Usage::
        >>> from vFense.group._db add_users_to_group
        >>> usernames = ['user names goes here']
        >>> group_id = 'fc88f36c-d911-4a8b-aad3-3728b3d1a607'
        >>> add_users_to_group(group_id, usernames)

    Return:
        Tuple (status_code, count, error, generated ids)
        >>> (2001, 1, None, [])
    """
    data = {}
    try:
        data = (
            r
            .table(GroupCollections.Groups)
            .get(group_id)
            .update(
                lambda x:
                {
                    GroupKeys.Users: (
                        x[GroupKeys.Users].set_union(usernames)
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
def add_user_to_groups(group_ids, user, conn=None):
    """Add 1 or multiple users to multiple groups.
    Args:
        group_ids (list): List of group_ids.
        user (string): username.

    Basic Usage::
        >>> from vFense.group._db add_user_to_groups
        >>> users = 'Name of user goes here'
        >>> group_ids = ['fc88f36c-d911-4a8b-aad3-3728b3d1a607']
        >>> add_user_to_groups(group_ids, user)

    Return:
        Tuple (status_code, count, error, generated ids)
        >>> (2001, 1, None, [])
    """
    data = {}
    try:
        data = (
            r
            .expr(group_ids)
            .for_each(
                lambda group_id:
                r
                .table(GroupCollections.Groups)
                .get(group_id)
                .update(
                    lambda x:
                    {
                        GroupKeys.Users: (
                            x[GroupKeys.Users].set_insert(user)
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
def add_users_to_groups(group_ids, users, conn=None):
    """Add 1 or multiple users to multiple groups.
    Args:
        group_ids (list): List of group_ids.
        users (list): List of users.

    Basic Usage::
        >>> from vFense.group._db add_users_to_groups
        >>> users = ['Name of user goes here']
        >>> group_ids = ['fc88f36c-d911-4a8b-aad3-3728b3d1a607']
        >>> add_users_to_groups(group_ids, users)

    Return:
        Tuple (status_code, count, error, generated ids)
        >>> (2001, 1, None, [])
    """
    data = {}
    try:
        data = (
            r
            .expr(group_ids)
            .for_each(
                lambda group_id:
                r
                .table(GroupCollections.Groups)
                .get(group_id)
                .update(
                    lambda x:
                    {
                        GroupKeys.Users: (
                            x[GroupKeys.Users].set_union(users)
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
def add_views_to_group(group_id, views, conn=None):
    """Add 1 or multiple views to which this group belongs too.
    Args:
        group_id (str): 36 character group UUID
        views (list): List of views.

    Basic Usage::
        >>> from vFense.group._db add_views_to_group
        >>> views = ['Name of view goes here']
        >>> group_id = 'fc88f36c-d911-4a8b-aad3-3728b3d1a607'
        >>> add_views_to_group(group_id, views)

    Return:
        Tuple (status_code, count, error, generated ids)
        >>> (2001, 1, None, [])
    """
    data = {}
    try:
        data = (
            r
            .table(GroupCollections.Groups)
            .get(group_id)
            .update(
                lambda x:
                {
                    GroupKeys.Views: (
                        x[GroupKeys.Views].set_union(views)
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
def add_view_to_groups(group_ids, view, conn=None):
    """Add 1 or multiple views to multiple groups.
    Args:
        group_ids (list): List of group_ids.
        views (string): The name of the view.

    Basic Usage::
        >>> from vFense.group._db add_view_to_groups
        >>> view = 'Name of view goes here'
        >>> group_ids = ['fc88f36c-d911-4a8b-aad3-3728b3d1a607']
        >>> add_view_to_groups(group_ids, views)

    Return:
        Tuple (status_code, count, error, generated ids)
        >>> (2001, 1, None, [])
    """
    data = {}
    try:
        data = (
            r
            .expr(group_ids)
            .for_each(
                lambda group_id:
                r
                .table(GroupCollections.Groups)
                .get(group_id)
                .update(
                    lambda x:
                    {
                        GroupKeys.Views: (
                            x[GroupKeys.Views].set_insert(view)
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
def add_views_to_groups(group_ids, views, conn=None):
    """Add 1 or multiple views to multiple groups.
    Args:
        group_ids (list): List of group_ids.
        views (list): List of views.

    Basic Usage::
        >>> from vFense.group._db add_views_to_groups
        >>> views = ['Name of view goes here']
        >>> group_ids = ['fc88f36c-d911-4a8b-aad3-3728b3d1a607']
        >>> add_views_to_groups(group_ids, views)

    Return:
        Tuple (status_code, count, error, generated ids)
        >>> (2001, 1, None, [])
    """
    data = {}
    try:
        data = (
            r
            .expr(group_ids)
            .for_each(
                lambda group_id:
                r
                .table(GroupCollections.Groups)
                .get(group_id)
                .update(
                    lambda x:
                    {
                        GroupKeys.Views: (
                            x[GroupKeys.Views].set_union(views)
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
def delete_views_from_groups(group_ids, views, conn=None):
    """Remove 1 or multiple views from multiple groups.
    Args:
        group_ids (list): List of group_ids.
        views (list): List of views.

    Basic Usage::
        >>> from vFense.group._db delete_views_from_groups
        >>> views = ['Name of view goes here']
        >>> group_ids = ['fc88f36c-d911-4a8b-aad3-3728b3d1a607']
        >>> delete_views_from_groups(group_ids, views)

    Return:
        Tuple (status_code, count, error, generated ids)
        >>> (2001, 1, None, [])
    """
    data = {}
    try:
        data = (
            r
            .expr(group_ids)
            .for_each(
                lambda group_id:
                r
                .table(GroupCollections.Groups)
                .get(group_id)
                .update(
                    lambda x:
                    {
                        GroupKeys.Views: (
                            x[GroupKeys.Views].set_difference(views)
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
def delete_group(group_id, conn=None):
    """Delete a group from the database.
    Args:
        group_id (str): group id of the group you are deleteing

    Basic Usage::
        >>> from vFense.group._db import delete_group
        >>> group_id = 'd081a343-cc6c-4f08-81d9-62a116fda025'
        >>> delete_group(group_id)

    Return:
        Tuple (status_code, count, error, generated ids)
        >>> (2001, 1, None, [])
    """
    data = {}
    try:

        data = (
            r
            .table(GroupCollections.Groups)
            .get(group_id)
            .delete()
            .run(conn)
        )

    except Exception as e:
        logger.exception(e)

    return(data)


@time_it
@db_create_close
@return_status_tuple
def delete_groups(group_ids, conn=None):
    """Delete a group from the database.
    Args:
        group_ids (list): group ids of the group you are deleteing

    Basic Usage::
        >>> from vFense.group._db import delete_groups
        >>> group_ids = ['d081a343-cc6c-4f08-81d9-62a116fda025']
        >>> delete_groups(group_ids)

    Return:
        Tuple (status_code, count, error, generated ids)
        >>> (2001, 1, None, [])
    """
    data = {}
    try:

        data = (
            r
            .expr(group_ids)
            .for_each(
                lambda group_id:
                r
                .table(GroupCollections.Groups)
                .get(group_id)
                .delete()
            )
            .run(conn)
        )

    except Exception as e:
        logger.exception(e)

    return(data)
