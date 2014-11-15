from vFense.db.client import r
from vFense.core._constants import CommonKeys
from vFense.plugins.patching._db_model import (
    AppCollections, DbCommonAppKeys, DbCommonAppIndexes,
    DbCommonAppPerAgentKeys, DbCommonAppPerAgentIndexes
)
from vFense.plugins.patching._constants import CommonAppKeys
from vFense.core.tag._db_model import (
    TagCollections, TagsPerAgentKeys, TagsPerAgentIndexes
)
from vFense.plugins.patching.search._db_base_search import FetchAppsBase

class FetchAppsByTagId(FetchAppsBase):
    """
        This class is used to get agent data from within the Packages Page
    """
    def __init__(
        self, tag_id=None, sort_key=DbCommonAppKeys.Name,
        show_hidden=CommonKeys.NO,
        apps_collection=AppCollections.UniqueApplications,
        apps_per_agent_collection=AppCollections.AppsPerAgent, **kwargs
    ):
        super(FetchAppsByTagId, self).__init__(**kwargs)
        self.tag_id = tag_id
        self.show_hidden = show_hidden
        self.sort_key = sort_key
        if show_hidden not in CommonAppKeys.ValidHiddenVals:
            self.show_hidden = CommonKeys.NO

        self.apps_collection = apps_collection
        self.apps_per_agent_collection = apps_per_agent_collection

        self.pluck_list = (
            [
                DbCommonAppKeys.AppId,
                DbCommonAppKeys.Version,
                DbCommonAppKeys.Name,
                DbCommonAppPerAgentKeys.Update,
                DbCommonAppKeys.ReleaseDate,
                DbCommonAppKeys.Hidden,
                DbCommonAppKeys.RebootRequired,
                DbCommonAppKeys.vFenseSeverity,
                DbCommonAppKeys.FilesDownloadStatus,
                DbCommonAppPerAgentKeys.Dependencies,
                DbCommonAppPerAgentKeys.InstallDate,
                DbCommonAppPerAgentKeys.Status,
                DbCommonAppPerAgentKeys.Update,
                DbCommonAppKeys.VulnerabilityId,
            ]
        )

        if sort_key in self.pluck_list:
            self.sort_key = sort_key
        else:
            self.sort_key = DbCommonAppKeys.Name

    def _set_map_hash(self):
        """ Set the global properties. """

        map_hash = (
            lambda x:
            {
                DbCommonAppKeys.AppId: x['right'][DbCommonAppKeys.AppId],
                DbCommonAppKeys.Version: x['right'][DbCommonAppKeys.Version],
                DbCommonAppKeys.Name: x['right'][DbCommonAppKeys.Name],
                DbCommonAppKeys.Hidden: x['right'][DbCommonAppKeys.Hidden],
                DbCommonAppPerAgentKeys.Update: (
                    x['left']['right'][DbCommonAppPerAgentKeys.Update]
                ),
                DbCommonAppKeys.ReleaseDate: (
                    x['right'][DbCommonAppKeys.ReleaseDate].to_epoch_time()
                ),
                DbCommonAppKeys.vFenseSeverity: (
                    x['right'][DbCommonAppKeys.vFenseSeverity]
                ),
                DbCommonAppKeys.RebootRequired: (
                    x['right'][DbCommonAppKeys.RebootRequired]
                ),
                DbCommonAppKeys.FilesDownloadStatus: (
                    x['right'][DbCommonAppKeys.FilesDownloadStatus]
                ),
                DbCommonAppPerAgentKeys.Dependencies: (
                    x['left']['right'][DbCommonAppPerAgentKeys.Dependencies]
                ),
                DbCommonAppPerAgentKeys.InstallDate: (
                    x['left']['right'][DbCommonAppPerAgentKeys.InstallDate]
                    .to_epoch_time()
                ),
                DbCommonAppPerAgentKeys.Status: (
                    x['left']['right'][DbCommonAppPerAgentKeys.Status]
                ),
                DbCommonAppKeys.VulnerabilityId: (
                    x['right'][DbCommonAppKeys.VulnerabilityId]
                ),
            }
        )

        return map_hash

    def _set_base_filter(self):
        map_hash = self._set_map_hash()
        base = (
            r
            .table(TagCollections.TagsPerAgent)
            .get_all(self.tag_id, index=TagsPerAgentIndexes.TagId)
            .pluck(TagsPerAgentKeys.AgentId)
            .eq_join(
                lambda x:
                x[DbCommonAppPerAgentKeys.AgentId],
                r.table(self.apps_per_agent_collection),
                index=DbCommonAppPerAgentIndexes.AgentId
            )
            .eq_join(
                lambda x:
                x['right'][DbCommonAppPerAgentKeys.AppId],
                r.table(self.apps_collection)
            )
            .map(map_hash)
        )

        return base

    def _set_sev_filter(self, sev):
        map_hash = self._set_map_hash()
        base = (
            r
            .table(TagCollections.TagsPerAgent)
            .get_all(self.tag_id, index=TagsPerAgentIndexes.TagId)
            .pluck(TagsPerAgentKeys.AgentId)
            .eq_join(
                lambda x:
                x[DbCommonAppPerAgentKeys.AgentId],
                r.table(self.apps_per_agent_collection),
                index=DbCommonAppPerAgentIndexes.AgentId
            )
            .eq_join(
                lambda x:
                [
                    x['right'][DbCommonAppKeys.AppId], sev
                ],
                r.table(self.apps_collection),
                index=DbCommonAppIndexes.AppIdAndvFenseSeverity
            )
            .map(map_hash)
        )

        return base

    def _set_status_and_sev_filter(self, status, sev):
        map_hash = self._set_map_hash()
        base = (
            r
            .table(TagCollections.TagsPerAgent)
            .get_all(self.tag_id, index=TagsPerAgentIndexes.TagId)
            .pluck(TagsPerAgentKeys.AgentId)
            .eq_join(
                lambda x:
                [
                    status, x[DbCommonAppPerAgentKeys.AgentId]
                ],
                r.table(self.apps_per_agent_collection),
                index=DbCommonAppPerAgentIndexes.StatusAndAgentId
            )
            .eq_join(
                lambda x:
                [
                    x['right'][DbCommonAppKeys.AppId], sev
                ],
                r.table(self.apps_collection),
                index=DbCommonAppIndexes.AppIdAndvFenseSeverity
            )
            .map(map_hash)
        )

        return base

    def _set_status_filter(self, status):
        map_hash = self._set_map_hash()
        base = (
            r
            .table(TagCollections.TagsPerAgent)
            .get_all(self.tag_id, index=TagsPerAgentIndexes.TagId)
            .pluck(TagsPerAgentKeys.AgentId)
            .eq_join(
                lambda x:
                [
                    status, x[DbCommonAppPerAgentKeys.AgentId]
                ],
                r.table(self.apps_per_agent_collection),
                index=DbCommonAppPerAgentIndexes.StatusAndAgentId
            )
            .eq_join(
                lambda x:
                x['right'][DbCommonAppPerAgentKeys.AppId],
                r.table(self.apps_collection)
            )
            .map(map_hash)
        )

        return base
