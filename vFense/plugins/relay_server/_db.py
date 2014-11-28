from vFense.db.client import db_create_close, r
from vFense.core.decorators import time_it, catch_it
from vFense.core._db import (
    insert_data_in_table, delete_data_in_table,
    update_data_in_table
)
from vFense.plugins.relay_server._db_model import (
    RelayServerCollections, RelayServerKeys, RelayServerIndexes
)

@catch_it(False)
@time_it
@db_create_close
def relay_exists(mouse_name, conn=None):
    is_empty = (
        r
        .table(RelayServerCollections.RelayServers)
        .get_all(mouse_name)
        .is_empty()
        .run(conn)
    )
    if not is_empty:
        exist = True
    else:
        exist = False

    return exist

@catch_it({})
@time_it
@db_create_close
def fetch_relay(mouse_name, conn=None):
    data = (
        r
        .table(RelayServerCollections.RelayServers)
        .get(mouse_name)
        .run(conn)
    )

    return data

@catch_it([])
@time_it
@db_create_close
def fetch_relay_addresses(view_name=None, conn=None):
    if view_name:
        data = list(
            r
            .table(RelayServerCollections.RelayServers)
            .get_all(RelayServerKeys.Views, index=RelayServerIndexes.Views)
            .map(lambda x: x[RelayServerKeys.Address])
            .run(conn)
        )
    else:
        data = list(
            r
            .table(RelayServerCollections.RelayServers)
            .pluck(RelayServerKeys.Address)
            .run(conn)
        )

    return data

def add_relay(relay_data, conn=None):
    """ Add a relay server into the database
        This function should not be called directly.
    Args:
        relay_data (list|dict): List or a dictionary of the data
            you are inserting.

    Basic Usage:
        >>> from vFense.plugins.relay_server._db import add_relay
        >>> relay_data = {'views': ['global'], 'address': '10.0.0.11',
                          'relay_name': 'remote_relay.local'}
        >>> add_relay(relay_data)

    Returns:
        Tuple (status_code, count, error, generated ids)
        >>> (2001, 1, None, [])
    """
    data = (
        insert_data_in_table(
            relay_data, RelayServerCollections.RelayServers
        )
    )
    return data

def update_relay(relay_name, relay_data, conn=None):
    """ Update a relay server
        This function should not be called directly.
    Args:
        relay_name (str): List or a dictionary of the data
            you are inserting.
        relay_data (dict): Dictionary of the data you are updating.

    Basic Usage:
        >>> from vFense.plugins.relay_server._db import update_relay
        >>> relay_data = {'views': ['global'], 'address': '10.0.0.11'}
        >>> update_relay(relay_data)

    Returns:
        Tuple (status_code, count, error, generated ids)
        >>> (2001, 1, None, [])
    """
    data = (
        update_data_in_table(
            relay_name, relay_data, RelayServerCollections.RelayServers
        )
    )
    return data

def delete_relay(relay_name, conn=None):
    """ Delete a relay server
        This function should not be called directly.
    Args:
        relay_name (str): The name of the relay server you are deleteing.

    Basic Usage:
        >>> from vFense.plugins.relay_server._db import delete_relay
        >>> delete_relay('relay_server.local')

    Returns:
        Tuple (status_code, count, error, generated ids)
        >>> (2001, 1, None, [])
    """
    data = (
        delete_data_in_table(
            relay_name, RelayServerCollections.RelayServers
        )
    )
    return data

@time_it
@catch_it([])
@db_create_close
def fetch_all_relays(view_name=None, conn=None):
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
