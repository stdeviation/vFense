#!/usr/bin/env python
import logging
import logging.config
from vFense import VFENSE_LOGGING_CONFIG

from vFense.core.decorators import (
    time_it, return_status_tuple
)
from vFense.core.tag._db_model import (
    TagCollections, TagKeys, TagsPerAgentKeys,
    TagsIndexes, TagsPerAgentIndexes
)

from vFense.db.client import db_create_close, r
from vFense.core.tag._db_sub_queries import TagMerge
from vFense.core._db import (
    insert_data_in_table, delete_data_in_table,
    update_data_in_table
)

logging.config.fileConfig(VFENSE_LOGGING_CONFIG)
logger = logging.getLogger('rvapi')

@db_create_close
def fetch_tag(tag_id, keys_to_pluck=None, conn=None):
    """Retrieve information of a tag
    Args:
        tag_id (str): 36 character uuid of the tag you are retrieving.

    Kwargs:
        keys_to_pluck (list): (Optional) Specific keys that you are retrieving
        from the database

    Basic Usage:
        >>> from vFense.core.tag._db import fetch_tag
        >>> tag_id = '52faa1db-290a-47a7-a4cf-e4ad70e25c38'
        >>> keys_to_pluck = ['tag_id', 'tag_name']
        >>> fetch_tag(tag_id, keys_to_pluck)

    Return:
        Dictionary of the agent data
        {
            u'tag_id': u'52faa1db-290a-47a7-a4cf-e4ad70e25c38',
            u'tag_name': u'Development'
        }
    """
    tag_info = {}

    try:
        if keys_to_pluck:
            tag_info = (
                r
                .table(TagCollections.Tags)
                .get(tag_id)
                .merge(TagMerge.AGENTS)
                .pluck(keys_to_pluck)
                .run(conn)
            )
        else:
            tag_info = (
                r
                .table(TagCollections.Tags)
                .merge(TagMerge.AGENTS)
                .get(tag_id)
                .run(conn)
            )

    except Exception as e:
        logger.exception(e)

    return tag_info


@db_create_close
def fetch_tag_ids(view_name=None, conn=None):
    """Retrieve all tag_ids for a view or all.
    Kwargs:
        view_name (str): name of the view, you are retriveing the tag ids for.


    Basic Usage:
        >>> from vFense.core.tag._db import fetch_tag_ids
        >>> view_name = 'Test1'
        >>> fetch_tag_ids(view_name)

    Return:
        List of tag ids
    """
    tag_info = {}

    try:
        if view_name:
            tag_info = (
                r
                .table(TagCollections.Tags)
                .get_all(view_name, index=TagsIndexes.ViewName)
                .map(lambda x: x[TagKeys.TagId])
                .run(conn)
            )
        else:
            tag_info = (
                r
                .table(TagCollections.Tags)
                .map(lambda x: x[TagKeys.TagId])
                .run(conn)
            )

    except Exception as e:
        logger.exception(e)

    return tag_info

@db_create_close
def fetch_agent_ids_in_tag(tag_id, conn=None):
    """Retrieve all agent_ids in a tag.
    Args:
        tag_id (str): 36 character UUID of a tag.

    Basic Usage:
        >>> from vFense.core.tag._db import fetch_agent_ids_in_tag
        >>> tag_id = '52faa1db-290a-47a7-a4cf-e4ad70e25c38'
        >>> fetch_agent_ids_in_tag(tag_id)

    Return:
        List of tag ids
    """
    tag_info = {}

    try:
        tag_info = (
           r
           .table(TagCollections.TagsPerAgent)
           .get_all(tag_id, index=TagsIndexes.TagId)
           .map(lambda x: x[TagsPerAgentKeys.AgentId])
           .run(conn)
        )

    except Exception as e:
        logger.exception(e)

    return tag_info

