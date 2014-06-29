import logging
import logging.config
from vFense import VFENSE_LOGGING_CONFIG
from vFense.plugins.patching.search._db_search_by_agentid import (
    FetchAppsByAgentId
)

from vFense.plugins.patching._db_model import (
    AppCollections, DbCommonAppKeys
)
from vFense.plugins.patching._constants import (
    CommonAppKeys, CommonSeverityKeys
)
from vFense.core._constants import (
    SortValues, DefaultQueryValues, CommonKeys
)

from vFense.errorz.status_codes import (
    GenericCodes, GenericFailureCodes
)
from vFense.errorz._constants import (
    ApiResultKeys
)


logging.config.fileConfig(VFENSE_LOGGING_CONFIG)
logger = logging.getLogger('rvapi')

class RetrieveAppsByAgentId(object):
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

        self.fetch_apps = (
            FetchAppsByAgentId(
                self.agent_id, count, offset,
                sort, sort_key, show_hidden
            )
        )

    def by_status(self, status):
        """Retrieve all applications by status.
            (installed, available, pending)
        Args:
            status (str): installed, available, pending

        Basic Usage:
            >>> from vFense.plugins.patching.search.search_by_agentid import RetrieveAppsByAgentId
            >>> agent_id = 'f91f3403-6a98-4206-b497-d73adc8cb7db'
            >>> fetch = RetrieveAppsByAgentId(agent_id, count=1)
            >>> fetch.by_status('available')

        Results:
            Dictionary of the application data.
            >>>
                {
                    "count": 254,
                    "data": [
                        {
                            "rv_severity": "Recommended",
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
            generic_status_code = GenericCodes.InformationRetrieved

            if count == 0:
                vfense_status_code = GenericFailureCodes.DataIsEmpty
                msg = 'dataset is empty'

            else:
                vfense_status_code = GenericCodes.InformationRetrieved
                msg = 'dataset retrieved'
        else:
            count = 0
            data = []
            generic_status_code = GenericCodes.InvalidFilterKey
            vfense_status_code = GenericCodes.InvalidFilterKey
            msg = 'Invalid status {0}'.format(status)

        results = (
            self._set_results(
                generic_status_code, vfense_status_code,
                msg, count, data
            )
        )
        return results

    def by_status_and_sev(self, status, sev):
        """Retrieve all applications by status and severity.
            (installed, available, pending)
            (critical, recommended, optional)
        Args:
            status (str): installed, available, pending
            sev (str): critical, recommended, optional

        Basic Usage:
            >>> from vFense.plugins.patching.search.search import RetrieveAppsByAgentId
            >>> agent_id = 'f91f3403-6a98-4206-b497-d73adc8cb7db'
            >>> fetch = RetrieveAppsByAgentId(agent_id, count=1)
            >>> fetch.by_status_and_sev('available', 'critical')

        Results:
            Dictionary of the application data.
            >>>
                {
                    "count": 25,
                    "data": [
                        {
                            "rv_severity": "Critical",
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
        count = 0
        data = []
        generic_status_code = GenericCodes.InvalidFilterKey
        vfense_status_code = GenericCodes.InvalidFilterKey
        msg = 'Invalid severity {0}'.format(sev)
        if status in CommonAppKeys.ValidPackageStatuses:
            if sev in CommonSeverityKeys.ValidRvSeverities:
                count, data = self.fetch_apps.by_status_and_sev(status, sev)
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

    def by_severity(self, sev):
        """Retrieve all applications by severity.
            (critical, recommended, optional)
        Args:
            sev (str): critical, recommended, optional

        Basic Usage:
            >>> from vFense.plugins.patching.search.search import RetrieveAppsByAgentId
            >>> agent_id = 'f91f3403-6a98-4206-b497-d73adc8cb7db'
            >>> fetch = RetrieveAppsByAgentId(
                    agent_id, count=1,
                    sort_key='vulnerability_id', sort='desc'
                )
            >>> fetch.by_severity('Critical')

        Results:
            Dictionary of the application data.
            >>>
                {
                    "count": 165,
                    "data": [
                        {
                            "rv_severity": "Critical",
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
            generic_status_code = GenericCodes.InformationRetrieved

            if count == 0:
                vfense_status_code = GenericFailureCodes.DataIsEmpty
                msg = 'dataset is empty'

            else:
                vfense_status_code = GenericCodes.InformationRetrieved
                msg = 'dataset retrieved'
        else:
            count = 0
            data = []
            generic_status_code = GenericCodes.InvalidFilterKey
            vfense_status_code = GenericCodes.InvalidFilterKey
            msg = 'Invalid severity {0}'.format(sev)

        results = (
            self._set_results(
                generic_status_code, vfense_status_code,
                msg, count, data
            )
        )
        return results

    def by_name(self, name):
        """Retrieve all applications by regular expression on the name
            of the application.

        Args:
            name (str): Regular expression of the application
                you are looking for.

        Basic Usage:
            >>> from vFense.plugins.patching.search.search import RetrieveAppsByAgentId
            >>> agent_id = 'f91f3403-6a98-4206-b497-d73adc8cb7db'
            >>> fetch = RetrieveAppsByAgentId(agent_id, count=1)
            >>> fetch.by_name("^\w+-\w+ssl$")

        Results:
            Dictionary of the application data.
            >>>
                {
                    "count": 1,
                    "data": [
                        {
                            "rv_severity": "Recommended",
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

    def by_status_and_name(self, status, name):
        """Retrieve all applications by regular expression on the name
            of the application.

        Args:
            status (str): installed, available, pending
            name (str): Regular expression of the application
                you are looking for.

        Basic Usage:
            >>> from vFense.plugins.patching.search.search import RetrieveAppsByAgentId
            >>> agent_id = 'f91f3403-6a98-4206-b497-d73adc8cb7db'
            >>> fetch = RetrieveAppsByAgentId(agent_id, count=1)
            >>> fetch.by_status_and_name("installed", "^\w+-\w+ssl$")

        Results:
            Dictionary of the application data.
            >>>
                {
                    "count": 1,
                    "data": [
                        {
                            "rv_severity": "Recommended",
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
            generic_status_code = GenericCodes.InformationRetrieved

            if count == 0:
                vfense_status_code = GenericFailureCodes.DataIsEmpty
                msg = 'dataset is empty'

            else:
                vfense_status_code = GenericCodes.InformationRetrieved
                msg = 'dataset retrieved'
        else:
            count = 0
            data = []
            generic_status_code = GenericCodes.InvalidFilterKey
            vfense_status_code = GenericCodes.InvalidFilterKey
            msg = 'Invalid status {0}'.format(status)

        results = (
            self._set_results(
                generic_status_code, vfense_status_code,
                msg, count, data
            )
        )
        return results

    def by_status_and_name_and_sev(self, status, name, sev):
        """Retrieve all applications by the status, regular expression
            on the name of the application, and the severity.

        Args:
            status (str): installed, available, pending
            name (str): Regular expression of the application
                you are looking for.
            sev (str): critical ,recommended, optional

        Basic Usage:
            >>> from vFense.plugins.patching.search.search import RetrieveAppsByAgentId
            >>> agent_id = 'f91f3403-6a98-4206-b497-d73adc8cb7db'
            >>> fetch = RetrieveAppsByAgentId(agent_id, count=1)
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
                            "rv_severity": "Recommended",
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
        count = 0
        data = []
        generic_status_code = GenericCodes.InvalidFilterKey
        vfense_status_code = GenericCodes.InvalidFilterKey
        msg = 'Invalid status {0}'.format(status)
        if status in CommonAppKeys.ValidPackageStatuses:
            if sev in CommonSeverityKeys.ValidRvSeverities:
                count, data = (
                    self.fetch_apps.by_status_and_name_and_sev(
                        status, name, sev
                    )
                )
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

    def by_status_and_name_vuln(self, status, name):
        """Retrieve all applications by the status, regular expression
            on the name of the application, and if a vulnerability exist.

        Args:
            status (str): installed, available, pending
            name (str): Regular expression of the application
                you are looking for.

        Basic Usage:
            >>> from vFense.plugins.patching.search.search import RetrieveAppsByAgentId
            >>> agent_id = 'f91f3403-6a98-4206-b497-d73adc8cb7db'
            >>> fetch = RetrieveAppsByAgentId(agent_id, count=1)
            >>> fetch.by_status_and_name_and_vuln("available", "json")

        Results:
            Dictionary of the application data.
            >>>
                {
                    "count": 1,
                    "data": [
                        {
                            "rv_severity": "Critical",
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
        count = 0
        data = []
        generic_status_code = GenericCodes.InvalidFilterKey
        vfense_status_code = GenericCodes.InvalidFilterKey
        msg = 'Invalid status {0}'.format(status)
        if status in CommonAppKeys.ValidPackageStatuses:
            count, data = (
                self.fetch_apps.by_status_and_name_and_vuln(status, name)
            )
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
            >>> from vFense.plugins.patching.search.search import RetrieveAppsByAgentId
            >>> agent_id = 'f91f3403-6a98-4206-b497-d73adc8cb7db'
            >>> fetch = RetrieveAppsByAgentId(agent_id, count=1)
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
                            "rv_severity": "Critical",
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
        count = 0
        data = []
        generic_status_code = GenericCodes.InvalidFilterKey
        vfense_status_code = GenericCodes.InvalidFilterKey
        msg = 'Invalid status {0}'.format(status)
        if status in CommonAppKeys.ValidPackageStatuses:
            if sev in CommonSeverityKeys.ValidRvSeverities:
                count, data = (
                    self.fetch_apps.by_status_and_name_and_sev_and_vuln(
                        status, name, sev
                    )
                )
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


    def by_sev_and_name(self, sev, name):
        """Retrieve all applications by the severity, regular expression
            on the name of the application.

        Args:
            sev (str): critical ,recommended, optional
            name (str): Regular expression of the application
                you are looking for.

        Basic Usage:
            >>> from vFense.plugins.patching.search.search import RetrieveAppsByAgentId
            >>> agent_id = 'f91f3403-6a98-4206-b497-d73adc8cb7db'
            >>> fetch = RetrieveAppsByAgentId(agent_id, count=1)
            >>> fetch.by_sev_and_name("critical", "json")

        Results:
            Dictionary of the application data.
            >>>
                {
                    "count": 1,
                    "data": [
                        {
                            "rv_severity": "Critical",
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
        count = 0
        data = []
        generic_status_code = GenericCodes.InvalidFilterKey
        vfense_status_code = GenericCodes.InvalidFilterKey
        msg = 'Invalid severity {0}'.format(sev)
        if sev in CommonSeverityKeys.ValidRvSeverities:
            count, data = (
                self.fetch_apps.by_sev_and_name(sev, name)
            )
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

    def by_status_and_vuln(self, status):
        """Retrieve all applications by the status and if vulnerability exist.

        Args:
            status (str): installed, available, pending

        Basic Usage:
            >>> from vFense.plugins.patching.search.search import RetrieveAppsByAgentId
            >>> agent_id = 'f91f3403-6a98-4206-b497-d73adc8cb7db"
            >>> fetch = RetrieveAppsByAgentId(agent_id, count=1)
            >>> fetch.by_status_and_vuln("available")

        Results:
            Dictionary of the application data.
            >>>
                {
                    "count": 1,
                    "data": [
                        {
                            "rv_severity": "Critical",
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
            count, data = self.fetch_apps.by_status_and_vuln(status)
            generic_status_code = GenericCodes.InformationRetrieved

            if count == 0:
                vfense_status_code = GenericFailureCodes.DataIsEmpty
                msg = 'dataset is empty'

            else:
                vfense_status_code = GenericCodes.InformationRetrieved
                msg = 'dataset retrieved'
        else:
            count = 0
            data = []
            generic_status_code = GenericCodes.InvalidFilterKey
            vfense_status_code = GenericCodes.InvalidFilterKey
            msg = 'Invalid status {0}'.format(status)

        results = (
            self._set_results(
                generic_status_code, vfense_status_code,
                msg, count, data
            )
        )
        return results

    def by_name_and_vuln(self, name):
        """Retrieve all applications by regular expression
            on the name of the application and if vulnerability exist.

        Args:
            name (str): Regular expression of the application
                you are looking for.

        Basic Usage:
            >>> from vFense.plugins.patching.search.search import RetrieveAppsByAgentId
            >>> agent_id = 'f91f3403-6a98-4206-b497-d73adc8cb7db'
            >>> fetch = RetrieveAppsByAgentId(agent_id, count=1)
            >>> fetch.by_name_and_vuln("json")

        Results:
            Dictionary of the application data.
            >>>
                {
                    "count": 1,
                    "data": [
                        {
                            "rv_severity": "Critical",
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
