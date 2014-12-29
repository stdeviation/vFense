from vFense.core.agent._db_model import AgentKeys
from vFense.plugins.patching._db_model import (
    AppCollections
)
from vFense.plugins.patching._constants import CommonAppKeys
from vFense.plugins.patching.search._db_search_by_appid import (
    FetchAgentsByAppId
)
from vFense.core.agent.search.search import RetrieveAgents


class RetrieveAgentsByAppId(RetrieveAgents):
    """
        This class is used to get agent data from within the Packages Page
    """
    def __init__(
        self, app_id=None, sort_key=AgentKeys.ComputerName,
        apps_collection=AppCollections.UniqueApplications,
        apps_per_agent_collection=AppCollections.AppsPerAgent, **kwargs
    ):
        super(RetrieveAgentsByAppId, self).__init__(**kwargs)
        self.app_id = app_id
        self.sort_key = sort_key
        self.fetch = (
            FetchAgentsByAppId(
                app_id=self.app_id, count=self.count, view_name=self.view_name,
                offset=self.offset, sort=self.sort, sort_key=self.sort_key,
                apps_collection=apps_collection,
                apps_per_agent_collection=apps_per_agent_collection
            )
        )

    def by_status(self, status):
        if status in CommonAppKeys.ValidPackageStatuses:
            count, data = self.fetch.by_status(status)
            return self._base(count, data)

        else:
            return self._set_results_invalid_filter_key(status)

    def by_name(self, name):
        count, data = self.fetch.by_name(name)
        return self._base(count, data)

    def by_status_and_name(self, status, name):
        if status in CommonAppKeys.ValidPackageStatuses:
            count, data = self.fetch.by_status_and_name(status, name)
            return self._base(count, data)

        else:
            return self._set_results_invalid_filter_key(status)


class RetrieveAgentsByCustomAppId(RetrieveAgentsByAppId):
    """
        This class is used to get agent data from within the Packages Page
    """
    def __init__(self, **kwargs):
        kwargs['apps_collection'] = AppCollections.CustomApps
        kwargs['apps_per_agent_collection'] = AppCollections.CustomAppsPerAgent
        super(RetrieveAgentsByCustomAppId, self).__init__(**kwargs)


class RetrieveAgentsBySupportedAppId(RetrieveAgentsByAppId):
    """
        This class is used to get agent data from within the Packages Page
    """
    def __init__(self, **kwargs):
        kwargs['apps_collection'] = AppCollections.SupportedApps
        kwargs['apps_per_agent_collection'] = (
            AppCollections.SupportedAppsPerAgent
        )
        super(RetrieveAgentsBySupportedAppId, self).__init__(**kwargs)


class RetrieveAgentsByAgentAppId(RetrieveAgentsByAppId):
    """
        This class is used to get agent data from within the Packages Page
    """
    def __init__(self, **kwargs):
        kwargs['apps_collection'] = AppCollections.vFenseApps
        kwargs['apps_per_agent_collection'] = AppCollections.vFenseAppsPerAgent
        super(RetrieveAgentsByAgentAppId, self).__init__(**kwargs)
