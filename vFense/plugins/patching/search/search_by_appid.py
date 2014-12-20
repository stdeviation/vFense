from vFense.core.agent._db_model import AgentKeys
from vFense.plugins.patching._db_model import (
    AppCollections
)
from vFense.plugins.patching._constants import CommonAppKeys
from vFense.plugins.patching.search._db_search_by_appid import (
    FetchAgentsByAppId
)
from vFense.plugins.patching.search.base_search import RetrieveAppsBase


class RetrieveAgentsByAppId(RetrieveAppsBase):
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
                app_id=self.app_id, count=self.count,
                offset=self.offset, sort=self.sort,
                sort_key=self.sort_key, show_hidden=self.show_hidden,
                apps_collection=self.apps_collection,
                apps_per_agent_collection=self.apps_per_agent_collection
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
        super(RetrieveAgentsByCustomAppId, self).__init__(**kwargs)
        self.apps_collection = AppCollections.CustomApps
        self.apps_per_agent_collection = AppCollections.CustomAppsPerAgent

        self.fetch = (
            FetchAgentsByAppId(
                app_id=self.app_id, count=self.count, offset=self.offset,
                sort=self.sort, sort_key=self.sort_key,
                apps_collectioon=self.apps_collection,
                apps_per_agent_collection=self.apps_per_agent_collection
            )
        )


class RetrieveAgentsBySupportedAppId(RetrieveAgentsByAppId):
    """
        This class is used to get agent data from within the Packages Page
    """
    def __init__(self, **kwargs):
        super(RetrieveAgentsBySupportedAppId, self).__init__(**kwargs)
        self.apps_collection = AppCollections.SupportedApps
        self.apps_per_agent_collection = AppCollections.SupportedAppsPerAgent

        self.fetch = (
            FetchAgentsByAppId(
                app_id=self.app_id, count=self.count, offset=self.offset,
                sort=self.sort, sort_key=self.sort_key,
                apps_collectioon=self.apps_collection,
                apps_per_agent_collection=self.apps_per_agent_collection
            )
        )

class RetrieveAgentsByAgentAppId(RetrieveAgentsByAppId):
    """
        This class is used to get agent data from within the Packages Page
    """
    def __init__(self, **kwargs):
        super(RetrieveAgentsByAgentAppId, self).__init__(**kwargs)
        self.apps_collection = AppCollections.vFenseApps
        self.apps_per_agent_collection = AppCollections.vFenseAppsPerAgent

        self.fetch = (
            FetchAgentsByAppId(
                app_id=self.app_id, count=self.count, offset=self.offset,
                sort=self.sort, sort_key=self.sort_key,
                apps_collectioon=self.apps_collection,
                apps_per_agent_collection=self.apps_per_agent_collection
            )
        )
