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
#from vFense.core.tag._db_model import *
#from vFense.plugins.patching._db_model import *
from vFense.core.decorators import return_status_tuple, time_it

logging.config.fileConfig(VFENSE_LOGGING_CONFIG)
logger = logging.getLogger('rvapi')


@time_it
@db_create_close
def fetch_production_levels_from_agent(view_name, conn=None):
    """Retrieve all the production levels that is in the database
    Args:
        view_name (str): Name of the view, where the agent is located

    Basic Usage:
        >>> from vFense.core.agent._db import fetch_production_levels_from_agent
        >>> view_name = 'default'
        >>> fetch_production_levels_from_agent(view_name)

    Returns:
        List of Production levels in the system
        [
            u'Development',
            u'Production'
        ]
    """
    data = []
    try:
        data = (
            r
            .table(AgentCollections.Agents)
            .get_all(view_name, index=AgentIndexes.ViewName)
            .pluck(AgentKeys.ProductionLevel)
            .distinct()
            .map(lambda x: x[AgentKeys.ProductionLevel])
            .run(conn)
        )

    except Exception as e:
        logger.exception(e)

    return data

@time_it
@db_create_close
def total_agents_in_view(view_name, conn=None):
    """Retrieve the total number of agents in view.
    Args:
        view_name (str): Name of the view, where the agent is located

    Basic Usage:
        >>> from vFense.core.agent._db import total_agents_in_view
        >>> view_name = 'default'
        >>> total_agents_in_view(view_name)

    Returns:
        Integer
    """
    count = 0
    try:
        count = (
            r
            .table(AgentCollections.Agents)
            .get_all(view_name, index=AgentIndexes.ViewName)
            .count()
            .run(conn)
        )

    except Exception as e:
        logger.exception(e)

    return count

@time_it
@db_create_close
def fetch_supported_os_strings(view_name, conn=None):
    """Retrieve all the operating systems that is in the database
    Args:
        view_name (str): Name of the view, where the agent is located

    Basic Usage:
        >>> from vFense.core.agent._db import fetch_supported_os_strings
        >>> view_name = 'default'
        >>> fetch_supported_os_strings(view_name)

    Returns:
        List of available operating system strings in the database
        [
            u'CentOS 6.5',
            u'Ubuntu 12.04',
            u'Windows 7 Professional Service Pack 1',
            u'Windows 8.1 '
        ]
    """
    data = []
    try:
        data = (
            r
            .table(AgentCollections.Agents)
            .get_all(view_name, index=AgentIndexes.ViewName)
            .pluck(AgentKeys.OsString)
            .distinct()
            .map(lambda x: x[AgentKeys.OsString])
            .run(conn)
        )

    except Exception as e:
        logger.exception(e)

    return data

@time_it
@db_create_close
def fetch_agent_ids_in_views(views=None, os_string=None, conn=None):
    """Retrieve a list of agent ids
    Kwargs:
        view_name (str): Name of the view, where the agent is located

    Basic Usage:
        >>> from vFense.core.agent._db import fetch_agent_ids_in_views
        >>> views = ['global']
        >>> fetch_agent_ids_in_views(views)

    Returns:
        List of agent ids
        [
            u'52faa1db-290a-47a7-a4cf-e4ad70e25c38',
            u'3ea8fd7a-8aad-40da-aff0-8da6fa5f8766'
        ]
    """
    data = []
    try:
        if views and not os_string:
            data = list(
                r.expr(views)
                .map(
                    lambda view:
                    r
                    .table(AgentCollections.Agents)
                    .get_all(view, index=AgentIndexes.Views)
                    .map(lambda x: x[AgentKeys.AgentId])
                )
                .run(conn)
            )

        elif views and os_string:
            data = list(
                r.expr(views)
                .map(
                    lambda view:
                    r
                    .table(AgentCollections.Agents)
                    .get_all(view, index=AgentIndexes.Views)
                    .filter({AgentKeys.OsString: os_string})
                    .map(lambda x: x[AgentKeys.AgentId])
                )
                .run(conn)
            )

        elif not views and os_string:
            data = list(
                r.expr(views)
                .map(
                    lambda view:
                    r
                    .table(AgentCollections.Agents)
                    .filter({AgentKeys.OsString: os_string})
                    .map(lambda x: x[AgentKeys.AgentId])
                )
                .run(conn)
            )
        else:
            data = list(
                r
                .table(AgentCollections.Agents)
                .map(lambda x: x[AgentKeys.AgentId])
                .run(conn)
            )

    except Exception as e:
        logger.exception(e)

    return data


