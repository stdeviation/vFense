import logging
from time import time

from vFense import VFENSE_LOGGING_CONFIG
from vFense.core._constants import CommonKeys
from vFense.core._db_constants import DbTime
from vFense.core.agent._db_model import AgentKeys
from vFense.core.agent._constants import AgentVirtualKeys, \
    AgentStatusKeys, ProductionLevels

from vFense.core.agent._db import fetch_production_levels_from_agent, \
    fetch_supported_os_strings, fetch_agent_ids, fetch_agents, \
    fetch_agent, \
    update_agent

from vFense.core.decorators import time_it

from vFense.db.hardware import Hardware
#from vFense.errorz.results import Results
from vFense.errorz._constants import ApiResultKeys
from vFense.errorz.status_codes import DbCodes, GenericCodes,\
    AgentCodes, AgentFailureCodes, GenericFailureCodes, \
    AgentResultCodes, AgentFailureResultCodes
#from vFense.plugins.patching._db_model import *

logging.config.fileConfig(VFENSE_LOGGING_CONFIG)
logger = logging.getLogger('rvapi')


@time_it
def get_production_levels(view_name):
    """Retrieve all the production levels that is in the database.
    Args:
        view_name (str): Name of the view, where the agent is located.

    Basic Usage:
        >>> from vFense.core.agent.agents import get_production_levels
        >>> view_name = 'default'
        >>> get_production_levels(view_name)
        [
            u'Development',
            u'Production'
        ]
    """
    data = fetch_production_levels_from_agent(view_name)
    return data

@time_it
def get_supported_os_codes():
    """Retrieve all the base operating systems codes
        that is in the database.

    Basic Usage:
        >>> from vFense.core.agent.agents import get_supported_os_codes
        >>> get_supported_os_codes()
        [
            u'windows',
            u'linux',
            u'darwin',
        ]
    """
    oses = ['windows', 'linux', 'darwin']
    return oses

@time_it
def get_supported_os_strings(view_name):
    """Retrieve all the operating systems that is in the database.
    Args:
        view_name (str): Name of the view, where the agent is located.

    Basic Usage:
        >>> from vFense.core.agent.agents import get_supported_os_strings
        >>> view_name = 'default'
        >>> get_supported_os_strings(view_name)
        [
            u'CentOS 6.5',
            u'Ubuntu 12.04',
            u'Windows 7 Professional Service Pack 1',
            u'Windows 8.1 '
        ]
    """
    data = fetch_supported_os_strings(view_name)
    return data

@time_it
def get_all_agent_ids(view_name=None, agent_os=None):
    """Retrieve all agent_ids by either view_name or os code.
    Kwargs:
        view_name (str, optional): Name of the view, where the agent
            is located
        agent_os (str, optional): linux or windows or darwin

    Basic Usage::
        >>> from vFense.core.agent.agents import get_all_agent_ids
        >>> view_name = 'default'
        >>> agent_os = 'os_code'
        >>> get_all_agent_ids(view_name, agent_os)
        [
            u'52faa1db-290a-47a7-a4cf-e4ad70e25c38',
            u'3ea8fd7a-8aad-40da-aff0-8da6fa5f8766'
        ]
    """

    if agent_os and view_name:
        agents = fetch_agent_ids(view_name, agent_os)

    elif agent_os and not view_name:
        agents = fetch_agent_ids(agent_os=agent_os)

    elif not agent_os and view_name:
        agents = fetch_agent_ids(view_name)

    elif not agent_os and not view_name:
        agents = fetch_agent_ids()

    return agents

