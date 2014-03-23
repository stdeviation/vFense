import logging                                                                                                     

from vFense.core.group import *
from vFense.core.user import *
from vFense.core.customer import *
from vFense.core.permissions import *
from vFense.core._db import retrieve_object
from vFense.core.group._db import insert_group, fetch_group, fetch_groups, \
    insert_group_per_user, fetch_group_by_name, delete_user_in_groups, \
    fetch_users_in_group

from vFense.core.decorators import results_message, time_it
from vFense.errorz.status_codes import DbCodes

logging.config.fileConfig('/opt/TopPatch/conf/logging.config')
logger = logging.getLogger('rvapi')


@time_it
def get_group(group_id):
    """
    Retrieve a group from the database.
    :param group_id: 36 Character UUID.
    Basic Usage::
        >>> from vFense.group.groups import get_group
        >>> group_id = '8757b79c-7321-4446-8882-65457f28c78b'
        >>> get_group(group_id)
        {
            u'group_name': u'Administrator',
            u'customer_name': u'default',
            u'id': u'8757b79c-7321-4446-8882-65457f28c78b',
            u'Permissions': [
                u'administrator'
            ]
        }
    """
    data = fetch_group(group_id)
    return(data)


@time_it
def get_group_by_name(group_name, customer_name):
    """
    Retrieve a group from the database
    :param group_name: name of the group.
    :param customer_name: name of the customer that the group belongs to.
    Basic Usage::
        >>> from vFense.group.groups import get_group_by_name
        >>> group_name = 'Administrator'
        >>> customer_name = 'default'
        >>> get_group_by_name(group_name, customer_name)
        {
            u'group_name': u'Administrator',
            u'customer_name': u'default',
            u'id': u'8757b79c-7321-4446-8882-65457f28c78b',
            u'Permissions': [
                u'administrator'
            ]
        }
    """
    data = fetch_group_by_name(group_name, customer_name)
    return(data)


@time_it
def get_users_in_group(
    group_id, fields_to_pluck=None,
    user_name=None, uri=None, method=None
    ):
    """
    Fetch all users for group_id
    :param group_id: 36 Character UUID
    Basic Usage::
        >>> from vFense.core.group.groups get_users_in_group
        >>> group_id = ['17753c6a-2099-4389-b97a-e6e2658b6396']
        >>> get_users_in_group(group_id)
    """
    data = fetch_users_in_group(group_id, fields_to_pluck)
    return(data)


@time_it
def get_groups(
    customer_name=None, groupname=None,
    fields_to_pluck=None
    ):
    """
    Retrieve all the groups that is in the database by customer_name or
        all of the customers or by regex.

    :param customer_name: (Optional) Name of the customer,
        that the group belongs too.
    :param groupname: (Optional) Name of the group you are searching for.
        This is a regular expression match.

    :param fields_to_pluck: (Optional) List of fields you want to pluck
        from the database

    Basic Usage::
        >>> from vFense.group.groups import get_groups
        >>> customer_name = 'default'
        >>> groupname = 'Ad'
        >>> get_groups(customer_name, groupname)
        [
            {
                u'permissions': [
                    u'administrator'
                ],
                u'group_name': u'Administrator',
                u'id': u'3ffc2a67-1203-4cb0-ada2-2ae870072680',
                u'customer_name': u'default'
                                                
            }
        ]
    """
    data = fetch_groups(customer_name, groupname, fields_to_pluck)
    return(data)


@time_it
def validate_group_ids(group_ids):
    """
    Validate a list if group ids,
    Returns a tuple
    example: (True, [valid_group_ids], [invalid_group_ids])
    :param group_ids: List of group ids

    Basic Usage::
        >>> from vFense.group.groups import validate_group_ids
        >>> group_ids = ['4b114647-a6ea-449f-a5a0-d5e1961afb28', '3e27f278-7839-416e-b516-fe4f7cbe98d7']
        >>> validate_group_ids(group_ids)
        (True, ['3ffc2a67-1203-4cb0-ada2-2ae870072680', '0834e656-27a5-4b13-ba56-635797d0d1fc'], [])
    """
    validated = True
    invalid_groups = []
    valid_groups = []
    if isinstance(group_ids, list):
        for group_id in group_ids:
            if get_group(group_id):
                valid_groups.append(group_id)
            else:
                invalid_groups.append(group_id)
                validated = False

    return(validated, valid_groups, invalid_groups)