@time_it
@db_create_close
def fetch_agent_ids(view_name=None, agent_os=None, conn=None):
    """Retrieve a list of agent ids
    Kwargs:
        view_name (str): Name of the view, where the agent is located
        agent_os (str):  The os code you are filtering on.
            (linux or windows or darwin)

    Basic Usage:
        >>> from vFense.core.agent._db import fetch_agent_ids
        >>> view_name = 'default'
        >>> os_code = 'os_code'
        >>> fetch_agent_ids(view_name, os_code)

    Returns:
        List of agent ids
        [
            u'52faa1db-290a-47a7-a4cf-e4ad70e25c38',
            u'3ea8fd7a-8aad-40da-aff0-8da6fa5f8766'
        ]
    """
    data = []
    try:
        if view_name and agent_os:
            data = list(
                r
                .table(AgentCollections.Agents)
                .get_all(view_name, index=AgentIndexes.Views)
                .filter({AgentKeys.OsCode: agent_os})
                .map(lambda x: x[AgentKeys.AgentId])
                .run(conn)
            )

        elif view_name and not agent_os:
            data = list(
                r
                .table(AgentCollections.Agents)
                .get_all(view_name, index=AgentIndexes.Views)
                .map(lambda x: x[AgentKeys.AgentId])
                .run(conn)
            )

        elif agent_os and not view_name:
            data = list(
                r
                .table(AgentCollections.Agents)
                .filter({AgentKeys.OsCode: agent_os})
                .map(lambda x: x[AgentKeys.AgentId])
                .run(conn)
            )

        elif not agent_os and not view_name:
            data = list(
                r
                .table(AgentCollections.Agents)
                .map(lambda x: x[AgentKeys.AgentId])
                .run(conn)
            )

    except Exception as e:
        logger.exception(e)

    return data

@time_it
@db_create_close
def fetch_agents(
        view_name=None, filter_key=None,
        filter_val=None, keys_to_pluck=None,
        conn=None
    ):
    """Retrieve all agents by any key in the agent collection
    Kwargs:
        view_name (str): Name of the view, where the agent is located
        filter_key (str): The name of the key that you are filtering on.
        filter_val (str):  The value that you are searching for.
        keys_to_pluck (list): Specific keys that you are retrieving from the database

    Basic Usage:
        >>> from vFense.core.agent._db import fetch_agents
        >>> key = 'os_code'
        >>> val = 'linux'
        >>> pluck = ['computer_name', 'agent_id']
        >>> fetch_agents(view_name, key, val, pluck)

    Return:
        List of agents
        [
            {
                u'agent_id': u'52faa1db-290a-47a7-a4cf-e4ad70e25c38',
                u'computer_name': u'ubuntu'
            },
            {
                u'agent_id': u'3ea8fd7a-8aad-40da-aff0-8da6fa5f8766',
                u'computer_name': u'localhost.localdomain'
            }
        ]
    """
    data = []
    try:
        if (
                filter_key and filter_val and not view_name
                and not keys_to_pluck
            ):

            data = list(
                r
                .table(AgentCollections.Agents)
                .filter({filter_key: filter_val})
                .merge(Merge.TAGS)
                .run(conn)
            )

        elif filter_key and filter_val and view_name and not keys_to_pluck:

            data = list(
                r
                .table(AgentCollections.Agents)
                .get_all(view_name, index=AgentIndexes.ViewName)
                .filter({filter_key: filter_val})
                .merge(Merge.TAGS)
                .run(conn)
            )

        elif filter_key and filter_val and keys_to_pluck and not view_name:

            data = list(
                r
                .table(AgentCollections.Agents)
                .filter({filter_key: filter_val})
                .merge(Merge.TAGS)
                .pluck(keys_to_pluck)
                .run(conn)
            )

        elif filter_key and filter_val and keys_to_pluck and view_name:

            data = list(
                r
                .table(AgentCollections.Agents)
                .get_all(view_name, index=AgentIndexes.ViewName)
                .filter({filter_key: filter_val})
                .merge(Merge.TAGS)
                .pluck(keys_to_pluck)
                .run(conn)
            )

        elif (
                not filter_key and not filter_val
                and not view_name and keys_to_pluck
            ):

            data = list(
                r
                .table(AgentCollections.Agents)
                .merge(Merge.TAGS)
                .pluck(keys_to_pluck)
                .run(conn)
            )

        elif (
                not filter_key and not filter_val
                and view_name and keys_to_pluck
            ):

            data = list(
                r
                .table(AgentCollections.Agents)
                .get_all(view_name, index=AgentIndexes.ViewName)
                .merge(Merge.TAGS)
                .pluck(keys_to_pluck)
                .run(conn)
            )

        elif (
                not filter_key and not filter_val
                and not view_name and not keys_to_pluck
            ):

            data = list(
                r
                .table(AgentCollections.Agents)
                .merge(Merge.TAGS)
                .run(conn)
            )

        elif (
                not filter_key and not filter_val
                and view_name and not keys_to_pluck
            ):

            data = list(
                r
                .table(AgentCollections.Agents)
                .get_all(view_name, index=AgentIndexes.ViewName)
                .merge(Merge.TAGS)
                .run(conn)
            )

    except Exception as e:
        logger.exception(e)

    return data

