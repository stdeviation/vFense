import logging
import logging.config
from vFense._constants import VFENSE_LOGGING_CONFIG
from vFense.plugins.patching.search._db_search_by_agentid import (
    FetchAppsByAgentId
)
from vFense.plugins.patching.search.base_search import RetrieveAppsBase

from vFense.plugins.patching._db_model import (
    AppCollections, DbCommonAppKeys
)
from vFense.core._constants import (
    SortValues, DefaultQueryValues, CommonKeys
)


logging.config.fileConfig(VFENSE_LOGGING_CONFIG)
logger = logging.getLogger('rvapi')

class RetrieveAppsByAgentId(RetrieveAppsBase):
    """
        This class is used to query for applications for an agent.
    """
    def __init__(self, agent_id,
                 count=DefaultQueryValues.COUNT,
                 offset=DefaultQueryValues.OFFSET,
                 sort=SortValues.ASC,
                 sort_key=DbCommonAppKeys.Name,
                 show_hidden=CommonKeys.NO):
        """
        Args:
            agent_id (str):The agent_id you are performing these application
                searches for.
        Kwargs:
            count (int): The amount of applications to return
                default=30
            offset (int): From where to begin the search from (pagination).
                default=0
            sort (str): Sort either ascending or descending (asc or desc).
                default="asc"
            sort_key (str): Key to sort the applications by.
                default="name"
            show_hidden (str): Return applications that have been hidden.
                default="no"
        """
        self.agent_id = agent_id

        self.fetch_apps = (
            FetchAppsByAgentId(
                self.agent_id, count, offset,
                sort, sort_key, show_hidden
            )
        )


class RetrieveCustomAppsByAgentId(RetrieveAppsByAgentId):
    """
        This class is used to get agent data from within the Packages Page
    """

    def __init__(self, agent_id,
                 count=DefaultQueryValues.COUNT,
                 offset=DefaultQueryValues.OFFSET,
                 sort=SortValues.ASC,
                 sort_key=DbCommonAppKeys.Name,
                 show_hidden=CommonKeys.NO):
        """
        Args:
            agent_id (str):The agent_id you are performing these application
                search for.
        Kwargs:
            count (int): The amount of applications to return
                default=30
            offset (int): From where to begin the search from (pagination).
                default=0
            sort (str): Sort either ascending or descending (asc or desc).
                default="asc"
            sort_key (str): Key to sort the applications by.
                default="name"
            show_hidden (str): Return applications that have been hidden.
                default="no"
        """
        self.agent_id = agent_id

        apps_collection = AppCollections.CustomApps
        apps_per_agent_collection = AppCollections.CustomAppsPerAgent

        self.fetch_apps = (
            FetchAppsByAgentId(
                self.agent_id, count, offset,
                sort, sort_key, show_hidden,
                apps_collection, apps_per_agent_collection
            )
        )

class RetrieveSupportedAppsByAgentId(RetrieveAppsByAgentId):
    """
        This class is used to get agent data from within the Packages Page
    """
    def __init__(self, agent_id,
                 count=DefaultQueryValues.COUNT,
                 offset=DefaultQueryValues.OFFSET,
                 sort=SortValues.ASC,
                 sort_key=DbCommonAppKeys.Name,
                 show_hidden=CommonKeys.NO):
        """
        Args:
            agent_id (str):The agent_id you are performing these application
                search for.
        Kwargs:
            count (int): The amount of applications to return
                default=30
            offset (int): From where to begin the search from (pagination).
                default=0
            sort (str): Sort either ascending or descending (asc or desc).
                default="asc"
            sort_key (str): Key to sort the applications by.
                default="name"
            show_hidden (str): Return applications that have been hidden.
                default="no"
        """
        self.agent_id = agent_id

        apps_collection = AppCollections.SupportedApps
        apps_per_agent_collection = AppCollections.SupportedAppsPerAgent

        self.fetch_apps = (
            FetchAppsByAgentId(
                self.agent_id, count, offset,
                sort, sort_key, show_hidden,
                apps_collection, apps_per_agent_collection
            )
        )

class RetrieveAgentAppsByAgentId(RetrieveAppsByAgentId):
    def __init__(self, agent_id,
                 count=DefaultQueryValues.COUNT,
                 offset=DefaultQueryValues.OFFSET,
                 sort=SortValues.ASC,
                 sort_key=DbCommonAppKeys.Name,
                 show_hidden=CommonKeys.NO):
        """
        Args:
            agent_id (str):The agent_id you are performing these application
                search for.
        Kwargs:
            count (int): The amount of applications to return
                default=30
            offset (int): From where to begin the search from (pagination).
                default=0
            sort (str): Sort either ascending or descending (asc or desc).
                default="asc"
            sort_key (str): Key to sort the applications by.
                default="name"
            show_hidden (str): Return applications that have been hidden.
                default="no"
        """
        self.agent_id = agent_id

        apps_collection = AppCollections.vFenseApps
        apps_per_agent_collection = AppCollections.vFenseAppsPerAgent

        self.fetch_apps = (
            FetchAppsByAgentId(
                self.agent_id, count, offset,
                sort, sort_key, show_hidden,
                apps_collection, apps_per_agent_collection
            )
        )
