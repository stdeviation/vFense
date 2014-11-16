#!/usr/bin/env python
import logging

from vFense._constants import VFENSE_LOGGING_CONFIG
from vFense.db.client import db_create_close, r
from vFense.plugins.notifications.mailer._db_model import (
    NotificationPluginKeys, NotificationPluginIndexes
)
from vFense.plugins.notifications._db_model import NotificationCollections
from vFense.core.decorators import return_status_tuple, time_it

from vFense.core._db import (
    insert_data_in_table, delete_data_in_table,
    update_data_in_table
)

from vFense.plugins.notifications._constants import NotifPluginTypes


logging.config.fileConfig(VFENSE_LOGGING_CONFIG)
logger = logging.getLogger('vfense_api')


@db_create_close
def fetch_email_config(view_name=None, conn=None):
    data = {}
    try:
        mail_config = list(
            r
            .table(NotificationCollections.NotificationPlugins)
            .get_all(view_name, index=NotificationPluginIndexes.ViewName)
            .filter(
                {
                    NotificationPluginKeys.PluginName: NotifPluginTypes.EMAIL
                }
            )
            .run(conn)
        )
        if mail_config:
            data = mail_config[0]

    except Exception as e:
        logger.exception(e)

    return data


@time_it
def insert_email(email_data):
    """ Insert an email config and its properties into the database
        This function should not be called directly.
    Args:
        email_data (list|dict): Dictionary of the data you are inserting.

    Basic Usage:
        >>> from vFense.plugins.notifications._db import insert_email
        >>> email_data = {'server': 'mail.google.com', 'port': 445}
        >>> insert_email(email_data)

    Return:
        Tuple (status_code, count, error, generated ids)
        >>> (2001, 1, None, [])
    """
    data = (
        insert_data_in_table(
            email_data, NotificationCollections.NotificationPlugins
        )
    )

    return data

@time_it
def update_email(email_id, email_data):
    """ Update an email config and its properties into the database
        This function should not be called directly.
    Args:
        email_id (str): the email config UUID
        email_data (list|dict): Dictionary of the data you are updating.

    Basic Usage:
        >>> from vFense.plugins.notifications._db import update_email
        >>> email_id = '38226b0e-a482-4cb8-b135-0a0057b913f2'
        >>> email_data = {'port': 25, 'server': 'mail.yahoo.com'}
        >>> update_email(email_id, email_data)

    Return:
        Tuple (status_code, count, error, generated ids)
        >>> (2001, 1, None, [])
    """
    data = (
        update_data_in_table(
            email_id, email_data, NotificationCollections.NotificationPlugins
        )
    )

    return data

@time_it
def delete_email(email_id):
    """ Delete the email settings and its properties in the database
        This function should not be called directly.
    Args:
        email_id (str): the email config UUID

    Basic Usage:
        >>> from vFense.plugins.notifications._db import delete_email
        >>> email_id = '38226b0e-a482-4cb8-b135-0a0057b913f2'
        >>> delete_email(email_id)

    Return:
        Tuple (status_code, count, error, generated ids)
        >>> (2001, 1, None, [])
    """
    data = (
        delete_data_in_table(
            email_id, NotificationCollections.NotificationPlugins
        )
    )

    return data
