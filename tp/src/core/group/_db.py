import logging

from vFense.core.group import *
from vFense.core.decorators import return_status_tuple, time_it
from vFense.db.client import db_create_close, r

logging.config.fileConfig('/opt/TopPatch/conf/logging.config')
logger = logging.getLogger('rvapi')


@time_it
@db_create_close
def fetch_group(group_id, conn=None):
    """
    Retrieve a group from the database
    :param group_id: 36 Character UUID.
    Basic Usage::
        >>> from vFense.group._db import fetch_group
        >>> group_id = 'a7d4690e-5851-4d92-9626-07e16acaea1f'
        >>> fetch_group(group_id)
        {
            u'current_customer': u'default',
            u'enabled': True,
            u'full_name': u'TopPatchAgentCommunicationAccount',
            u'default_customer': u'default',
            u'user_name': u'agent',
            u'email': u'admin@toppatch.com'
        }
    """
    data = {}
    try:
        data = (
            r
            .table(GroupsCollection)
            .get(group_id)
            .run(conn)
        )

    except Exception as e:
        logger.exception(e)

    return(data)


@time_it
@db_create_close
def fetch_group_by_name(
    group_name, customer_name,
    fields_to_pluck=None, conn=None):
    """
    Retrieve a group from the database
    :param group_name: name of group.
    :param customer_name: name of customer, that the customer belongs to.
    :param fields_to_pluck: (Optional) List of fields you want to retrieve.
    Basic Usage::
        >>> from vFense.group._db import fetch_group_by_name
        >>> group_name = 'Administrator'
        >>> customer_name = 'default'
        >>> fetch_group_by_name(group_name, customer_name)
        {
            u'group_name': u'Administrator',
            u'customer_name': u'default',
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
                .table(GroupsCollection)
                .filter(
                    {
                        GroupKeys.GroupName: group_name,
                        GroupKeys.CustomerName: customer_name
                    }
                )
                .pluck(fields_to_pluck)
                .run(conn)
            )
        else:
            data = list(
                r
                .table(GroupsCollection)
                .filter(
                    {
                        GroupKeys.GroupName: group_name,
                        GroupKeys.CustomerName: customer_name
                    }
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
    """
    Fetch all users for group_id
    :param group_id: 36 Character UUID
    :param fields_to_pluck: (Optional) List of fields you want to
        pluck from the database.
    Basic Usage::
        >>> from vFense.group._db import fetch_users_in_group
        >>> group_id = 'a7d4690e-5851-4d92-9626-07e16acaea1f'
        >>> fetch_users_in_group(group_id, ['user_name'])
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
                .table(GroupsPerUserCollection)
                .get_all(group_id, index=GroupsPerUserIndexes.GroupId)
                .pluck(fields_to_pluck)
                .run(conn)
            )
        else:
            data = list(
                r
                .table(GroupsPerUserCollection)
                .get_all(group_id, index=GroupsPerUserIndexes.GroupId)
                .run(conn)
            )

    except Exception as e:
        logger.exception(e)

    return(data)


