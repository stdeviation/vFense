import logging
import logging.config
from vFense import VFENSE_LOGGING_CONFIG
from vFense.db.client import db_create_close, r
from vFense.plugins.patching._db_model import *
from vFense.plugins.patching.search._db_search_by_agentid import (
    FetchAppsByAgentId
)
from vFense.core._constants import CommonKeys
from vFense.plugins.patching._constants import CommonSeverityKeys, CommonAppKeys
from vFense.core.agent._db_model import *
from vFense.core.agent.agents import get_agent_info
from vFense.errorz.error_messages import GenericResults, PackageResults

logging.config.fileConfig(VFENSE_LOGGING_CONFIG)
logger = logging.getLogger('rvapi')

class RetrieveAppsByAgentId(object):
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
        """
        self.agent_id = agent_id

        self.fetch_apps = (
            FetchAppsByAgentId(
                self.agent_id, count, offset,
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

    def by_sev_and_name(self, sev, name):
        count = 0
        data = []
        generic_status_code = GenericCodes.InvalidFilterKey
        vfense_status_code = GenericCodes.InvalidFilterKey
        msg = 'Invalid status {0}'.format(status)
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
    def __init__(self, username, view_name,
                 agent_id, uri=None, method=None,
                 count=30, offset=0, sort='asc',
                 sort_key=CustomAppsKey.Name,
                 show_hidden=CommonKeys.NO):
        """
        """
        self.count = count
        self.uri = uri
        self.method = method
        self.offset = offset
        self.count = count
        self.sort = sort
        self.agent_id = agent_id
        self.username = username
        self.view_name = view_name
        self.CurrentAppsCollection = AppCollections.CustomApps
        self.CurrentAppsIndexes = CustomAppsIndexes
        self.CurrentAppsPerAgentCollection = AppCollections.CustomAppsPerAgent
        DbCommonAppKeys = CustomAppsKey
        DbCommonAppPerAgentKeys = CustomAppsPerAgentKey
        self.CurrentAppsPerAgentIndexes = CustomAppsPerAgentIndexes

        self.pluck_list = (
            [
                DbCommonAppKeys.AppId,
                DbCommonAppKeys.Version,
                DbCommonAppKeys.Name,
                DbCommonAppKeys.Hidden,
                DbCommonAppPerAgentKeys.Update,
                DbCommonAppKeys.ReleaseDate,
                DbCommonAppKeys.RebootRequired,
                DbCommonAppKeys.RvSeverity,
                DbCommonAppKeys.FilesDownloadStatus,
                DbCommonAppPerAgentKeys.Dependencies,
                DbCommonAppPerAgentKeys.InstallDate,
                DbCommonAppPerAgentKeys.Status,
                DbCommonAppPerAgentKeys.Update,
            ]
        )

        self.map_hash = (
            {
                DbCommonAppKeys.AppId: r.row[DbCommonAppKeys.AppId],
                DbCommonAppKeys.Version: r.row[DbCommonAppKeys.Version],
                DbCommonAppKeys.Name: r.row[DbCommonAppKeys.Name],
                DbCommonAppKeys.Hidden: r.row[DbCommonAppKeys.Hidden],
                DbCommonAppPerAgentKeys.Update: r.row[DbCommonAppPerAgentKeys.Update],
                DbCommonAppKeys.ReleaseDate: r.row[DbCommonAppKeys.ReleaseDate].to_epoch_time(),
                DbCommonAppKeys.RvSeverity: r.row[DbCommonAppKeys.RvSeverity],
                DbCommonAppKeys.RebootRequired: r.row[DbCommonAppKeys.RebootRequired],
                DbCommonAppKeys.FilesDownloadStatus: r.row[DbCommonAppKeys.FilesDownloadStatus],
                DbCommonAppPerAgentKeys.Dependencies: r.row[DbCommonAppPerAgentKeys.Dependencies],
                DbCommonAppPerAgentKeys.InstallDate: r.row[DbCommonAppPerAgentKeys.InstallDate].to_epoch_time(),
                DbCommonAppPerAgentKeys.Status: r.row[DbCommonAppPerAgentKeys.Status],
                DbCommonAppPerAgentKeys.Update: r.row[DbCommonAppPerAgentKeys.Update],
            }
        )

        if show_hidden in CommonAppKeys.ValidHiddenVals:
            self.show_hidden = show_hidden
        else:
            self.show_hidden = CommonKeys.NO

        if sort_key in self.pluck_list:
            self.sort_key = sort_key
        else:
            self.sort_key = DbCommonAppKeys.Name

        if sort == 'asc':
            self.sort = r.asc
        else:
            self.sort = r.desc


class RetrieveSupportedAppsByAgentId(RetrieveAppsByAgentId):
    """
        This class is used to get agent data from within the Packages Page
    """
    def __init__(self, username, view_name,
                 agent_id, uri=None, method=None,
                 count=30, offset=0, sort='asc',
                 sort_key=SupportedAppsKey.Name,
                 show_hidden=CommonKeys.NO):
        """
        """
        self.count = count
        self.uri = uri
        self.method = method
        self.offset = offset
        self.count = count
        self.sort = sort
        self.agent_id = agent_id
        self.username = username
        self.view_name = view_name
        self.CurrentAppsCollection = AppCollections.SupportedApps
        self.CurrentAppsIndexes = SupportedAppsIndexes
        self.CurrentAppsPerAgentCollection = AppCollections.SupportedAppsPerAgent
        DbCommonAppKeys = SupportedAppsKey
        DbCommonAppPerAgentKeys = SupportedAppsPerAgentKey
        self.CurrentAppsPerAgentIndexes = SupportedAppsPerAgentIndexes

        self.pluck_list = (
            [
                DbCommonAppKeys.AppId,
                DbCommonAppKeys.Version,
                DbCommonAppKeys.Name,
                DbCommonAppKeys.Hidden,
                DbCommonAppPerAgentKeys.Update,
                DbCommonAppKeys.ReleaseDate,
                DbCommonAppKeys.RebootRequired,
                DbCommonAppKeys.RvSeverity,
                DbCommonAppKeys.FilesDownloadStatus,
                DbCommonAppPerAgentKeys.Dependencies,
                DbCommonAppPerAgentKeys.InstallDate,
                DbCommonAppPerAgentKeys.Status,
                DbCommonAppPerAgentKeys.Update,
            ]
        )

        self.map_hash = (
            {
                DbCommonAppKeys.AppId: r.row[DbCommonAppKeys.AppId],
                DbCommonAppKeys.Version: r.row[DbCommonAppKeys.Version],
                DbCommonAppKeys.Name: r.row[DbCommonAppKeys.Name],
                DbCommonAppKeys.Hidden: r.row[DbCommonAppKeys.Hidden],
                DbCommonAppPerAgentKeys.Update: r.row[DbCommonAppPerAgentKeys.Update],
                DbCommonAppKeys.ReleaseDate: r.row[DbCommonAppKeys.ReleaseDate].to_epoch_time(),
                DbCommonAppKeys.RvSeverity: r.row[DbCommonAppKeys.RvSeverity],
                DbCommonAppKeys.RebootRequired: r.row[DbCommonAppKeys.RebootRequired],
                DbCommonAppKeys.FilesDownloadStatus: r.row[DbCommonAppKeys.FilesDownloadStatus],
                DbCommonAppPerAgentKeys.Dependencies: r.row[DbCommonAppPerAgentKeys.Dependencies],
                DbCommonAppPerAgentKeys.InstallDate: r.row[DbCommonAppPerAgentKeys.InstallDate].to_epoch_time(),
                DbCommonAppPerAgentKeys.Status: r.row[DbCommonAppPerAgentKeys.Status],
                DbCommonAppPerAgentKeys.Update: r.row[DbCommonAppPerAgentKeys.Update],
            }
        )

        if show_hidden in CommonAppKeys.ValidHiddenVals:
            self.show_hidden = show_hidden
        else:
            self.show_hidden = CommonKeys.NO

        if sort_key in self.pluck_list:
            self.sort_key = sort_key
        else:
            self.sort_key = DbCommonAppKeys.Name

        if sort == 'asc':
            self.sort = r.asc
        else:
            self.sort = r.desc


class RetrieveAgentAppsByAgentId(RetrieveAppsByAgentId):
    """
        This class is used to get agent data from within the Packages Page
    """
    def __init__(self, username, view_name,
                 agent_id, uri=None, method=None,
                 count=30, offset=0, sort='asc',
                 sort_key=AgentAppsKey.Name,
                 show_hidden=CommonKeys.NO):

        self.count = count
        self.uri = uri
        self.method = method
        self.offset = offset
        self.count = count
        self.sort = sort
        self.agent_id = agent_id
        self.username = username
        self.view_name = view_name
        self.CurrentAppsCollection = AppCollections.vFenseApps
        self.CurrentAppsIndexes = AgentAppsIndexes
        self.CurrentAppsPerAgentCollection = AppCollections.vFenseAppsPerAgent
        DbCommonAppKeys = AgentAppsKey
        DbCommonAppPerAgentKeys = AgentAppsPerAgentKey
        self.CurrentAppsPerAgentIndexes = AgentAppsPerAgentIndexes

        self.pluck_list = (
            [
                DbCommonAppKeys.AppId,
                DbCommonAppKeys.Version,
                DbCommonAppKeys.Name,
                DbCommonAppKeys.Hidden,
                DbCommonAppPerAgentKeys.Update,
                DbCommonAppKeys.ReleaseDate,
                DbCommonAppKeys.RebootRequired,
                DbCommonAppKeys.RvSeverity,
                DbCommonAppKeys.FilesDownloadStatus,
                DbCommonAppPerAgentKeys.Dependencies,
                DbCommonAppPerAgentKeys.InstallDate,
                DbCommonAppPerAgentKeys.Status,
                DbCommonAppPerAgentKeys.Update,
            ]
        )

        self.map_hash = (
            {
                DbCommonAppKeys.AppId: r.row[DbCommonAppKeys.AppId],
                DbCommonAppKeys.Version: r.row[DbCommonAppKeys.Version],
                DbCommonAppKeys.Name: r.row[DbCommonAppKeys.Name],
                DbCommonAppKeys.Hidden: r.row[DbCommonAppKeys.Hidden],
                DbCommonAppKeys.RvSeverity: r.row[DbCommonAppKeys.RvSeverity],
                DbCommonAppKeys.RebootRequired: r.row[DbCommonAppKeys.RebootRequired],
                DbCommonAppKeys.FilesDownloadStatus: r.row[DbCommonAppKeys.FilesDownloadStatus],
                DbCommonAppPerAgentKeys.Update: r.row[DbCommonAppPerAgentKeys.Update],
                DbCommonAppKeys.ReleaseDate: r.row[DbCommonAppKeys.ReleaseDate].to_epoch_time(),
                DbCommonAppPerAgentKeys.Dependencies: r.row[DbCommonAppPerAgentKeys.Dependencies],
                DbCommonAppPerAgentKeys.InstallDate: r.row[DbCommonAppPerAgentKeys.InstallDate].to_epoch_time(),
                DbCommonAppPerAgentKeys.Status: r.row[DbCommonAppPerAgentKeys.Status],
                DbCommonAppPerAgentKeys.Update: r.row[DbCommonAppPerAgentKeys.Update],
            }
        )

        if show_hidden in CommonAppKeys.ValidHiddenVals:
            self.show_hidden = show_hidden
        else:
            self.show_hidden = CommonKeys.NO

        if sort_key in self.pluck_list:
            self.sort_key = sort_key
        else:
            self.sort_key = DbCommonAppKeys.Name

        if sort == 'asc':
            self.sort = r.asc
        else:
            self.sort = r.desc

