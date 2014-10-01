import logging

from vFense import VFENSE_LOGGING_CONFIG
from vFense.db.client import db_create_close, r
from vFense.core._db import (
    insert_data_in_table, delete_data_in_table,
    update_data_in_table
)
from vFense.core.agent._db_model import (
    AgentCollections, AgentIndexes, AgentKeys,
    HardwarePerAgentIndexes
)
from vFense.core.agent._db_sub_queries import Merge
from vFense.core.decorators import return_status_tuple, time_it

logging.config.fileConfig(VFENSE_LOGGING_CONFIG)
logger = logging.getLogger('rvapi')


@time_it
def insert_hardware(hw_data):
    """ Insert hardware for an agent and its properties into the database
        This function should not be called directly.
    Args:
        hw_data (list|dict): Dictionary of the data you are inserting.

    Basic Usage:
        >>> from vFense.core.agent._db import insert_hardware
        >>> hw_data = {'view_name': 'vFense', 'needs_reboot': 'no'}
        >>> insert_hardware(hw_data)

    Return:
        Tuple (status_code, count, error, generated ids)
        >>> (2001, 1, None, [])
    """
    data = (
        insert_data_in_table(
            hw_data, AgentCollections.Hardware
        )
    )

    return data

@time_it
@db_create_close
@return_status_tuple
def delete_hardware_for_agent(agent_id, conn=None):
    """ Delete hardware for an agent and its properties from the database
        This function should not be called directly.
    Args:
        agent_id (str): 36 character UUID of an agent.

    Basic Usage:
        >>> from vFense.core.agent._db import delete_hardware_for_agent
        >>> agent_id = ''
        >>> delete_hardware_for_agent(agent_id)

    Return:
        Tuple (status_code, count, error, generated ids)
        >>> (2001, 1, None, [])
    """
    try:
        data = (
            r
            .table(AgentCollections.Hardware)
            .get_all(agent_id, index=HardwarePerAgentIndexes.AgentId)
            .delete()
            .run(conn)
        )

    except Exception as e:
        logger.exception(e)


    return data

@time_it
@db_create_close
@return_status_tuple
def delete_hardware_for_agents(agent_ids, conn=None):
    """ Delete hardware for a list of agents and its properties from the database
        This function should not be called directly.
    Args:
        agent_ids (list): List of agent ids.

    Basic Usage:
        >>> from vFense.core.agent._db import delete_hardware_for_agents
        >>> agent_ids = ['']
        >>> delete_hardware_for_agents(agent_ids)

    Return:
        Tuple (status_code, count, error, generated ids)
        >>> (2001, 1, None, [])
    """
    try:
        data = (
            r
            .expr(agent_ids)
            .for_each(
                lambda agent_id:
                r
                .table(AgentCollections.Hardware)
                .get_all(agent_id, index=HardwarePerAgentIndexes.AgentId)
                .delete()
            )
            .run(conn, no_reply=True)
        )

    except Exception as e:
        logger.exception(e)


    return data