@time_it
@db_create_close
def fetch_groups(
    customer_name=None, groupname=None,
    fields_to_pluck=None, conn=None
    ):
    """
    Retrieve all groups that is in the database by customer_name or
        all of the groups or by regex.

    :param customer_name: (Optional) Name of the customer,
        in which the group belongs too.

    :param groupname: (Optional) Name of the group you are searching for.
        This is a regular expression match.

    :param fields_to_pluck: (Optional) List of fields you want to pluck
        from the database

    Basic Usage::
        >>> from vFense.group._db import fetch_groups
        >>> customer_name = 'default'
        >>> groupname = 'fo'
        >>> fetch_groups(customer_name, groupname)
        [
            {
                u'group_name': u'FooLee',
                u'customer_name': u'default',
                u'id': u'5215a906-4b05-46fa-b0fc-4f55f974ebbc',
                u'Permissions': [
                    u'shutdown',
                    u'reboot'
                ]
                                                
            },
            {
                u'group_name': u'FooLah',
                u'customer_name': u'default',
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
        if not customer_name and not groupname and not fields_to_pluck:
            data = list(
                r
                .table(GroupsCollection)
                .run(conn)
            )

        elif not customer_name and not groupname and fields_to_pluck:
            data = list(
                r
                .table(GroupsCollection)
                .pluck(fields_to_pluck)
                .run(conn)
            )

        elif not customer_name and groupname and not fields_to_pluck:
            data = list(
                r
                .table(GroupsCollection)
                .filter(
                    lambda x:
                    x[GroupKeys.GroupName].match("(?i)" + groupname)
                )
                .run(conn)
            )

        elif not customer_name and groupname and fields_to_pluck:
            data = list(
                r
                .table(GroupsCollection)
                .filter(
                    lambda x:
                    x[GroupKeys.GroupName].match("(?i)" + groupname)
                )
                .pluck(fields_to_pluck)
                .run(conn)
            )

        elif customer_name and not groupname and not fields_to_pluck:
            data = list(
                r
                .table(GroupsCollection)
                .get_all(
                    customer_name, index=GroupIndexes.CustomerName
                )
                .run(conn)
            )

        elif customer_name and not groupname and fields_to_pluck:
            data = list(
                r
                .table(GroupsCollection)
                .get_all(
                    customer_name, index=GroupIndexes.CustomerName
                )
                .pluck(fields_to_pluck)
                .run(conn)
            )

        elif customer_name and groupname and not fields_to_pluck:
            data = list(
                r
                .table(GroupsCollection)
                .get_all(
                    customer_name, index=GroupIndexes.CustomerName
                )
                .filter(
                    lambda x:
                    x[GroupKeys.GroupName].match("(?i)" + groupname)
                )
                .run(conn)
            )

        elif customer_name and groupname and fields_to_pluck:
            data = list(
                r
                .table(GroupsCollection)
                .get_all(
                    customer_name, index=GroupIndexes.CustomerName
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
    """
    This function should not be called directly.
    :param group_data: Can either be a list of dictionaries or a dictionary
        of the data you are inserting.

    Basic Usage::
        >>> from vFense.group._db import insert_group
        >>> group_data = {'customer_name': 'vFense', 'needs_reboot': 'no'}
        >>> insert_group(group_data)
        >>> (2001, 1, None, [])
    """
    data = {}
    try:
        data = (
            r
            .table(GroupsCollection)
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
    """
    This function should not be called directly.
    :param group_data: Can either be a list of dictionaries or a dictionary
        of the data you are inserting.

    Basic Usage::
        >>> from vFense.group._db import insert_group_per_user
        >>> group_data = {'customer_name': 'vFense', 'needs_reboot': 'no'}
        >>> insert_group_per_user(group_data)
        >>> (2001, 1, None, [])
    """
    data = {}
    try:
        data = (
            r
            .table(GroupsPerUserCollection)
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
    """
    :param group_id: group id  of the group you are updateing.

    Basic Usage::
        >>> from vFense.group._db import update_group
        >>> group_id = 'd081a343-cc6c-4f08-81d9-62a116fda025'
        >>> data = {'production_level': 'Development', 'needs_reboot': 'no'}
        >>> update_group(group_id)
        >>> (2001, 1, None, [])
    """
    data = {}
    try:
        data = (
            r
            .table(GroupsCollection)
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
def delete_user_in_groups(username, group_id=None, conn=None):
    """
    :param username: username
    :param group_id: (Optional) 36 Character UUID

    Basic Usage::
        >>> from vFense.group._db delete_user_in_groups
        >>> username = 'agent_api'
        >>> delete_user_in_groups(username)
        >>> (2001, 1, None, [])
    """
    data = {}
    try:
        if group_id:
            data = (
                r
                .table(GroupsPerUserCollection)
                .filter(
                    {
                        GroupsPerUserKeys.UserName: username,
                        GroupsPerUserKeys.GroupId: group_id
                    }
                )
                .delete()
                .run(conn)
            )

        else:
            data = (
                r
                .table(GroupsPerUserCollection)
                .filter(
                    {
                        GroupsPerUserKeys.UserName: username,
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
def delete_group(group_id, conn=None):
    """
    :param group_id: group id  of the group you are updating
    :param group_data: Dictionary of the data you are updating

    Basic Usage::
        >>> from vFense.group._db import delete_group
        >>> group_id = 'd081a343-cc6c-4f08-81d9-62a116fda025'
        >>> delete_group(group_id)
        >>> (2001, 1, None, [])
    """
    data = {}
    try:

        data = (
            r
            .table(GroupsCollection)
            .get(group_id)
            .update(group_data)
            .run(conn)
        )

    except Exception as e:
        logger.exception(e)

    return(data)
