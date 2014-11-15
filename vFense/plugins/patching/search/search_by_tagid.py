from vFense.plugins.patching.search._db_search_by_tagid import (
    FetchAppsByTagId
)
from vFense.plugins.patching.search.base_search import RetrieveAppsBase
from vFense.plugins.patching._db_model import (
    AppCollections, DbCommonAppKeys
)
from vFense.core._constants import CommonKeys

class RetrieveAppsByTagId(RetrieveAppsBase):
    """
        This class is used to query for applications for a tag.
    """
    def __init__(
        self, tag_id=None, sort_key=DbCommonAppKeys.Name,
        show_hidden=CommonKeys.NO,
        apps_collection=AppCollections.UniqueApplications,
        apps_per_agent_collection=AppCollections.AppsPerAgent, **kwargs
    ):
        """
        Kwargs:
            tag_id (str):The tag_id you are performing these application
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
        super(RetrieveAppsByTagId, self).__init__(**kwargs)
        self.tag_id = tag_id
        self.sort_key = sort_key
        self.show_hidden = show_hidden
        self.fetch_apps = (
            FetchAppsByTagId(
                tag_id=self.tag_id, count=self.count,
                offset=self.offset, sort=self.sort,
                sort_key=self.sort_key, show_hidden=self.show_hidden,
                apps_collection=self.apps_collection,
                apps_per_agent_collection=self.apps_per_agent_collection
            )
        )


class RetrieveCustomAppsByTagId(RetrieveAppsByTagId):
    """
        This class is used to query for applications for a tag.
    """
    def __init__(self, **kwargs):
        self.apps_collection = AppCollections.CustomApps
        self.apps_per_agent_collection = AppCollections.CustomAppsPerAgent
        self.fetch_apps = (
            FetchAppsByTagId(
                tag_id=self.tag_id, count=self.count,
                offset=self.offset, sort=self.sort,
                sort_key=self.sort_key, show_hidden=self.show_hidden,
                apps_collection=self.apps_collection,
                apps_per_agent_collection=self.apps_per_agent_collection
            )
        )


class RetrieveSupportedAppsByTagId(RetrieveAppsByTagId):
    """
        This class is used to query for applications for a tag.
    """
    def __init__(self, **kwargs):
        self.apps_collection = AppCollections.SupportedApps
        self.apps_per_agent_collection = AppCollections.SupportedAppsPerAgent

        self.fetch_apps = (
            FetchAppsByTagId(
                tag_id=self.tag_id, count=self.count,
                offset=self.offset, sort=self.sort,
                sort_key=self.sort_key, show_hidden=self.show_hidden,
                apps_collection=self.apps_collection,
                apps_per_agent_collection=self.apps_per_agent_collection
            )
        )


class RetrieveAgentAppsByTagId(RetrieveAppsByTagId):
    """
        This class is used to query for applications for a tag.
    """
    def __init__(self, **kwargs):
        self.apps_collection = AppCollections.vFenseApps
        self.apps_per_agent_collection = AppCollections.vFenseAppsPerAgent

        self.fetch_apps = (
            FetchAppsByTagId(
                tag_id=self.tag_id, count=self.count,
                offset=self.offset, sort=self.sort,
                sort_key=self.sort_key, show_hidden=self.show_hidden,
                apps_collection=self.apps_collection,
                apps_per_agent_collection=self.apps_per_agent_collection
            )
        )