@time_it
@results_message
def add_user_to_groups(
    username, customer_name, group_ids,
    user_name=None, uri=None, method=None
    ):
    """
    Add a user into a vFense group
    :param username:  Name of the user already in vFense.
    :param customer_name: The customer this user is part of.
    :param group_ids: List of group ids.

    Basic Usage::
        >>> from vFense.group.groups import add_user_to_groups
        >>> username = 'alien'
        >>> customer_name = 'default'
        >>> group_ids = ['0834e656-27a5-4b13-ba56-635797d0d1fc']
        >>> add_user_to_groups(username, customer_name, group_ids)
    {
        'uri': None,
        'rv_status_code': 1010,
        'http_method': None,
        'http_status': 200,
        'message': "None - groups per user [u'ee54820c-cb4e-46a1-9d11-73afe8c4c4e3'] was created",
        'data': {
            'group_name': u'FooLah',
            'user_name': 'alien',
            'group_id': '0834e656-27a5-4b13-ba56-635797d0d1fc',
            'customer_name': 'default'
        }
    }
    """
    groups_are_valid = validate_group_ids(group_ids)
    user_exist = retrieve_object(username, UsersCollection)
    customer_exist = retrieve_object(customer_name, CustomersCollection)
    results = None
    if groups_are_valid[0] and user_exist and customer_exist:
        data_list = []
        for group_id in group_ids:
            group_exist = get_group(group_id)
            data_to_add = (
                {
                    GroupsPerUserKeys.CustomerName: customer_name,
                    GroupsPerUserKeys.UserName: username,
                    GroupsPerUserKeys.GroupName: group_exist[GroupKeys.GroupName],
                    GroupsPerUserKeys.GroupId: group_id
                }
            )
            data_list.append(data_to_add)

        object_status, object_count, error, generated_ids = (
            insert_group_per_user(data_to_add)
        )

        results = (
            object_status, generated_ids, 'groups per user', data_to_add,
            error, user_name, uri, method
        )

    elif not groups_are_valid[0]:
        status_code = DbCodes.Errors
        status_error = 'Group Ids are invalid: %s' % (groups_are_valid[2])
        results = (
            status_code, None, 'groups per user', [],
            status_error, user_name, uri, method
        )

    elif not user_exist:
        status_code = DbCodes.Errors
        status_error = 'User name is invalid: %s' % (username)
        results = (
            status_code, None, 'groups per user', [],
            status_error, user_name, uri, method
        )

    elif not customer_exist:
        status_code = DbCodes.Errors
        status_error = 'Customer name is invalid: %s' % (customer_name)
        results = (
            status_code, None, 'groups per user', [],
            status_error, user_name, uri, method
        )

    return(results)


@time_it
@results_message
def create_group(
        group_name, customer_name, permissions,
        user_name=None, uri=None, method=None
    ):
    """
    Create a group in vFense
    :param group_name: The name of the group.
    :param customer_name: The name of the customer you are adding this group too.
    :param permissions: List of permissions, this group has.

    Basic Usage::
        >>> from vFense.group.groups import create_group
        >>> group_name = 'Linux Admins'
        >>> customer_name = 'default'
        >>> permissions = ['administrator']
        >>> create_group(group_name, customer_name, permissions)
        {
            'uri': None,
            'rv_status_code': 1010,
            'http_method': None,
            'http_status': 200,
            'message': "None - create group [u'8757b79c-7321-4446-8882-65457f28c78b'] was created",
            'data': {
                'Permissions': [
                    'administrator'
                ],
                'group_name': 'Linux Admins',
                'customer_name': 'default'
            }
        }
    """

    try:
        group_exist = get_group_by_name(group_name, customer_name)
        permissions_valid = set(permissions).issubset(set(VALID_PERMISSIONS))
        if not group_exist and permissions_valid:
            group_data = (
                {
                    GroupKeys.CustomerName: customer_name,
                    GroupKeys.GroupName: group_name,
                    GroupKeys.Permissions: permissions,
                }
            )

            status_code, status_count, error, generated_ids = (
                insert_group(group_data)
            )

            results = (
                status_code, generated_ids, 'create group',
                group_data, error, user_name, uri, method
            )

        elif not group_exist and not permissions_valid:
            error = 'invalid permissions %s' % (permissions)
            results = (
                DbCodes.Errors, group_name, 'create group',
                [], error, user_name, uri, method
            )

        elif group_exist:
            error = 'group %s exists' % (group_name)
            results = (
                DbCodes.Errors, group_name, 'create group',
                [], error, user_name, uri, method
            )

    except Exception as e:
        logger.exception(e)
        results = (
            DbCodes.Errors, group_name, 'create group',
            [], e, user_name, uri, method
        )

    return(results)


@time_it
@results_message
def remove_groups_from_user(
    username, group_ids=None,
    user_name=None, uri=None, method=None
    ):
    """
    :param username: username.
    :param group_ids: (Optional) List of group_ids.

    Basic Usage::
        >>> from vFense.core.group.groups remove_groups_from_user
        >>> username = 'agent_api'
        >>> remove_groups_from_user(username)
        >>> (2001, 1, None, [])
    """
    try:
        status_code, count, errors, generated_ids = (
            delete_user_in_groups(username, group_ids)
        )
        status = remove_groups_from_user.func_name + ' - '
        results = (
            status_code, username, status, [], None,
            user_name, uri, method
        )

    except Exception as e:
        logger.exception(e)
        status = remove_groups_from_user.func_name + ' - '
        results = (
            DbCodes.Errors, username, status, [], e,
            user_name, uri, method
        )

    return(results)


@time_it
@results_message
def remove_group(group_id, user_name=None, uri=None, method=None):
    """
    Create a group in vFense
    :param group_id: 36 Character UUID

    Basic Usage::
        >>> from vFense.core.group.groups import delete_group
        >>> group_id = '4b114647-a6ea-449f-a5a0-d5e1961afb28'
        >>> delete_group(group_id)
    """
    status = remove_groups.func_name + ' - '
    try:
        users_exist = get_users_in_group(group_id)
        group_exist = get_group(group_id)
        if not users_exist and group_exist:
            status_code, status_count, error, generated_id = (
                delete_group(group_id)
            )
            status = remove_groups.func_name + ' - '
            results = (
                status_code, group_id, status, [], error,
                user_name, uri, method
            )

        elif users_exist:
            error = (
                'users exist for group %s' % (group_id)
            )

            results = (
                DbCodes.Unchanged, group_id, status + error, [], None,
                user_name, uri, method
            )

        elif not group_exist:
            error = 'group %s does not exist'

            results = (
                DbCodes.Skipped, group_id, status + error, [], None,
                user_name, uri, method
            )

    except Exception as e:
        logger.exception(e)
        error = 'failed to remove group %s' % (group_id)
        results = (
            DbCodes.Errors, group_id, status + error, [], e,
            user_name, uri, method
        )

    return(results)
