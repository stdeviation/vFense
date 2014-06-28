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

from vFense.errorz.status_codes import (
    GenericCodes, GenericFailureCodes
)
from vFense.errorz._constants import (
    ApiResultKeys
)

logging.config.fileConfig(VFENSE_LOGGING_CONFIG)
logger = logging.getLogger('rvapi')


class RetrieveApps(object):
    """
        This class is used to get agent data from within the Packages Page
    """
    def __init__(self, view_name=None,
                 count=DefaultQueryValues.COUNT,
                 offset=DefaultQueryValues.OFFSET,
                 sort=SortValues.ASC,
                 sort_key=DbCommonAppKeys.Name,
                 show_hidden=CommonKeys.NO,
                 apps_collection=AppCollections.UniqueApplications,
                 apps_per_agent_collection=AppCollections.AppsPerAgent):
        """
        """

        if view_name == DefaultViews.GLOBAL:
            view_name = None

        self.fetch_apps = (
            FetchApps(
                view_name, count, offset,
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


    def all(self):
        count, data = self.fetch_apps.all()
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
        This class is used to get agent data from within the Packages Page
    """
    def __init__(self, view_name=None,
                 count=DefaultQueryValues.COUNT,
                 offset=DefaultQueryValues.OFFSET,
                 sort=SortValues.ASC,
                 sort_key=DbCommonAppKeys.Name,
                 show_hidden=CommonKeys.NO):
        """
        """
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
        This class is used to get agent data from within the Packages Page
    """
    def __init__(self, view_name=None,
                 count=DefaultQueryValues.COUNT,
                 offset=DefaultQueryValues.OFFSET,
                 sort=SortValues.ASC,
                 sort_key=DbCommonAppKeys.Name,
                 show_hidden=CommonKeys.NO):
        """
        """
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
        This class is used to get agent data from within the Packages Page
    """
    def __init__(self, view_name=None,
                 count=DefaultQueryValues.COUNT,
                 offset=DefaultQueryValues.OFFSET,
                 sort=SortValues.ASC,
                 sort_key=DbCommonAppKeys.Name,
                 show_hidden=CommonKeys.NO):
        """
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
