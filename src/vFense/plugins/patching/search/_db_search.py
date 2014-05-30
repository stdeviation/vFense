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
    CommonAppKeys, CommonSeverityKeys
)

logging.config.fileConfig(VFENSE_LOGGING_CONFIG)
logger = logging.getLogger('rvapi')

class FetchApps(object):
    """
        This class is used to get agent data from within the Packages Page
    """
    def __init__(self, view_name=None,
                 count=30, offset=0, sort='asc',
                 sort_key=DbCommonAppKeys.Name,
                 show_hidden=CommonKeys.NO):
        """
        """
        self._set_global_properties(
            count, offset, show_hidden, sort_key, sort, view_name
        )

    def _set_global_properties(
            self, count, offset, show_hidden, sort_key, sort, view_name
            ):
        self.count = count
        self.offset = offset
        self.view_name = view_name
        self.show_hidden = show_hidden
        self.sort_key = sort_key
        if sort == 'asc':
            self.sort = r.asc
        else:
            self.sort = r.desc

    def set_db_properties(self, apps_collection, apps_per_agent_collection):
        """ Set the global properties. """

        self.CurrentAppsCollection = apps_collection
        self.CurrentAppsPerAgentCollection = apps_per_agent_collection

        self.joined_map_hash = (
            {
                DbCommonAppKeys.Id:
                    r.row['right'][DbCommonAppKeys.AppId],
                DbCommonAppKeys.Version:
                    r.row['right'][DbCommonAppKeys.Version],
                DbCommonAppKeys.Name:
                    r.row['right'][DbCommonAppKeys.Name],
                DbCommonAppKeys.ReleaseDate:
                    r.row['right'][DbCommonAppKeys.ReleaseDate].to_epoch_time(),
                DbCommonAppKeys.RvSeverity:
                    r.row['right'][DbCommonAppKeys.RvSeverity],
                DbCommonAppKeys.VulnerabilityId:
                    r.row['right'][DbCommonAppKeys.VulnerabilityId],
                DbCommonAppKeys.Hidden:
                    r.row['right'][DbCommonAppKeys.Hidden],
            }
        )

        self.map_hash = (
            {
                DbCommonAppKeys.AppId: r.row[DbCommonAppKeys.AppId],
                DbCommonAppKeys.Version: r.row[DbCommonAppKeys.Version],
                DbCommonAppKeys.Name: r.row[DbCommonAppKeys.Name],
                DbCommonAppKeys.ReleaseDate: (
                    r.row[DbCommonAppKeys.ReleaseDate].to_epoch_time()
                ),
                DbCommonAppKeys.RvSeverity: r.row[DbCommonAppKeys.RvSeverity],
                DbCommonAppKeys.VulnerabilityId: (
                    r.row[DbCommonAppKeys.VulnerabilityId],
                )
            }
        )
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

    def _base_filter(self):
        if self.view_name:
            base = (
                r
                .table(self.CurrentAppsCollection)
                .get_all(
                    self.view_name,
                    index=DbCommonAppIndexes.Views
                )
            )

        else:
            base = (
                r
                .table(self.CurrentAppsCollection)
            )

        return base

    def _base_per_agent_filter(self):
        if self.view_name:
            base = (
                r
                .table(self.CurrentAppsPerAgentCollection)
                .get_all(
                    self.view_name,
                    index=DbCommonAppPerAgentIndexes.Views
                )
            )

        else:
            base = (
                r
                .table(self.CurrentAppsPerAgentCollection)
            )

        return base
