from vFense.plugins.patching._db_model import (
    DbCommonAppKeys, AppCollections
)
from vFense.plugins.patching._constants import (
    CommonAppKeys, CommonSeverityKeys
)
from vFense.core._constants import CommonKeys
from vFense.plugins.patching.search._db_search import FetchApps
from vFense.search.base import RetrieveBase


class RetrieveAppsBase(RetrieveBase):
    """
        This class is used to query for applications.
    """
    def __init__(
        self, sort_key=DbCommonAppKeys.Name, show_hidden=CommonKeys.NO,
        apps_collection=AppCollections.UniqueApplications,
        apps_per_agent_collection=AppCollections.AppsPerAgent, **kwargs
    ):
        """
        Kwargs:
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
        super(RetrieveAppsBase, self).__init__(**kwargs)
        self.sort_key = sort_key
        self.show_hidden = show_hidden
        self.apps_collection = apps_collection
        self.apps_per_agent_collection = apps_per_agent_collection
        self.fetch_apps = (
            FetchApps(
                view_name=self.view_name, count=self.count,
                offset=self.offset, sort=self.sort,
                sort_key=self.sort_key, show_hidden=self.show_hidden,
                apps_collection=self.apps_collection,
                apps_per_agent_collection=self.apps_per_agent_collection
            )
        )

    def by_status(self, status):
        """Retrieve all applications by status.
            (installed, available, pending)
        Args:
            status (str): installed, available, pending

        Basic Usage:
            >>> from vFense.plugins.patching.search.search import RetrieveAppsBase
            >>> fetch = RetrieveAppsBase(count=1)
            >>> fetch.by_status('available')

        Results:
            Dictionary of the application data.
            >>>
                {
                    "count": 254,
                    "data": [
                        {
                            "vfense_severity": "Recommended",
                            "release_date": 1400212800,
                            "app_id": "d582e489691f78314b483ab12557933abc1194bb57041e787faf1328429c09f4",
                            "version": "2.14.1-0ubuntu3.2",
                            "hidden": "no",
                            "vulnerability_id": "",
                            "name": "apport"
                        }
                    ],
                    "message": "dataset retrieved",
                    "vfense_status_code": 1001,
                    "generic_status_code": 1001
                }
        """
        status = status.lower()
        if status in CommonAppKeys.ValidPackageStatuses:
            count, data = self.fetch_apps.by_status(status)
            return self._base(count, data)

        else:
            return self._set_results_invalid_filter_key(status)

    def by_severity(self, sev):
        """Retrieve all applications by severity.
            (critical, recommended, optional)
        Args:
            sev (str): critical, recommended, optional

        Basic Usage:
            >>> from vFense.plugins.patching.search.search import RetrieveAppsBase
            >>> fetch = RetrieveAppsBase(count=1, sort_key='vulnerability_id', sort='desc')
            >>> fetch.by_severity('Critical')

        Results:
            Dictionary of the application data.
            >>>
                {
                    "count": 165,
                    "data": [
                        {
                            "vfense_severity": "Critical",
                            "release_date": 1403755200,
                            "app_id": "b7b02f38f3176cb3d0614170d0b4ae8c888e81e999f0e7f5ee8dbc13bdd7a739",
                            "version": "1.4.16-1ubuntu2.1",
                            "hidden": "no",
                            "vulnerability_id": "USN-2258-1",
                            "name": "gnupg"
                        }
                    ],
                    "message": "dataset retrieved",
                    "vfense_status_code": 1001,
                    "generic_status_code": 1001
                }
        """
        sev = sev.capitalize()
        if sev in CommonSeverityKeys.ValidRvSeverities:
            count, data = self.fetch_apps.by_severity(sev)
            return self._base(count, data)

        else:
            return self._set_results_invalid_filter_key(sev)

    def by_status_and_sev(self, status, sev):
        """Retrieve all applications by status and severity.
            (installed, available, pending)
            (critical, recommended, optional)
        Args:
            status (str): installed, available, pending
            sev (str): critical, recommended, optional

        Basic Usage:
            >>> from vFense.plugins.patching.search.search import RetrieveAppsBase
            >>> fetch = RetrieveAppsBase(count=1)
            >>> fetch.by_status_and_sev('available', 'critical')

        Results:
            Dictionary of the application data.
            >>>
                {
                    "count": 25,
                    "data": [
                        {
                            "vfense_severity": "Critical",
                            "release_date": 1403755200,
                            "app_id": "b7b02f38f3176cb3d0614170d0b4ae8c888e81e999f0e7f5ee8dbc13bdd7a739",
                            "version": "1.4.16-1ubuntu2.1",
                            "hidden": "no",
                            "vulnerability_id": "USN-2258-1",
                            "name": "gnupg"
                        }
                    ],
                    "message": "dataset retrieved",
                    "vfense_status_code": 1001,
                    "generic_status_code": 1001
                }
        """
        status = status.lower()
        sev = sev.capitalize()
        if status in CommonAppKeys.ValidPackageStatuses:
            if sev in CommonSeverityKeys.ValidRvSeverities:
                count, data = self.fetch_apps.by_status_and_sev(status, sev)
                return self._base(count, data)

            else:
                return self._set_results_invalid_filter_key(sev)

        else:
            return self._set_results_invalid_filter_key(status)

    def all(self):
        """Retrieve all applications.

        Basic Usage:
            >>> from vFense.plugins.patching.search.search import RetrieveAppsBase
            >>> fetch = RetrieveAppsBase(count=1)
            >>> fetch.all()

        Results:
            Dictionary of the application data.
            >>>
                {
                    "count": 25,
                    "data": [
                        {
                            "vfense_severity": "Critical",
                            "release_date": 1403755200,
                            "app_id": "b7b02f38f3176cb3d0614170d0b4ae8c888e81e999f0e7f5ee8dbc13bdd7a739",
                            "version": "1.4.16-1ubuntu2.1",
                            "hidden": "no",
                            "vulnerability_id": "USN-2258-1",
                            "name": "gnupg"
                        }
                    ],
                    "message": "dataset retrieved",
                    "vfense_status_code": 1001,
                    "generic_status_code": 1001
                }
        """
        count, data = self.fetch_apps.all()
        return self._base(count, data)

    def by_name(self, name):
        """Retrieve all applications by regular expression on the name
            of the application.

        Args:
            name (str): Regular expression of the application
                you are looking for.

        Basic Usage:
            >>> from vFense.plugins.patching.search.search import RetrieveAppsBase
            >>> fetch = RetrieveAppsBase(count=1)
            >>> fetch.by_name("^\w+-\w+ssl$")

        Results:
            Dictionary of the application data.
            >>>
                {
                    "count": 1,
                    "data": [
                        {
                            "vfense_severity": "Recommended",
                            "release_date": 0,
                            "app_id": "8174d8162ba128746ce1bb6e7d56cdd079729ecb91722fb26ca5d9b6c49689bc",
                            "version": "0.13-2ubuntu6",
                            "hidden": "no",
                            "vulnerability_id": "",
                            "name": "python-openssl"
                        }
                    ],
                    "message": "dataset retrieved",
                    "vfense_status_code": 1001,
                    "generic_status_code": 1001
                }
        """
        count, data = self.fetch_apps.by_name(name)
        return self._base(count, data)

    def by_status_and_name(self, status, name):
        """Retrieve all applications by regular expression on the name
            of the application.

        Args:
            status (str): installed, available, pending
            name (str): Regular expression of the application
                you are looking for.

        Basic Usage:
            >>> from vFense.plugins.patching.search.search import RetrieveAppsBase
            >>> fetch = RetrieveAppsBase(count=1)
            >>> fetch.by_status_and_name("installed", "^\w+-\w+ssl$")

        Results:
            Dictionary of the application data.
            >>>
                {
                    "count": 1,
                    "data": [
                        {
                            "vfense_severity": "Recommended",
                            "release_date": 0,
                            "app_id": "8174d8162ba128746ce1bb6e7d56cdd079729ecb91722fb26ca5d9b6c49689bc",
                            "version": "0.13-2ubuntu6",
                            "hidden": "no",
                            "vulnerability_id": "",
                            "name": "python-openssl"
                        }
                    ],
                    "message": "dataset retrieved",
                    "vfense_status_code": 1001,
                    "generic_status_code": 1001
                }
        """
        status = status.lower()
        if status in CommonAppKeys.ValidPackageStatuses:
            count, data = self.fetch_apps.by_status_and_name(status, name)
            return self._base(count, data)

        else:
            return self._set_results_invalid_filter_key(status)

    def by_status_and_name_and_vuln(self, status, name):
        """Retrieve all applications by the status, regular expression
            on the name of the application, and if a vulnerability exist.

        Args:
            status (str): installed, available, pending
            name (str): Regular expression of the application
                you are looking for.

        Basic Usage:
            >>> from vFense.plugins.patching.search.search import RetrieveAppsBase
            >>> fetch = RetrieveAppsBase(count=1)
            >>> fetch.by_status_and_name_and_vuln("available", "json")

        Results:
            Dictionary of the application data.
            >>>
                {
                    "count": 1,
                    "data": [
                        {
                            "vfense_severity": "Critical",
                            "release_date": 1402545600,
                            "app_id": "bee662f542aaa86ce6889d570e2c404c93dfb7514cdbcd9a878f13a8db790073",
                            "version": "0.11-3ubuntu1.2",
                            "hidden": "no",
                            "vulnerability_id": "USN-2245-1",
                            "name": "libjson0"
                        }
                    ],
                    "message": "dataset retrieved",
                    "vfense_status_code": 1001,
                    "generic_status_code": 1001
                }
        """
        status = status.lower()
        if status in CommonAppKeys.ValidPackageStatuses:
            count, data = (
                self.fetch_apps.by_status_and_name_and_vuln(status, name)
            )
            return self._base(count, data)

        else:
            return self._set_results_invalid_filter_key(status)

    def by_status_and_name_and_sev(self, status, name, sev):
        """Retrieve all applications by the status, regular expression
            on the name of the application, and the severity.

        Args:
            status (str): installed, available, pending
            name (str): Regular expression of the application
                you are looking for.
            sev (str): critical ,recommended, optional

        Basic Usage:
            >>> from vFense.plugins.patching.search.search import RetrieveAppsBase
            >>> fetch = RetrieveAppsBase(count=1)
            >>> fetch.by_status_and_name_and_sev(
                    "installed", "^\w+-\w+ssl$", "recommended"
                )

        Results:
            Dictionary of the application data.
            >>>
                {
                    "count": 1,
                    "data": [
                        {
                            "vfense_severity": "Recommended",
                            "release_date": 0,
                            "app_id": "8174d8162ba128746ce1bb6e7d56cdd079729ecb91722fb26ca5d9b6c49689bc",
                            "version": "0.13-2ubuntu6",
                            "hidden": "no",
                            "vulnerability_id": "",
                            "name": "python-openssl"
                        }
                    ],
                    "message": "dataset retrieved",
                    "vfense_status_code": 1001,
                    "generic_status_code": 1001
                }
        """
        status = status.lower()
        sev = sev.capitalize()
        if status in CommonAppKeys.ValidPackageStatuses:
            if sev in CommonSeverityKeys.ValidRvSeverities:
                count, data = (
                    self.fetch_apps.by_status_and_name_and_sev(
                        status, name, sev
                    )
                )
                return self._base(count, data)

            else:
                return self._set_results_invalid_filter_key(sev)

        else:
            return self._set_results_invalid_filter_key(status)

    def by_status_and_name_and_sev_and_vuln(self, status, name, sev):
        """Retrieve all applications by the status, regular expression
            on the name of the application, and the severity and if
            vulnerability exist.

        Args:
            status (str): installed, available, pending
            name (str): Regular expression of the application
                you are looking for.
            sev (str): critical ,recommended, optional

        Basic Usage:
            >>> from vFense.plugins.patching.search.search import RetrieveAppsBase
            >>> fetch = RetrieveAppsBase(count=1)
            >>> fetch.by_status_and_name_and_sev_and_vuln(
                    "available", "json", "critical"
                )

        Results:
            Dictionary of the application data.
            >>>
                {
                    "count": 1,
                    "data": [
                        {
                            "vfense_severity": "Critical",
                            "release_date": 1402545600,
                            "app_id": "bee662f542aaa86ce6889d570e2c404c93dfb7514cdbcd9a878f13a8db790073",
                            "version": "0.11-3ubuntu1.2",
                            "hidden": "no",
                            "vulnerability_id": "USN-2245-1",
                            "name": "libjson0"
                        }
                    ],
                    "message": "dataset retrieved",
                    "vfense_status_code": 1001,
                    "generic_status_code": 1001
                }
        """
        status = status.lower()
        sev = sev.capitalize()
        if status in CommonAppKeys.ValidPackageStatuses:
            if sev in CommonSeverityKeys.ValidRvSeverities:
                count, data = (
                    self.fetch_apps.by_status_and_name_and_sev_and_vuln(
                        status, name, sev
                    )
                )
                return self._base(count, data)

            else:
                return self._set_results_invalid_filter_key(sev)

        else:
            return self._set_results_invalid_filter_key(status)

    def by_sev_and_name(self, sev, name):
        """Retrieve all applications by the severity, regular expression
            on the name of the application.

        Args:
            sev (str): critical ,recommended, optional
            name (str): Regular expression of the application
                you are looking for.

        Basic Usage:
            >>> from vFense.plugins.patching.search.search import RetrieveAppsBase
            >>> fetch = RetrieveAppsBase(count=1)
            >>> fetch.by_sev_and_name("critical", "json")

        Results:
            Dictionary of the application data.
            >>>
                {
                    "count": 1,
                    "data": [
                        {
                            "vfense_severity": "Critical",
                            "release_date": 1402545600,
                            "app_id": "bee662f542aaa86ce6889d570e2c404c93dfb7514cdbcd9a878f13a8db790073",
                            "version": "0.11-3ubuntu1.2",
                            "hidden": "no",
                            "vulnerability_id": "USN-2245-1",
                            "name": "libjson0"
                        }
                    ],
                    "message": "dataset retrieved",
                    "vfense_status_code": 1001,
                    "generic_status_code": 1001
                }
        """
        sev = sev.capitalize()
        if sev in CommonSeverityKeys.ValidRvSeverities:
            count, data = (
                self.fetch_apps.by_sev_and_name(sev, name)
            )
            return self._base(count, data)

        else:
            return self._set_results_invalid_filter_key(sev)

    def by_status_and_vuln(self, status):
        """Retrieve all applications by the status and if vulnerability exist.

        Args:
            status (str): installed, available, pending

        Basic Usage:
            >>> from vFense.plugins.patching.search.search import RetrieveAppsBase
            >>> fetch = RetrieveAppsBase(count=1)
            >>> fetch.by_status_and_vuln("available")

        Results:
            Dictionary of the application data.
            >>>
                {
                    "count": 1,
                    "data": [
                        {
                            "vfense_severity": "Critical",
                            "release_date": 1402545600,
                            "app_id": "bee662f542aaa86ce6889d570e2c404c93dfb7514cdbcd9a878f13a8db790073",
                            "version": "0.11-3ubuntu1.2",
                            "hidden": "no",
                            "vulnerability_id": "USN-2245-1",
                            "name": "libjson0"
                        }
                    ],
                    "message": "dataset retrieved",
                    "vfense_status_code": 1001,
                    "generic_status_code": 1001
                }
        """
        status = status.lower()
        if status in CommonAppKeys.ValidPackageStatuses:
            count, data = (
                self.fetch_apps.by_status_and_vuln(status)
            )
            return self._base(count, data)

        else:
            return self._set_results_invalid_filter_key(status)

    def by_name_and_vuln(self, name):
        """Retrieve all applications by regular expression
            on the name of the application and if vulnerability exist.

        Args:
            name (str): Regular expression of the application
                you are looking for.

        Basic Usage:
            >>> from vFense.plugins.patching.search.search import RetrieveAppsBase
            >>> fetch = RetrieveAppsBase(count=1)
            >>> fetch.by_name_and_vuln("json")

        Results:
            Dictionary of the application data.
            >>>
                {
                    "count": 1,
                    "data": [
                        {
                            "vfense_severity": "Critical",
                            "release_date": 1402545600,
                            "app_id": "bee662f542aaa86ce6889d570e2c404c93dfb7514cdbcd9a878f13a8db790073",
                            "version": "0.11-3ubuntu1.2",
                            "hidden": "no",
                            "vulnerability_id": "USN-2245-1",
                            "name": "libjson0"
                        }
                    ],
                    "message": "dataset retrieved",
                    "vfense_status_code": 1001,
                    "generic_status_code": 1001
                }
        """
        count, data = (
            self.fetch_apps.by_name_and_vuln(name)
        )
        return self._base(count, data)