@time_it
def get_agents_info(view_name=None, agent_os=None, keys_to_pluck=None):
    """Retrieve a list of agents by os code and or view name.

    Kwargs:
        view_name (str, optional): Name of the view, where the agent
            is located
        agent_os (str, optional): The operating system you are filtering for.
            Ex: linux or windows or darwin
        keys_to_pluck (list, optional): List of specific keys that you
            are retrieving from the database.

    Basic Usage:
        >>> from vFense.core.agent.agents import get_agents_info
        >>> os_code = 'linux'
        >>> pluck = ['computer_name', 'agent_id']
        >>> get_agents_info(view_name, os_code, keys_to_pluck=pluck)

    Returns:
        (list): list of dictionaries with agent data
            Ex:
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

    if agent_os and not keys_to_pluck and view_name:
        agents = (
            fetch_agents(
                view_name=view_name,
                filter_key=AgentKeys.OsCode,
                filter_val=agent_os
            )
        )

    elif agent_os and not keys_to_pluck and not view_name:
        agents = (
            fetch_agents(
                filter_key=AgentKeys.OsCode,
                filter_val=agent_os
            )
        )

    elif agent_os and keys_to_pluck and view_name:
        agents = (
            fetch_agents(
                view_name=view_name,
                filter_key=AgentKeys.OsCode,
                filter_val=agent_os,
                keys_to_pluck=keys_to_pluck,
            )
        )

    elif agent_os and keys_to_pluck and not view_name:
        agents = (
            fetch_agents(
                filter_key=AgentKeys.OsCode,
                filter_val=agent_os,
                keys_to_pluck=keys_to_pluck,
            )
        )

    elif not agent_os and keys_to_pluck and view_name:
        agents = (
            fetch_agents(
                view_name=view_name,
                keys_to_pluck=keys_to_pluck,
            )
        )

    elif not agent_os and keys_to_pluck and not view_name:
        agents = (
            fetch_agents(
                keys_to_pluck=keys_to_pluck,
            )
        )

    elif not agent_os and not keys_to_pluck and not view_name:
        agents = (
            fetch_agents()
        )

    elif not agent_os and not keys_to_pluck and view_name:
        agents = (
            fetch_all_agents_for_view(view_name)
        )

    return agents


@time_it
def get_agent_info(agent_id, keys_to_pluck=None):
    """Retrieve agent information.
    Args:
        agent_id (str): 36 character uuid of the agent you are updating.

    Kwargs:
        keys_to_pluck (list, optional): List of specific keys that
        you are retrieving from the database.

    Basic Usage::
        >>> from vFense.core.agent.agents import get_agent_info
        >>> agent_id = '52faa1db-290a-47a7-a4cf-e4ad70e25c38'
        >>> keys_to_pluck = ['production_level', 'needs_reboot']
        >>> get_agent_info(agent_id, keys_to_pluck)
        {
            u'agent_id': u'52faa1db-290a-47a7-a4cf-e4ad70e25c38',
            u'production_level': u'Development'
        }
    """

    return fetch_agent(agent_id, keys_to_pluck)


@time_it
def update_agent_status(agent_id, username=None, uri=None, method=None):
    """Update the status of an agent.
    Args:
        agent_id (str): 36 character uuid of the agent you are updating.

    Kwargs:
        user_name (str): The name of the user who called this function.
        uri (str): The uri that was used to call this function.
        method (str): The HTTP methos that was used to call this function.

    Basic Usage:
        >>> from vFense.core.agent.agents import update_agent_status
        >>> agent_id = '0a1f9a3c-9200-42ef-ba63-f4fd17f0644c'
        >>> update_agent_status(agent_id)
        {
            'uri': None,
            'rv_status_code': 1008,
            'http_method': None,
            'http_status': 200,
            'message': 'admin - agent 52faa1db-290a-47a7-a4cf-e4ad70e25c38 was updated',
            'data': {'needs_reboot': 'no'}
        }
    """
    status = update_agent_status.func_name + ' - '
    now = time()
    agent_data = {
        AgentKeys.LastAgentUpdate: DbTime.epoch_time_to_db_time(now),
        AgentKeys.AgentStatus: 'up'
    }
    status_code, count, error, generated_ids = (
        update_agent(agent_id, agent_data)
    )
    if status_code == DbCodes.Replaced:
        msg = 'agent_id %s updated'
        generic_status_code = GenericCodes.ObjectUpdated
        vfense_status_code = AgentCodes.AgentsUpdated

    elif status_code == DbCodes.Skipped:
        msg = 'agent_id %s does not exist'
        generic_status_code = GenericFailureCodes.FailedToUpdateObject
        vfense_status_code = AgentFailureCodes.AgentsDoesNotExist

    elif status_code == DbCodes.Errors:
        msg = 'agent_id %s could not be updated'
        generic_status_code = GenericFailureCodes.FailedToUpdateObject
        vfense_status_code = AgentFailureCodes.AgentsFailedToUpdate

    agent_data[AgentKeys.LastAgentUpdate] = now

    results = {
        ApiResultKeys.DB_STATUS_CODE: status_code,
        ApiResultKeys.GENERIC_STATUS_CODE: generic_status_code,
        ApiResultKeys.VFENSE_STATUS_CODE: vfense_status_code,
        ApiResultKeys.MESSAGE: status + msg,
        ApiResultKeys.DATA: [],
        ApiResultKeys.USERNAME: username,
        ApiResultKeys.URI: uri,
        ApiResultKeys.HTTP_METHOD: method
    }

    return results

def remove_all_agents_for_view(
        view_name,
        user_name=None, uri=None, method=None
    ):
    """Remove all agents from the system, filtered by view_name
    Args:
        view_name (str): The name of the view.

    Kwargs:
        user_name (str): The name of the user who called this function.
        uri (str): The uri that was used to call this function.
        method (str): The HTTP methos that was used to call this function.

    Basic Usage:
        >>> from vFense.core.agent.agents import remove_all_agents_for_view
        >>> view_name = 'tester'
        >>> remove_all_agents_for_view(view_name)
    """
    status = remove_all_agents_for_view.func_name + ' - '

    status_code, count, error, generated_ids = (
        delete_all_agents_for_view(view_name)
    )
    msg = 'total number of agents deleted: %s' % (str(count))
    if status_code == DbCodes.Deleted:
        generic_status_code = GenericCodes.ObjectDeleted
        vfense_status_code = AgentCodes.AgentsDeleted

    elif status_code == DbCodes.Skipped:
        generic_status_code = GenericCodes.DoesNotExist
        vfense_status_code = AgentFailureCodes.AgentsDoesNotExist

    elif status_code == DbCodes.DoesNotExist:
        generic_status_code = GenericCodes.DoesNotExist
        vfense_status_code = AgentFailureCodes.AgentsDoesNotExist

    elif status_code == DbCodes.Errors:
        generic_status_code = GenericFailureCodes.FailedToDeleteObject
        vfense_status_code = AgentFailureCodes.AgentsFailedToDelete

    results = {
        ApiResultKeys.DB_STATUS_CODE: status_code,
        ApiResultKeys.GENERIC_STATUS_CODE: generic_status_code,
        ApiResultKeys.VFENSE_STATUS_CODE: vfense_status_code,
        ApiResultKeys.MESSAGE: status + msg,
        ApiResultKeys.DATA: [],
        ApiResultKeys.USERNAME: user_name,
        ApiResultKeys.URI: uri,
        ApiResultKeys.HTTP_METHOD: method
    }

    return results


@time_it
def validate_agent_ids_in_views(agent_ids, views):
    """Validate a list of agent ids against a view.
    Args:
        agent_ids (list): List of agent ids.
        views (list): List of view names.

    Basic Usage:
        >>> from vFense.agent.agents import validate_agent_ids_in_views
        >>> agent_ids = ['agent1', 'agent2']
        >>> views = ['global', 'test1']
        >>> validate_agent_ids_in_views(agent_ids, views)

    Return:
        Tuple - (Boolean, [valid list], [invalid list])
        (False, ['tag1'], ['tag2'])
    """
    validated = False
    invalid_ids = []
    valid_ids = []
    if isinstance(agent_ids, list) and isinstance(views, list):
        for agent_id in agent_ids:
            agent = fetch_agent(agent_id)
            if agent:
                if set(agent[AgentKeys.Views]).issuperset(views):
                    valid_ids.append(agent_id)
                else:
                    invalid_ids.append(agent_id)

    if valid_ids and not invalid_ids:
        validated = True

    return(validated, valid_ids, invalid_ids)
