import logging
import logging.config
from vFense._constants import VFENSE_LOGGING_CONFIG
from vFense.db.client import db_create_close, r
from vFense.core.decorators import return_status_tuple, time_it, catch_it
from vFense.plugins.mightymouse import (
    RelayServerCollections, RelayServerKeys
)

logging.config.fileConfig(VFENSE_LOGGING_CONFIG)
logger = logging.getLogger('rvapi')

def mouse_exists(mouse_name):

    conn = db_connect()
    try:
        exist = (
            r
            .table(RelayServersCollection)
            .get(mouse_name)
            .run(conn)
        )

    except Exception as e:
        logger.exception(e)
        exist = False

    conn.close()

    return(exist)

def get_mouse_addresses(view_name):

    conn = db_connect()
    try:
        exist = list(
            r
            .table(RelayServersCollection)
            .pluck(RelayServers.Address)
            .run(conn)
        )

    except Exception as e:
        logger.exception(e)
        exist = False

    conn.close()

    return(exist)


def add_mouse(view_names, mouse_name, address,
              username, uri, method):
    conn = db_connect()
    data = {
        RelayServers.RelayName: mouse_name,
        RelayServers.Views: view_names,
        RelayServers.Address: address,
    }
    try:
        (
            r
            .table(RelayServersCollection)
            .insert(data)
            .run(conn)
        )
        status = (
            MightyMouseResults(
                username, uri, method
            ).created(mouse_name, data)
        )

    except Exception as e:
        status = (
            MightyMouseResults(
                username, uri, method
            ).failed_to_create(mouse_name, e)
        )

        logger.exception(status)

    conn.close()

    return(status)

@time_it
@catch_it({})
@db_create_close
@return_status_tuple
def update_mouse(exist, mouse_name, view_names, address, conn=None):
    if not address:
        address = exist[RelayServerKeys.Address]

    data = {
        RelayServers.Views: view_names,
        RelayServers.Address: address,
    }
    data = (
        r
        .table(RelayServerCollections.RelayServers)
        .get(mouse_name)
        .update(data)
        .run(conn)
    )

    return data

@time_it
@catch_it({})
@db_create_close
@return_status_tuple
def delete_mouse(mouse_name, conn=None):
    data = (
       r
        .table(RelayServerCollections.RelayServers)
        .get(mouse_name)
        .delete()
        .run(conn)
    )

    return data

@time_it
@catch_it([])
@db_create_close
def get_all_mouseys(view_name=None, conn=None):
    if not view_name:
        data = list(
            r
            .table(RelayServerCollections.RelayServers)
            .run(conn)
        )
    else:
        data = list(
            r
            .table(RelayServerCollections.RelayServers)
            .filter(lambda x: x[RelayServerKeys.Views].contains(view_name))
            .run(conn)
        )

    return data
