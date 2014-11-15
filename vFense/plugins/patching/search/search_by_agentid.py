from vFense.core._constants import CommonKeys
from vFense.plugins.patching._db_model import (
    AppCollections, DbCommonAppKeys
)
from vFense.plugins.patching.search._db_search_by_agentid import (
    FetchAppsByAgentId
)
from vFense.plugins.patching.search.base_search import RetrieveAppsBase

class RetrieveAppsByAgentId(RetrieveAppsBase):
    """
        This class is used to query for applications for an agent.
    """
    def __init__(
        self, agent_id=None, sort_key=DbCommonAppKeys.Name,
        show_hidden=CommonKeys.NO,
        apps_collection=AppCollections.UniqueApplications,
        apps_per_agent_collection=AppCollections.AppsPerAgent, **kwargs
    ):
        """
        Kwargs:
            agent_id (str):The agent_id you are performing these application
                searches for.
            show_hidden (str): Return applications that have been hidden.
                default="no"
            apps_collection (str): The name of the appliaction table,
                that is going to be used to begin the search.
                default='unique_applications'
            apps_per_agent_collection (str): The name of the applications
                per agent table, that is going to be used to begin the
                search.
                default='apps_per_agent'

            For the rest of the kwargs, please check vFense.search.base
        """
        super(RetrieveAppsByAgentId, self).__init__(**kwargs)
        self.agent_id = agent_id
        self.sort_key = sort_key
        self.show_hidden = show_hidden
        self.fetch_apps = (
            FetchAppsByAgentId(
                agent_id=self.agent_id, count=self.count,
                offset=self.offset, sort=self.sort,
                sort_key=self.sort_key, show_hidden=self.show_hidden,
                apps_collection=self.apps_collection,
                apps_per_agent_collection=self.apps_per_agent_collection
            )
        )


class RetrieveCustomAppsByAgentId(RetrieveAppsByAgentId):
    """
        This class is used to get agent data from within the Packages Page
    """

    def __init__(self, **kwargs):
        super(RetrieveCustomAppsByAgentId, self).__init__(**kwargs)
        self.apps_collection = AppCollections.CustomApps
        self.apps_per_agent_collection = AppCollections.CustomAppsPerAgent

        self.fetch_apps = (
            FetchAppsByAgentId(
                agent_id=self.agent_id, count=self.count,
                offset=self.offset, sort=self.sort,
                sort_key=self.sort_key, show_hidden=self.show_hidden,
                apps_collection=self.apps_collection,
                apps_per_agent_collection=self.apps_per_agent_collection
            )
        )

class RetrieveSupportedAppsByAgentId(RetrieveAppsByAgentId):
    """
        This class is used to get agent data from within the Packages Page
    """
    def __init__(self, **kwargs):
        super(RetrieveSupportedAppsByAgentId, self).__init__(**kwargs)
        self.apps_collection = AppCollections.SupportedApps
        self.apps_per_agent_collection = AppCollections.SupportedAppsPerAgent

        self.fetch_apps = (
            FetchAppsByAgentId(
                agent_id=self.agent_id, count=self.count,
                offset=self.offset, sort=self.sort,
                sort_key=self.sort_key, show_hidden=self.show_hidden,
                apps_collection=self.apps_collection,
                apps_per_agent_collection=self.apps_per_agent_collection
            )
        )

class RetrieveAgentAppsByAgentId(RetrieveAppsByAgentId):
    def __init__(self, **kwargs):
        super(RetrieveAgentAppsByAgentId, self).__init__(**kwargs)
        self.apps_collection = AppCollections.vFenseApps
        self.apps_per_agent_collection = AppCollections.vFenseAppsPerAgent

        self.fetch_apps = (
            FetchAppsByAgentId(
                agent_id=self.agent_id, count=self.count,
                offset=self.offset, sort=self.sort,
                sort_key=self.sort_key, show_hidden=self.show_hidden,
                apps_collection=self.apps_collection,
                apps_per_agent_collection=self.apps_per_agent_collection
            )
        )

