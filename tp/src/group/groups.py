import logging                                                                                                     
from datetime import datetime                                                                                      
from time import mktime

from vFense.group import *
from vFense.user import *
from vFense.customer import *
from vFense._db import retrieve_object
from vFense.utils.security import Crypto
from vFense.group._db import insert_group, fetch_group, fetch_group, \
    insert_group_per_user
from vFense.db.client import r, return_status_tuple, results_message
from vFense.errorz.error_messages import GenericResults
from vFense.errorz.status_codes import DbCodes

logging.config.fileConfig('/opt/TopPatch/conf/logging.config')
logger = logging.getLogger('rvapi')

def get_group(group_id):
    """
    Retrieve a group from the database
    :param group_id: 36 Character UUID.
    Basic Usage::
        >>> from vFense.group.groups import get_group
        >>> username = 'admin'
        >>> get_group(group_id)
        {
            u'current_customer': u'default',
            u'enabled': True,
            u'full_name': u'TopPatchAgentCommunicationAccount',
            u'default_customer': u'default',
            u'user_name': u'agent',
            u'email': u'admin@toppatch.com'
        }
    """
    data = fetch_group(group_id)
    return(data)

def get_groups(customer_name=None, groupname=None):
    """
    Retrieve all the groups that is in the database by customer_name or
        all of the customers or by regex.

    :param customer_name: (Optional) Name of the customer,
        that the group belongs too.
    :param groupname: (Optional) Name of the group you are searching for.
        This is a regular expression match.

    Basic Usage::
        >>> from vFense.group.groups import get_groups
        >>> customer_name = 'default'
        >>> groupname = 'Ad'
        >>> get_groups(customer_name, groupname)
        [
            {
                u'customer_name': u'default',
                u'user_name': u'agent',
                u'id': u'ccac5136-3077-4d2c-a391-9bb15acd79fe'
            }
        ]
    """
    data = fetch_groups(customer_name, groupname) 
    return(data)

def validate_group_ids(group_ids):
    """
    Validate a list if group ids
    :param group_ids: List of group ids

    Basic Usage::
        >>> from vFense.group.groups import validate_group_ids
        >>> group_ids = ['4b114647-a6ea-449f-a5a0-d5e1961afb28', '3e27f278-7839-416e-b516-fe4f7cbe98d7']
        >>> validate_group_ids(group_ids)
        [
            {
                u'customer_name': u'default',
                u'user_name': u'agent',
                u'id': u'ccac5136-3077-4d2c-a391-9bb15acd79fe'
            }
        ]
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

@results_message
def create_group(group_name, customer_name, permissions, user_ids):
    """
    Create a group in vFense
    :param group_name: The name of the group.
    :param customer_name: The name of the customer you are adding this group too.
    :param permissions: List of permissions, this group has.
    :param user_ids: List of user ids, that will be added to this group

    Basic Usage::
        >>> from vFense.group.groups import create_group
        >>> group_name = 'Linux Admins'
        >>> customer_name = 'default'
        >>> permissions = ['install', 'uninstall', 'reboot']
        >>> user_ids = ['4b114647-a6ea-449f-a5a0-d5e1961afb28', '3e27f278-7839-416e-b516-fe4f7cbe98d7']
        >>> create_group(group_name, customer_name, permissions, user_ids)
    """
    validated = True
    invalid_groups = []
    valid_groups = []
    if isinstance(group_ids, list):
        for group_id in group_ids:
            if get_group(group_id):
                valid_groups.append(group_id)
                validated = False
            else:
                invalid_groups.append(group_id)

    return(validated, valid_groups, invalid_groups)
