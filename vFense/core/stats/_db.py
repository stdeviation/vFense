import logging

from vFense._constants import VFENSE_LOGGING_CONFIG
from vFense.db.client import db_create_close, r
from vFense.core._db import (
    insert_data_in_table, delete_data_in_table,
    update_data_in_table
)
from vFense.core.stats._db_model import (
    StatsCollections, AgentStatKeys, StatsPerAgentIndexes,
    CpuStatKeys, MemoryStatKeys, FileSystemStatKeys
)
from vFense.core.decorators import return_status_tuple, time_it

logging.config.fileConfig(VFENSE_LOGGING_CONFIG)
logger = logging.getLogger('rvapi')

@time_it
@db_create_close
def fetch_stats_by_agent_id_and_type(agent_id, stat_type, conn=None):
    """Retrieve information of an agent
    Args:
        agent_id (str): 36 character uuid of the agent you are retrieving.
        stat_type (str): cpu, memory, file_system

    Basic Usage:
        >>> from vFense.core.stats._db import fetch_stats_by_agent_id_and_type
        >>> agent_id = '52faa1db-290a-47a7-a4cf-e4ad70e25c38'
        >>> fetch_stats_by_agent_id_and_type(agent_id, 'cpu')

    Return:
        Dictionary of the stat data
        {
            u'agent_id': u'52faa1db-290a-47a7-a4cf-e4ad70e25c38',
            u'environment': u'Development'
        }
    """
    data = []
    try:
        data = list(
            r
            .table(StatsCollections.AgentStats)
            .get_all(
                [agent_id, stat_type],
                index=StatsPerAgentIndexes.AgentIdAndStatType
            )
            .run(conn)
        )

    except Exception as e:
        logger.exception(e)

    return data

@time_it
@db_create_close
def fetch_stats_by_agent_id_and_device_path(agent_id, device_path, conn=None):
    """Retrieve stats by the device path and agent_id.
    Args:
        agent_id (str): 36 character uuid of the agent you are retrieving.
        fs_name (str): The device_path

    Basic Usage:
        >>> from vFense.core.stats._db import fetch_stats_by_agent_id_and_type
        >>> agent_id = '52faa1db-290a-47a7-a4cf-e4ad70e25c38'
        >>> fetch_stats_by_agent_id_and_type(agent_id, 'cpu')

    Return:
        Dictionary of the stat data
        {
            u'agent_id': u'52faa1db-290a-47a7-a4cf-e4ad70e25c38',
            u'environment': u'Development'
        }
    """
    data = []
    try:
        data = list(
            r
            .table(StatsCollections.AgentStats)
            .get_all(agent_id)
            .filter(lambda x: x.contains(FileSystemStatKeys.Name))
            .filter({FileSystemStatKeys.Name: device_path})
            .run(conn)
        )

    except Exception as e:
        logger.exception(e)

    return data


@time_it
def insert_stat(stat):
    """ Insert a new stat for an agent into the database
        This function should not be called directly.
    Args:
        stat (dict): Dictionary of the data you are inserting.

    Basic Usage:
        >>> from vFense.core.stat._db import insert_stat
        >>> stat = {'view_name': 'vFense', 'needs_reboot': 'no'}
        >>> insert_stat(stat)

    Return:
        Tuple (status_code, count, error, generated ids)
        >>> (2001, 1, None, [])
    """
    data = (
        insert_data_in_table(
            stat, StatsCollections.AgentStats
        )
    )

    return data


@time_it
def update_stat(agent_id, stat):
    """ Insert stats for an agent and its properties into the database
        This function should not be called directly.
    Args:
        agent_id (str): The 36 character UUID of the agent.
        stat (list|dict): Dictionary of the data you are inserting.

    Basic Usage:
        >>> from vFense.core.stat._db import update_stat
        >>> agent_id = '38226b0e-a482-4cb8-b135-0a0057b913f2'
        >>> stat = {'view_name': 'vFense', 'needs_reboot': 'no'}
        >>> update_stat(agent_id, stat)

    Return:
        Tuple (status_code, count, error, generated ids)
        >>> (2001, 1, None, [])
    """
    data = (
        update_data_in_table(
            agent_id, stat, StatsCollections.AgentStats
        )
    )

    return data

@time_it
@db_create_close
@return_status_tuple
def delete_stats(agent_id, conn=None):
    """ Delete stats for an agent and its properties from the database
        This function should not be called directly.
    Args:
        agent_id (str): 36 character UUID of an agent.

    Basic Usage:
        >>> from vFense.core.stats._db import delete_stats
        >>> agent_id = ''
        >>> delete_stats(agent_id)

    Return:
        Tuple (status_code, count, error, generated ids)
        >>> (2001, 1, None, [])
    """
    try:
        data = (
            r
            .table(StatsCollections.AgentStats)
            .get_all(agent_id, index=StatsPerAgentIndexes.AgentId)
            .delete()
            .run(conn)
        )

    except Exception as e:
        logger.exception(e)


    return data

@time_it
@db_create_close
@return_status_tuple
def delete_stats_for_agents(agent_ids, conn=None):
    """ Delete stats for a list of agents and its properties from the database
        This function should not be called directly.
    Args:
        agent_ids (list): List of agent ids.

    Basic Usage:
        >>> from vFense.core.stats._db import delete_stats_for_agents
        >>> agent_ids = ['']
        >>> delete_stats_for_agents(agent_ids)

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
                .table(StatsCollections.AgentStat)
                .get_all(agent_id, index=StatsPerAgentIndexes.AgentId)
                .delete()
            )
            .run(conn, no_reply=True)
        )

    except Exception as e:
        logger.exception(e)

    return data
