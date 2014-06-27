import logging
import logging.config
from vFense import VFENSE_LOGGING_CONFIG

from vFense.db.client import db_create_close, r
from vFense.plugins.patching._db_model import *
from vFense.core._constants import CommonKeys
from vFense.plugins.patching._constants import CommonAppKeys, CommonSeverityKeys
from vFense.core.agent._db_model import *
from vFense.errorz.error_messages import GenericResults, PackageResults

logging.config.fileConfig(VFENSE_LOGGING_CONFIG)
logger = logging.getLogger('rvapi')


class RetrieveApps(object):
    """
        This class is used to get agent data from within the Packages Page
    """
    def __init__(self, username, view_name,
                 uri=None, method=None, count=30,
                 offset=0, sort='asc', sort_key=AppsKey.Name,
                 show_hidden=CommonKeys.NO):
        """
        """
        self.count = count
        self.offset = offset
        self.view_name = view_name
        self.username = username
        self.uri = uri
        self.method = method

        if show_hidden in CommonAppKeys.ValidHiddenVals:
            self.show_hidden = show_hidden
        else:
            self.show_hidden = CommonKeys.NO

        if sort_key in self.pluck_list:
            self.sort_key = sort_key
        else:
            self.sort_key = self.CurrentAppsKey.Name

        if sort == 'asc':
            self.sort = r.asc
        else:
            self.sort = r.desc

        if self.view_name == DefaultViews.GLOBAL:
            self.view_name = None

        self.fetch_apps = (
            FetchApps(
                self.view_name, self.count, self.offset,
                self.sort, self.sort_key, self.show_hidden
            )
        )

    def by_status(self, status):
        if pkg_status in CommonAppKeys.ValidPackageStatuses:
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

    def filter_by_status_and_sev(self, status, sev):
        count = 0
        data = []
        generic_status_code = GenericCodes.InvalidFilterKey
        vfense_status_code = GenericCodes.InvalidFilterKey
        msg = 'Invalid severity {0}'.format(sev)
        if pkg_status in CommonAppKeys.ValidPackageStatuses:
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
        if pkg_status in CommonAppKeys.ValidPackageStatuses:
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
        if pkg_status in CommonAppKeys.ValidPackageStatuses:
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
    def __init__(self, username, view_name,
                 uri=None, method=None, count=30,
                 offset=0, sort='asc', sort_key=CustomAppsKey.Name,
                 show_hidden=CommonKeys.NO):

        self.count = count
        self.offset = offset
        self.view_name = view_name
        self.username = username
        self.uri = uri
        self.method = method

        self.set_global_properties(
            AppCollections.CustomApps, CustomAppsIndexes,
            AppCollections.CustomAppsPerAgent,
            CustomAppsKey, CustomAppsPerAgentKey,
            CustomAppsPerAgentIndexes
        )

        if show_hidden in CommonAppKeys.ValidHiddenVals:
            self.show_hidden = show_hidden
        else:
            self.show_hidden = CommonKeys.NO

        if sort_key in self.pluck_list:
            self.sort_key = sort_key
        else:
            self.sort_key = self.CurrentAppsKey.Name

        if sort == 'asc':
            self.sort = r.asc
        else:
            self.sort = r.desc

class RetrieveSupportedApps(RetrieveApps):
    """
        This class is used to get agent data from within the Packages Page
    """
    def __init__(self, username, view_name,
                 uri=None, method=None, count=30,
                 offset=0, sort='asc',
                 sort_key=SupportedAppsKey.Name,
                 show_hidden=CommonKeys.NO):

        self.count = count
        self.offset = offset
        self.view_name = view_name
        self.username = username
        self.uri = uri
        self.method = method

        self.set_global_properties(
            AppCollections.SupportedApps, SupportedAppsIndexes,
            AppCollections.SupportedAppsPerAgent,
            SupportedAppsKey, SupportedAppsPerAgentKey,
            SupportedAppsPerAgentIndexes
        )

        if show_hidden in CommonAppKeys.ValidHiddenVals:
            self.show_hidden = show_hidden
        else:
            self.show_hidden = CommonKeys.NO

        if sort_key in self.pluck_list:
            self.sort_key = sort_key
        else:
            self.sort_key = self.CurrentAppsKey.Name

        if sort == 'asc':
            self.sort = r.asc
        else:
            self.sort = r.desc

class RetrieveAgentApps(RetrieveApps):
    """
        This class is used to get agent data from within the Packages Page
    """
    def __init__(self, username, view_name,
                 uri=None, method=None, count=30,
                 offset=0, sort='asc',
                 sort_key=AgentAppsKey.Name,
                 show_hidden=CommonKeys.NO):

        self.count = count
        self.offset = offset
        self.view_name = view_name
        self.username = username
        self.uri = uri
        self.method = method

        self.set_global_properties(
            AppCollections.vFenseApps, AgentAppsIndexes,
            AppCollections.vFenseAppsPerAgent,
            AgentAppsKey, AgentAppsPerAgentKey,
            AgentAppsPerAgentIndexes
        )

        if show_hidden in CommonAppKeys.ValidHiddenVals:
            self.show_hidden = show_hidden
        else:
            self.show_hidden = CommonKeys.NO

        if sort_key in self.pluck_list:
            self.sort_key = sort_key
        else:
            self.sort_key = self.CurrentAppsKey.Name

        if sort == 'asc':
            self.sort = r.asc
        else:
            self.sort = r.desc



