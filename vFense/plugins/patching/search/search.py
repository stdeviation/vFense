from vFense.plugins.patching._db_model import (
    AppCollections, DbCommonAppKeys
)
from vFense.core._constants import CommonKeys
from vFense.plugins.patching.search._db_search import FetchApps
from vFense.plugins.patching.search.base_search import RetrieveAppsBase


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
                        "vfense_severity": "Recommended",
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
        return self._base(count, data)

class RetrieveCustomApps(RetrieveApps):
    """
        This class is used to query for applications.
    """
    def __init__(
        self, sort_key=DbCommonAppKeys.Name, show_hidden=CommonKeys.NO,
        **kwargs
    ):
        """
        Kwargs:
            show_hidden (str): Return applications that have been hidden.
                default="no"

            For the rest of the kwargs, please check vFense.search._db_base
        """
        super(RetrieveCustomApps, self).__init__(**kwargs)
        self.apps_collection = AppCollections.CustomApps
        self.apps_per_agent_collection = AppCollections.CustomAppsPerAgent

        self.fetch_apps = (
            FetchApps(
                view_name=self.view_name, count=self.count,
                offset=self.offset, sort=self.sort, sort_key=self.sort_key,
                show_hidden=self.show_hidden,
                apps_collections=self.apps_collection,
                apps_per_agent_collection=self.apps_per_agent_collection
            )
        )


class RetrieveSupportedApps(RetrieveApps):
    """
        This class is used to query for applications.
    """
    def __init__(
        self, sort_key=DbCommonAppKeys.Name, show_hidden=CommonKeys.NO,
        **kwargs
    ):
        """
        Kwargs:
            show_hidden (str): Return applications that have been hidden.
                default="no"
        """
        super(RetrieveSupportedApps, self).__init__(**kwargs)
        self.apps_collection = AppCollections.SupportedApps
        self.apps_per_agent_collection = AppCollections.SupportedAppsPerAgent

        self.fetch_apps = (
            FetchApps(
                view_name=self.view_name, count=self.count,
                offset=self.offset, sort=self.sort, sort_key=self.sort_key,
                show_hidden=self.show_hidden,
                apps_collections=self.apps_collection,
                apps_per_agent_collection=self.apps_per_agent_collection
            )
        )

class RetrieveAgentApps(RetrieveApps):
    """
        This class is used to query for applications.
    """
    def __init__(
        self, sort_key=DbCommonAppKeys.Name, show_hidden=CommonKeys.NO,
        **kwargs
    ):
        """
        Kwargs:
            show_hidden (str): Return applications that have been hidden.
                default="no"
        """
        super(RetrieveAgentApps, self).__init__(**kwargs)
        self.apps_collection = AppCollections.vFenseApps
        self.apps_per_agent_collection = AppCollections.vFenseAppsPerAgent

        self.fetch_apps = (
            FetchApps(
                view_name=self.view_name, count=self.count,
                offset=self.offset, sort=self.sort, sort_key=self.sort_key,
                show_hidden=self.show_hidden,
                apps_collections=self.apps_collection,
                apps_per_agent_collection=self.apps_per_agent_collection
            )
        )
