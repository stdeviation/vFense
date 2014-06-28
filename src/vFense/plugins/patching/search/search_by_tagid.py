import logging
import logging.config
from vFense import VFENSE_LOGGING_CONFIG

from vFense.plugins.patching.search._db_search_by_tagid import (
    FetchAppsByTagId
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

class RetrieveAppsByTagId(object):
    """
        This class is used to get tag data from within the Packages Page
    """
    def __init__(self, tag_id,
                 count=DefaultQueryValues.COUNT,
                 offset=DefaultQueryValues.OFFSET,
                 sort=SortValues.ASC,
                 sort_key=DbCommonAppKeys.Name,
                 show_hidden=CommonKeys.NO):
        """
        """
        self.tag_id = tag_id

        self.fetch_apps = (
            FetchAppsByTagId(
                self.tag_id, count, offset,
                sort, sort_key, show_hidden
            )
        )

    def by_status(self, status):
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

    def by_status_and_name(self, status, name):
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

    def by_name(self, name):
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

    def by_status_and_name_and_sev(self, status, name, sev):
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

    def by_status_and_name_and_sev_and_vuln(self, status, name, sev):
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


    def by_severity(self, sev):
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

    def by_sev_and_name(self, sev, name):
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

    def by_status_and_sev(self, status, sev):
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

    def by_status_and_vuln(self, status):
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


class RetrieveCustomAppsByTagId(RetrieveAppsByTagId):
    """
        This class is used to get tag data from within the Packages Page
    """
    def __init__(self, tag_id,
                 count=DefaultQueryValues.COUNT,
                 offset=DefaultQueryValues.OFFSET,
                 sort=SortValues.ASC,
                 sort_key=DbCommonAppKeys.Name,
                 show_hidden=CommonKeys.NO):
        """
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
        This class is used to get tag data from within the Packages Page
    """
    def __init__(self, tag_id,
                 count=DefaultQueryValues.COUNT,
                 offset=DefaultQueryValues.OFFSET,
                 sort=SortValues.ASC,
                 sort_key=DbCommonAppKeys.Name,
                 show_hidden=CommonKeys.NO):
        """
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
        This class is used to get tag data from within the Packages Page
    """
    def __init__(self, tag_id,
                 count=DefaultQueryValues.COUNT,
                 offset=DefaultQueryValues.OFFSET,
                 sort=SortValues.ASC,
                 sort_key=DbCommonAppKeys.Name,
                 show_hidden=CommonKeys.NO):
        """
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
