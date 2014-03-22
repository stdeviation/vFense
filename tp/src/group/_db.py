import logging
from datetime import datetime
from time import mktime
from vFense.group import *
from vFense.db.client import db_create_close, r, db_connect, return_status_tuple
from vFense.errorz.error_messages import AgentResults, GenericResults
from vFense.errorz.status_codes import DbCodes

logging.config.fileConfig('/opt/TopPatch/conf/logging.config')
logger = logging.getLogger('rvapi')

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

@db_create_close
def fetch_groups(customer_name=None, groupname=None, conn=None):
    """
    Retrieve all groups that is in the database by customer_name or
        all of the groups or by regex.

    :param customer_name: (Optional) Name of the customer,
        in which the group belongs too.
    :param groupname: (Optional) Name of the group you are searching for.
        This is a regular expression match.

    Basic Usage::
        >>> from vFense.group._db import fetch_groups
        >>> customer_name = 'default'
        >>> groupname = 'Ad'
        >>> fetch_groups(customer_name, groupname)
        [
            {
                u'customer_name': u'default',
                u'user_name': u'agent',
                u'id': u'ccac5136-3077-4d2c-a391-9bb15acd79fe'
            }
        ]
    """
    data = []
    try:
        if not customer_name and not groupname:
            data = list(
                r
                .table(GroupsCollection)
                .run(conn)
            )

        elif not customer_name and groupname:
            data = list(
                r
                .table(GroupsCollection)
                .filter(
                    lambda x:
                    x[GroupKeys.GroupName].match("(?i)" + groupname)
                )
                .run(conn)
            )

        elif customer_name and not groupname:
            data = list(
                r
                .table(GroupsCollection)
                .get_all(
                    customer_name, index=GroupsIndexes.CustomerName
                )
                .run(conn)
            )

        elif customer_name and username:
            data = list(
                r
                .table(GroupsCollection)
                .get_all(
                    customer_name, index=GroupsIndexes.CustomerName
                )
                .filter(
                    lambda x:
                    x[GroupKeys.GroupName].match("(?i)" + groupname)
                )
                .run(conn)
            )

    except Exception as e:
        logger.exception(e)

    return(data)


@db_create_close
@return_status_tuple
def insert_group_data(group_data, conn=None):
    """
    This function should not be called directly.
    :param group_data: Can either be a list of dictionaries or a dictionary
        of the data you are inserting.

    Basic Usage::
        >>> from vFense.group._db import insert_group_data
        >>> group_data = {'customer_name': 'vFense', 'needs_reboot': 'no'}
        >>> insert_group_data(group_data)
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
        logger.exception(status)

    return(data)

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
        logger.exception(data)

    return(data)


@db_create_close
@return_status_tuple
def update_group_data(group_id, group_data, conn=None):
    """
    :param group_id: group id  of the group you are updating
    :param group_data: Dictionary of the data you are updating

    Basic Usage::
        >>> from vFense.group._db import update_group_data
        >>> group_id = 'd081a343-cc6c-4f08-81d9-62a116fda025'
        >>> data = {'production_level': 'Development', 'needs_reboot': 'no'}
        >>> update_group_data(group_id, data)
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
        logger.exception(status)

    return(data)