@time_it
@db_create_close
def fetch_agent(agent_id, keys_to_pluck=None, conn=None):
    """Retrieve information of an agent
    Args:
        agent_id (str): 36 character uuid of the agent you are retrieving.

    Kwargs:
        keys_to_pluck (list): (Optional) Specific keys that you are retrieving
            from the database.

    Basic Usage:
        >>> from vFense.core.agent._db import fetch_agent
        >>> agent_id = '52faa1db-290a-47a7-a4cf-e4ad70e25c38'
        >>> keys_to_pluck = ['production_level', 'needs_reboot']
        >>> fetch_agent(agent_id, keys_to_pluck)

    Return:
        Dictionary of the agent data
        {
            u'agent_id': u'52faa1db-290a-47a7-a4cf-e4ad70e25c38',
            u'production_level': u'Development'
        }
    """
    data = {}
    try:
        if agent_id and keys_to_pluck:
            data = (
                r
                .table(AgentCollections.Agents)
                .get(agent_id)
                .merge(Merge.AGENTS)
                .merge(Merge.TAGS)
                .pluck(keys_to_pluck)
                .run(conn)
            )

        elif agent_id and not keys_to_pluck:
            data = (
                r
                .table(AgentCollections.Agents)
                .get(agent_id)
                .merge(Merge.AGENTS)
                .merge(Merge.TAGS)
                .run(conn)
            )

    except Exception as e:
        logger.exception(e)

    return data

@time_it
@db_create_close
@return_status_tuple
def fetch_all_agents_for_view(view_name, conn=None):
    """Retrieve all agents for a view.
    Args:
        view_name (str): Name of the view.

    Basic Usage:
        >>> from vFense.agent._db import fetch_all_agents_for_view
        >>> view_name = 'test'
        >>> fetch_all_agents_for_view(view_nam)

    Return:
        List of dictionaries.
    """
    data = []
    try:
        data = list(
            r
            .table(AgentCollections.Agents)
            .get_all(view_name, index=AgentIndexes.ViewName)
            .run(conn)
        )

    except Exception as e:
        logger.exception(e)

    return data

@time_it
def update_agent(agent_id, agent_data):
    """Update Agent data
    Args:
        agent_id (str): 36 character uuid of the agent you are updating
        agent_data(list|dict): Dictionary of the data you are updating

    Basic Usage::
        >>> from vFense.core.agent._db import update_agent
        >>> agent_id = '0a1f9a3c-9200-42ef-ba63-f4fd17f0644c'
        >>> data = {'production_level': 'Development', 'needs_reboot': 'no'}
        >>> update_agent(agent_id, data)

    Return:
        Tuple (status_code, count, error, generated ids)
        >>> (2001, 1, None, [])
    """
    data = (
        update_data_in_table(
            agent_id, agent_data, AgentCollections.Agents
        )
    )

    return data

@time_it
def insert_agent(agent_data):
    """ Insert a new agent and its properties into the database
        This function should not be called directly.
    Args:
        agent_data (dict): Dictionary of the data you are inserting.

    Basic Usage:
        >>> from vFense.core.agent._db import insert_agent
        >>> agent_data = {'view_name': 'vFense', 'needs_reboot': 'no'}
        >>> insert_agent(agent_data)

    Return:
        Tuple (status_code, count, error, generated ids)
        >>> (2001, 1, None, [])
    """
    data = (
        insert_data_in_table(
            agent_data, AgentCollections.Agents
        )
    )

    return data


@time_it
def delete_agent(agent_id):
    """ Delete an agent and its properties from the database
        This function should not be called directly.
    Args:
        agent_id (str): 36 character UUID of the agent.

    Basic Usage:
        >>> from vFense.agent._db import delete_agent
        >>> agent_id = ""
        >>> delete_agent(agent_id)

    Returns:
        Tuple (status_code, count, error, generated ids)
        >>> (2001, 1, None, [])
    """
    data = (
        delete_data_in_table(
            agent_id, AgentCollections.Agents
        )
    )
    return data


@time_it
@db_create_close
@return_status_tuple
def delete_all_agents_from_view(view_name, agent_ids=None, conn=None):
    """Delete all agents in a view from vFense or just a list of agents.
    Args:
        view_name (str): Name of the view.

    Basic Usage:
        >>> from vFense.agent._db import delete_all_agents_for_view
        >>> view_name = 'test'
        >>> delete_all_agents_for_view(view_nam)

    Return:
        Tuple (status_code, count, error, generated ids)
        >>> (2001, 1, None, [])
    """
    data = {}
    try:
        if agent_ids:
            data = (
                r
                .expr(agent_ids)
                .for_each(
                    lambda agent_id:
                    r
                    .table(AgentCollections.Agents)
                    .get(agent_id)
                    .delete()
                )
                .run(conn, no_reply=True)
            )

        else:
            data = (
                r
                .table(AgentCollections.Agents)
                .get_all(view_name, index=AgentIndexes.Views)
                .delete()
                .run(conn, no_reply=True)
            )

    except Exception as e:
        logger.exception(e)

    return data