@time_it
@db_create_close
@return_status_tuple
def delete_agent_ids_from_tag(tag_id, agent_ids=None, conn=None):
    """Delete 1 or multiple agents in a tag.
    Args:
        tag_id (str): 36 character UUID of a tag.

    Kwargs:
        agent_ids (list): List of agent ids to remove from tag.
            default=None (Remove all agents from tag)

    Basic Usage:
        >>> from vFense.core.tag._db import delete_agent_ids_from_tag
        >>> tag_id = '52faa1db-290a-47a7-a4cf-e4ad70e25c38'
        >>> agent_ids = ['agent1', 'agent2']
        >>> delete_agent_ids_from_tag(tag_id, agent_ids)

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
                    .table(TagCollections.TagsPerAgent)
                    .get_all(
                        [agent_id, tag_id],
                        index=TagsPerAgentIndexes.AgentIdAndTagId
                    )
                    .delete()
                )
                .run(conn)
            )

        else:
            data = (
                r
                .table(TagCollections.TagsPerAgent)
                .get_all(tag_id, index=TagsPerAgentIndexes.TagId)
                .delete()
                .run(conn)
            )

    except Exception as e:
        logger.exception(e)

    return data

@time_it
@db_create_close
@return_status_tuple
def delete_tag_ids_from_agent(agent_id, tag_ids=None, conn=None):
    """Delete 1 or multiple tags from an agent.
    Args:
        agent_id (str): 36 character UUID of a agent.

    Kwargs:
        tag_ids (list): List of tag ids to remove from an agent.
            default=None (Remove all tags from an agent)

    Basic Usage:
        >>> from vFense.core.tag._db import delete_tag_ids_from_agent
        >>> agent_id = '52faa1db-290a-47a7-a4cf-e4ad70e25c38'
        >>> tag_ids = ['tag1', 'tag2']
        >>> delete_tag_ids_from_agent(agent_id, tag_ids)

    Return:
        Tuple (status_code, count, error, generated ids)
        >>> (2001, 1, None, [])
    """
    data = {}

    try:
        if tag_ids:
            data = (
                r
                .expr(tag_ids)
                .for_each(
                    lambda tag_id:
                    r
                    .table(TagCollections.TagsPerAgent)
                    .get_all(
                        [agent_id, tag_id],
                        index=TagsPerAgentIndexes.AgentIdAndTagId
                    )
                    .delete()
                )
                .run(conn)
            )

        else:
            data = (
                r
                .table(TagCollections.TagsPerAgent)
                .get_all(agent_id, index=TagsPerAgentIndexes.AgentId)
                .delete()
                .run(conn)
            )

    except Exception as e:
        logger.exception(e)

    return data


@time_it
def add_agents_to_tag(tag_data):
    """ Add an agent to a tag into the database
        This function should not be called directly.
    Args:
        tag_data (list|dict): List or a dictionary of the data
            you are inserting.

    Basic Usage:
        >>> from vFense.tag._db import add_agents_to_tag
        >>> tag_data = {'tag_id': 'tag_id', 'agent_id': 'agent_id'}
        >>> add_agents_to_tag(tag_data)

    Returns:
        Tuple (status_code, count, error, generated ids)
        >>> (2001, 1, None, [])
    """
    data = (
        insert_data_in_table(
            tag_data, TagCollections.TagsPerAgent
        )
    )
    return data

@time_it
def add_tags_to_agent(tag_data):
    """ Add a tag to an agnt into the database
        This function should not be called directly.
    Args:
        tag_data (list|dict): List or a dictionary of the data
            you are inserting.

    Basic Usage:
        >>> from vFense.tag._db import add_tags_to_agent
        >>> tag_data = {'tag_id': 'tag_id', 'agent_id': 'agent_id'}
        >>> add_tags_to_agent(tag_data)

    Returns:
        Tuple (status_code, count, error, generated ids)
        >>> (2001, 1, None, [])
    """
    data = (
        insert_data_in_table(
            tag_data, TagCollections.TagsPerAgent
        )
    )
    return data


@time_it
def insert_tag(tag_data):
    """ Insert a new tag and its properties into the database
        This function should not be called directly.
    Args:
        tag_data (dict): Dictionary of the data you are inserting.

    Basic Usage:
        >>> from vFense.tag._db import insert_tag
        >>> tag_data = {'view_name': 'global', 'needs_reboot': 'no'}
        >>> insert_tag(tag_data)

    Returns:
        Tuple (status_code, count, error, generated ids)
        >>> (2001, 1, None, [])
    """
    data = (
        insert_data_in_table(
            tag_data, TagCollections.Tags
        )
    )
    return data



@time_it
def delete_tag(tag_id):
    """ Delete a tag and its properties from the database
        This function should not be called directly.
    Args:
        tag_id (str): 36 character UUID of the tag.

    Basic Usage:
        >>> from vFense.tag._db import delete_tag
        >>> tag_id = ""
        >>> delete_tag(tag_id)

    Returns:
        Tuple (status_code, count, error, generated ids)
        >>> (2001, 1, None, [])
    """
    data = (
        delete_data_in_table(
            tag_id, TagCollections.Tags
        )
    )
    return data



@time_it
def update_tag(tag_id, tag_data):
    """ Update a tag and its properties in the database
        This function should not be called directly.
    Args:
        tag_id (str): 36 character UUID of the tag.
        tag_data (dict): Dictionary of the data you are updating.

    Basic Usage:
        >>> from vFense.tag._db import update_tag
        >>> tag_id = ""
        >>> tag_data = {'production_level': 'Development'}
        >>> udpate_tag(tag_id, tag_data)

    Returns:
        Tuple (status_code, count, error, generated ids)
        >>> (2001, 1, None, [])
    """
    data = (
        update_data_in_table(
            tag_id, tag_data, TagCollections.Tags
        )
    )
    return data
