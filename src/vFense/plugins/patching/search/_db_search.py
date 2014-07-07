#!/usr/bin/env python

import logging
import logging.config
from vFense import VFENSE_LOGGING_CONFIG
from vFense.db.client import db_create_close, r
from vFense.core._constants import (
    SortValues, DefaultQueryValues, CommonKeys
)
from vFense.plugins.patching._db_model import (
    AppCollections, DbCommonAppKeys, DbCommonAppIndexes,
    DbCommonAppPerAgentKeys, DbCommonAppPerAgentIndexes
)
from vFense.plugins.patching._constants import (
    CommonAppKeys
)
from vFense.core.agent._db_model import (
    AgentCollections, AgentKeys, AgentIndexes
)
from vFense.plugins.patching.search._db_base_search import FetchAppsBase

logging.config.fileConfig(VFENSE_LOGGING_CONFIG)
logger = logging.getLogger('rvapi')

class FetchApps(FetchAppsBase):
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
        self.count = count
        self.offset = offset
        self.view_name = view_name
        self.show_hidden = show_hidden
        self.sort_key = sort_key

        if sort == SortValues.ASC:
            self.sort = r.asc
        else:
            self.sort = r.desc

        if show_hidden in CommonAppKeys.ValidHiddenVals:
            self.show_hidden = show_hidden
        else:
            self.show_hidden = CommonKeys.NO

        self.apps_collection = apps_collection
        self.apps_per_agent_collection = apps_per_agent_collection

        self.pluck_list = (
            [
                DbCommonAppKeys.AppId,
                DbCommonAppKeys.Version,
                DbCommonAppKeys.Name,
                DbCommonAppKeys.ReleaseDate,
                DbCommonAppKeys.RvSeverity,
                DbCommonAppKeys.VulnerabilityId,
            ]
        )

        if sort_key in self.pluck_list:
            self.sort_key = sort_key
        else:
            self.sort_key = DbCommonAppKeys.Name

    @db_create_close
    def by_id(self, app_id, conn=None):
        count = 0
        data = []
        agent_stats_merge = self._set_agent_stats_merge(app_id)
        try:
            base = (
                r
                .table(self.apps_collection)
                .get(app_id)
                .merge(
                    {
                        DbCommonAppKeys.ReleaseDate: (
                            r.row[DbCommonAppKeys.ReleaseDate].to_epoch_time()
                        )
                    }
                )
            )

            data = (
                base
                .merge(agent_stats_merge)
                .run(conn)
            )

            if data:
                count = 1

        except Exception as e:
            logger.exception(e)

        return(count, data)

    def _set_agent_stats_merge(self, app_id):
        """ Set the global properties. """
        if self.view_name:
            merge_hash = (
                lambda x:
                {
                    CommonAppKeys.AGENT_STATS: (
                        [
                            {
                                CommonAppKeys.COUNT: (
                                    r
                                    .table(AgentCollections.Agents)
                                    .get_all(
                                        self.view_name,
                                        index=AgentIndexes.Views
                                    )
                                    .pluck(AgentKeys.AgentId)
                                    .eq_join(
                                        lambda y:
                                        [
                                            y[DbCommonAppPerAgentKeys.AgentId],
                                            CommonAppKeys.INSTALLED,
                                            app_id
                                        ],
                                        r.table(self.apps_per_agent_collection),
                                        index=DbCommonAppPerAgentIndexes.AgentIdAndAppId
                                    )
                                    .count()
                                ),
                                CommonAppKeys.STATUS: CommonAppKeys.INSTALLED,
                                CommonAppKeys.NAME: (
                                    CommonAppKeys.INSTALLED.capitalize()
                                )
                            },
                            {
                                CommonAppKeys.COUNT: (
                                    r
                                    .table(AgentCollections.Agents)
                                    .get_all(
                                        self.view_name,
                                        index=AgentIndexes.Views
                                    )
                                    .pluck(AgentKeys.AgentId)
                                    .eq_join(
                                        lambda y:
                                        [
                                            y[DbCommonAppPerAgentKeys.AgentId],
                                            CommonAppKeys.AVAILABLE,
                                            app_id
                                        ],
                                        r.table(self.apps_per_agent_collection),
                                        index=DbCommonAppPerAgentIndexes.AgentIdAndAppId
                                    )
                                    .count()
                                ),
                                CommonAppKeys.STATUS: CommonAppKeys.AVAILABLE,
                                CommonAppKeys.NAME: (
                                    CommonAppKeys.AVAILABLE.capitalize()
                                )
                            },
                            {
                                CommonAppKeys.COUNT: (
                                    r
                                    .table(AgentCollections.Agents)
                                    .get_all(
                                        self.view_name,
                                        index=AgentIndexes.Views
                                    )
                                    .pluck(AgentKeys.AgentId)
                                    .eq_join(
                                        lambda y:
                                        [
                                            y[DbCommonAppPerAgentKeys.AgentId],
                                            CommonAppKeys.PENDING,
                                            app_id
                                        ],
                                        r.table(self.apps_per_agent_collection),
                                        index=DbCommonAppPerAgentIndexes.AgentIdAndAppId
                                    )
                                    .count()
                                ),
                                CommonAppKeys.STATUS: CommonAppKeys.PENDING,
                                CommonAppKeys.NAME: (
                                    CommonAppKeys.PENDING.capitalize()
                                )
                            },
                        ]
                    )
                }
            )

        else:
            merge_hash = (
                lambda x:
                {
                    CommonAppKeys.AGENT_STATS: (
                        [
                            {
                                CommonAppKeys.COUNT: (
                                    r
                                    .table(self.apps_per_agent_collection)
                                    .get_all(
                                        [
                                            app_id,
                                            CommonAppKeys.INSTALLED
                                        ],
                                        index=DbCommonAppPerAgentIndexes.AppIdAndStatus
                                    )
                                    .count()
                                ),
                                CommonAppKeys.STATUS: CommonAppKeys.INSTALLED,
                                CommonAppKeys.NAME: (
                                    CommonAppKeys.INSTALLED.capitalize()
                                )
                            },
                            {
                                CommonAppKeys.COUNT: (
                                    r
                                    .table(self.apps_per_agent_collection)
                                    .get_all(
                                        [
                                            app_id,
                                            CommonAppKeys.AVAILABLE
                                        ],
                                        index=DbCommonAppPerAgentIndexes.AppIdAndStatus
                                    )
                                    .count()
                                ),
                                CommonAppKeys.STATUS: CommonAppKeys.AVAILABLE,
                                CommonAppKeys.NAME: (
                                    CommonAppKeys.AVAILABLE.capitalize()
                                )
                            },
                            {
                                CommonAppKeys.COUNT: (
                                    r
                                    .table(self.apps_per_agent_collection)
                                    .get_all(
                                        [
                                            app_id,
                                            CommonAppKeys.PENDING
                                        ],
                                        index=DbCommonAppPerAgentIndexes.AppIdAndStatus
                                    )
                                    .count()
                                ),
                                CommonAppKeys.STATUS: CommonAppKeys.PENDING,
                                CommonAppKeys.NAME: (
                                    CommonAppKeys.PENDING.capitalize()
                                )
                            },
                        ]
                    )
                }
            )

        return merge_hash