@time_it
@db_create_close
@return_status_tuple
def remove_all_agents_from_view(view_name, agent_ids=None, conn=None):
    """Remove all agents from a view or just a list of agents.
    Args:
        view_name (str): Name of the view.

    Basic Usage:
        >>> from vFense.agent._db import remove_all_agents_from_view
        >>> view_name = 'test'
        >>> remove_all_agents_from_view(view_nam)

    Return:
        Tuple (status_code, count, error, generated ids)
        >>> (2001, 1, None, [])
    """
    data = {}
    try:
        if agent_ids:
            data = (
                r
                .expr(agent_ids)
                .for_each(
                    lambda agent_id:
                    r
                    .table(AgentCollections.Agents)
                    .get_all(agent_id)
                    .update(
                        lambda x:
                        {
                            AgentKeys.Views: (
                                x[AgentKeys.Views].set_difference([view_name])
                            )
                        }
                    )
                )
                .run(conn, no_reply=True)
            )

        else:
            data = (
                r
                .table(AgentCollections.Agents)
                .get_all(view_name, index=AgentIndexes.Views)
                .update(
                    lambda x:
                    {
                        AgentKeys.Views: (
                            x[AgentKeys.Views].set_difference([view_name])
                        )
                    }
                )
                .delete()
                .run(conn, no_reply=True)
            )

    except Exception as e:
        logger.exception(e)

    return data


@time_it
@db_create_close
@return_status_tuple
def add_agents_to_views(agent_ids, views, conn=None):
    """Add a list of agents into a list of views
    Args:
        agent_ids (list): List of agent ids
        views (str): List of views.

    Basic Usage:
        >>> from vFense.agent._db import add_agents_to_views
        >>> views = ['test']
        >>> agent_ids = ['7f242ab8-a9d7-418f-9ce2-7bcba6c2d9dc']
        >>> add_agents_to_views(agent_ids, views)

    Returns:
        Tuple (status_code, count, error, generated ids)
        >>> (2001, 1, None, [])
    """
    data = {}
    try:
        data = (
            r
            .expr(agent_ids)
            .for_each(
                lambda agent_id:
                r
                .table(AgentCollections.Agents)
                .get_all(agent_id)
                .update(
                    lambda x:
                    {
                        AgentKeys.Views: (
                            x[AgentKeys.Views].set_union(views)
                        )
                    }
                )
            )
            .run(conn)
        )

    except Exception as e:
        logger.exception(e)

    return data

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


@time_it
@db_create_close
@return_status_tuple
def update_views_for_agent(views, agent_id, conn=None):
    """Update the views for an agent,
    Args:
        views (list): List of views you are adding to this agent.
        agent_id (str): The 36 character UUID of this agent.

    Basic Usage:
        >>> from vFense.agent._db import update_views_for_agent
        >>> views = ['NYC', 'MIAMI']
        >>> agent_id = 'cac3f82c-d320-4e6f-9ee7-e28b1f527d76'
        >>> update_views_for_agent(views, agent_id)

    Returns:
        Tuple (status_code, count, error, generated ids)
        >>> (2001, 1, None, [])
    """
    data = {}
    try:
        data = (
            r
            .table(AgentCollections.Agents)
            .get(agent_id)
            .update(
                lambda y:
                {
                    AgentKeys.Views: (
                        y[AgentKeys.Views].set_union(views)
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
def delete_views_from_agent(views, agent_id, conn=None):
    """Delete views from this agent,
    Args:
        views (list): List of views you are removing from this agent.
        agent_id (str): The 36 character UUID of this agent.

    Basic Usage:
        >>> from vFense.agent._db import delete_views_from_agent
        >>> views = ['NYC', 'MIAMI']
        >>> agent_id = 'cac3f82c-d320-4e6f-9ee7-e28b1f527d76'
        >>> delete_views_from_agent(views, agent_id)

    Returns:
        Tuple (status_code, count, error, generated ids)
        >>> (2001, 1, None, [])
    """
    data = {}
    try:
        data = (
            r
            .table(AgentCollections.Agents)
            .get(agent_id)
            .update(
                lambda y:
                {
                    AgentKeys.Views: (
                        y[AgentKeys.Views].set_difference(views)
                    )
                }
            )
            .run(conn)
        )

    except Exception as e:
        logger.exception(e)

    return(data)

