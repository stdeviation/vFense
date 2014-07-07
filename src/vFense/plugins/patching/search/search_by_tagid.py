import logging
import logging.config
from vFense import VFENSE_LOGGING_CONFIG

from vFense.plugins.patching.search._db_search_by_tagid import (
    FetchAppsByTagId
)

from vFense.plugins.patching.search.base_search import RetrieveAppsBase

from vFense.plugins.patching._db_model import (
    AppCollections, DbCommonAppKeys
)
from vFense.plugins.patching._constants import (
    CommonAppKeys, CommonSeverityKeys
)
from vFense.core._constants import (
    SortValues, DefaultQueryValues, CommonKeys
)

from vFense.result.status_codes import (
    GenericCodes, GenericFailureCodes
)
from vFense.result._constants import (
    ApiResultKeys
)


logging.config.fileConfig(VFENSE_LOGGING_CONFIG)
logger = logging.getLogger('rvapi')

class RetrieveAppsByTagId(RetrieveAppsBase):
    """
        This class is used to query for applications for a tag.
    """
    def __init__(self, tag_id,
                 count=DefaultQueryValues.COUNT,
                 offset=DefaultQueryValues.OFFSET,
                 sort=SortValues.ASC,
                 sort_key=DbCommonAppKeys.Name,
                 show_hidden=CommonKeys.NO):
        """
        Args:
            tag_id (str):The tag_id you are performing these application
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
        self.tag_id = tag_id

        self.fetch_apps = (
            FetchAppsByTagId(
                self.tag_id, count, offset,
                sort, sort_key, show_hidden
            )
        )


class RetrieveCustomAppsByTagId(RetrieveAppsByTagId):
    """
        This class is used to query for applications for a tag.
    """
    def __init__(self, tag_id,
                 count=DefaultQueryValues.COUNT,
                 offset=DefaultQueryValues.OFFSET,
                 sort=SortValues.ASC,
                 sort_key=DbCommonAppKeys.Name,
                 show_hidden=CommonKeys.NO):
        """
        Args:
            tag_id (str):The tag_id you are performing these application
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
        self.tag_id = tag_id

        apps_collection = AppCollections.CustomApps
        apps_per_agent_collection = AppCollections.CustomAppsPerAgent

        self.fetch_apps = (
            FetchAppsByTagId(
                self.tag_id, count, offset,
                sort, sort_key, show_hidden,
                apps_collection, apps_per_agent_collection
            )
        )


class RetrieveSupportedAppsByTagId(RetrieveAppsByTagId):
    """
        This class is used to query for applications for a tag.
    """
    def __init__(self, tag_id,
                 count=DefaultQueryValues.COUNT,
                 offset=DefaultQueryValues.OFFSET,
                 sort=SortValues.ASC,
                 sort_key=DbCommonAppKeys.Name,
                 show_hidden=CommonKeys.NO):
        """
        Args:
            tag_id (str):The tag_id you are performing these application
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
        self.tag_id = tag_id

        apps_collection = AppCollections.SupportedApps
        apps_per_agent_collection = AppCollections.SupportedAppsPerAgent

        self.fetch_apps = (
            FetchAppsByTagId(
                self.tag_id, count, offset,
                sort, sort_key, show_hidden,
                apps_collection, apps_per_agent_collection
            )
        )


class RetrieveAgentAppsByTagId(RetrieveAppsByTagId):
    """
        This class is used to query for applications for a tag.
    """
    def __init__(self, tag_id,
                 count=DefaultQueryValues.COUNT,
                 offset=DefaultQueryValues.OFFSET,
                 sort=SortValues.ASC,
                 sort_key=DbCommonAppKeys.Name,
                 show_hidden=CommonKeys.NO):
        """
        Args:
            tag_id (str):The tag_id you are performing these application
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
        self.tag_id = tag_id

        apps_collection = AppCollections.vFenseApps
        apps_per_agent_collection = AppCollections.vFenseAppsPerAgent

        self.fetch_apps = (
            FetchAppsByTagId(
                self.tag_id, count, offset,
                sort, sort_key, show_hidden,
                apps_collection, apps_per_agent_collection
            )
        )
