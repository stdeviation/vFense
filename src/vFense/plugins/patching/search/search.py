import logging
import logging.config
from vFense import VFENSE_LOGGING_CONFIG

from vFense.plugins.patching._db_model import (
    AppCollections, DbCommonAppKeys
)
from vFense.plugins.patching._constants import (
    CommonAppKeys, CommonSeverityKeys
)
from vFense.core._constants import (
    SortValues, DefaultQueryValues, CommonKeys
)
from vFense.core.view._constants import DefaultViews
from vFense.plugins.patching.search._db_search import FetchApps
from vFense.plugins.patching.search.base_search import RetrieveAppsBase

from vFense.result.status_codes import (
    GenericCodes, GenericFailureCodes
)
from vFense.result._constants import (
    ApiResultKeys
)

logging.config.fileConfig(VFENSE_LOGGING_CONFIG)
logger = logging.getLogger('rvapi')


class RetrieveApps(RetrieveAppsBase):
    """
        This class is used to query for applications.
    """

    def by_id(self, app_id):
        """Retrieve all information about an application by its app_id.
        Args:
            app_id (str): 64 character hexdigest of the application

        Basic Usage:
            >>> from vFense.plugins.patching.search.search import RetrieveApps
            >>> fetch = RetrieveApps()
            >>> fetch.by_id('138051177c8c97bc0d4af440ac62e1ba82991962fa01a4dd76b91963e8424435')

        Results:
            Dictionary of the application data.
            >>>
                {
                    "count": 1,
                    "data": {
                        "kb": "",
                        "rv_severity": "Recommended",
                        "vendor_name": "",
                        "support_url": "http://www.abisource.com/",
                        "description": "efficient, featureful word processor with collaboration\n AbiWord is a full-featured, efficient word processing application.\n It is suitable for a wide variety of word processing tasks, and\n is extensible with a variety of plugins.\n .\n This package includes many of the available import/export plugins allowing\n AbiWord to interact with ODT, WordPerfect, and other formats.  It also\n includes tools plugins, offering live collaboration with AbiWord users\n on Linux and Windows (using TCP or Jabber/XMPP), web translation and\n dictionary support, and more.\n .\n Additional plugins that require significant amounts of extra software to\n function are in the various abiword-plugin-* packages.",
                        "vulnerability_categories": [],
                        "agent_stats": [
                            {
                                "count": 1,
                                "status": "installed",
                                "name": "Installed"
                            },
                            {
                                "count": 0,
                                "status": "available",
                                "name": "Available"
                            },
                            {
                                "count": 0,
                                "status": "pending",
                                "name": "Pending"
                            }
                        ],
                        "release_date": 0,
                        "vendor_severity": "recommended",
                        "app_id": "138051177c8c97bc0d4af440ac62e1ba82991962fa01a4dd76b91963e8424435",
                        "reboot_required": "no",
                        "os_code": "linux",
                        "repo": "",
                        "files_download_status": 5006,
                        "version": "3.0.0-4ubuntu1",
                        "cve_ids": [],
                        "hidden": "no",
                        "uninstallable": "yes",
                        "vulnerability_id": "",
                        "name": "abiword"
                    },
                    "message": "dataset retrieved",
                    "vfense_status_code": 1001,
                    "generic_status_code": 1001
                }
        """
        count, data = self.fetch_apps.by_id(app_id)
        generic_status_code = GenericCodes.InformationRetrieved

        if count == 0:
            vfense_status_code = GenericFailureCodes.DataIsEmpty
            msg = 'dataset is empty'

        else:
            vfense_status_code = GenericCodes.InformationRetrieved
            msg = 'dataset retrieved'

        results = (
            self._set_results(
                generic_status_code, vfense_status_code,
                msg, count, data
            )
        )
        return results


    def _set_results(self, gen_status_code, vfense_status_code,
                     msg, count, data):

        results = {
            ApiResultKeys.GENERIC_STATUS_CODE: gen_status_code,
            ApiResultKeys.VFENSE_STATUS_CODE: vfense_status_code,
            ApiResultKeys.MESSAGE: msg,
            ApiResultKeys.COUNT: count,
            ApiResultKeys.DATA: data,
        }

        return(results)


class RetrieveCustomApps(RetrieveApps):
    """
        This class is used to query for applications.
    """
    def __init__(self, view_name=None,
                 count=DefaultQueryValues.COUNT,
                 offset=DefaultQueryValues.OFFSET,
                 sort=SortValues.ASC,
                 sort_key=DbCommonAppKeys.Name,
                 show_hidden=CommonKeys.NO):
        """
        Kwargs:
            view_name (str):The view you are performing this query on.
                default=None
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
        apps_collection = AppCollections.vFenseApps
        apps_collection = AppCollections.CustomApps
        apps_per_agent_collection = AppCollections.CustomAppsPerAgent

        if view_name == DefaultViews.GLOBAL:
            view_name = None

        self.fetch_apps = (
            FetchApps(
                view_name, count, offset,
                sort, sort_key, show_hidden,
                apps_collection, apps_per_agent_collection
            )
        )

class RetrieveSupportedApps(RetrieveApps):
    """
        This class is used to query for applications.
    """
    def __init__(self, view_name=None,
                 count=DefaultQueryValues.COUNT,
                 offset=DefaultQueryValues.OFFSET,
                 sort=SortValues.ASC,
                 sort_key=DbCommonAppKeys.Name,
                 show_hidden=CommonKeys.NO):
        """
        Kwargs:
            view_name (str):The view you are performing this query on.
                default=None
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
        apps_collection = AppCollections.vFenseApps
        apps_collection = AppCollections.SupportedApps
        apps_per_agent_collection = AppCollections.SupportedAppsPerAgent

        if view_name == DefaultViews.GLOBAL:
            view_name = None

        self.fetch_apps = (
            FetchApps(
                view_name, count, offset,
                sort, sort_key, show_hidden,
                apps_collection, apps_per_agent_collection
            )
        )

class RetrieveAgentApps(RetrieveApps):
    """
        This class is used to query for applications.
    """
    def __init__(self, view_name=None,
                 count=DefaultQueryValues.COUNT,
                 offset=DefaultQueryValues.OFFSET,
                 sort=SortValues.ASC,
                 sort_key=DbCommonAppKeys.Name,
                 show_hidden=CommonKeys.NO):
        """
        Kwargs:
            view_name (str):The view you are performing this query on.
                default=None
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
        apps_collection = AppCollections.vFenseApps
        apps_per_agent_collection = AppCollections.vFenseAppsPerAgent

        if view_name == DefaultViews.GLOBAL:
            view_name = None

        self.fetch_apps = (
            FetchApps(
                view_name, count, offset,
                sort, sort_key, show_hidden,
                apps_collection, apps_per_agent_collection
            )
        )
