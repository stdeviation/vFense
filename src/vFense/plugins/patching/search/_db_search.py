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
from vFense.core.agent._db_model import (
    AgentCollections, AgentKeys, AgentIndexes
)

logging.config.fileConfig(VFENSE_LOGGING_CONFIG)
logger = logging.getLogger('rvapi')

class FetchApps(object):
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


    @db_create_close
    def all(self, conn=None):
        count = 0
        data = []
        map_hash = self._set_join_map_hash()
        base_filter = self._set_base_filter()
        try:
            base = base_filter
            if self.show_hidden == CommonKeys.NO:
                base = (
                    base
                    .filter(
                        {
                            DbCommonAppKeys.Hidden: CommonKeys.NO
                        }
                    )
                )

            data = list(
                base
                .map(self.map_hash)
                .order_by(self.sort(self.sort_key))
                .skip(self.offset)
                .limit(self.count)
                .run(conn)
            )

            count = (
                base
                .count()
                .run(conn)
            )

        except Exception as e:
            logger.exception(e)

        return(count, data)


    @db_create_close
    def by_status(self, pkg_status, conn=None):
        count = 0
        data = []
        map_hash = self._set_join_map_hash()
        base_filter = self._set_status_filter(pkg_status)
        try:
            base = (
                base_filter
                .map(map_hash)
            )

            if self.show_hidden == CommonKeys.NO:
                base = base.filter(
                    {DbCommonAppKeys.Hidden: CommonKeys.NO}
                )

                count = (
                    base
                    .pluck(self.CurrentAppsKey.AppId)
                    .distinct()
                    .count()
                    .run(conn)
                )

                data = list(
                    base
                    .distinct()
                    .order_by(self.sort(self.sort_key))
                    .skip(self.offset)
                    .limit(self.count)
                    .run(conn)
                )

        except Exception as e:
            logger.exception(e)

        return(count, data)

    @db_create_close
    def by_severity(self, sev, conn=None):
        count = 0
        data = []
        map_hash = self._set_join_map_hash()
        base_filter = self._set_sev_filter(sev)
        try:
            base = base_filter
            if self.show_hidden == CommonKeys.NO:
                base = (
                    base
                    .map(self.map_hash)
                    .filter(
                        {
                            DbCommonAppKeys.Hidden: CommonKeys.NO
                        }
                    )
                )

                data = list(
                    base
                    .order_by(self.sort(self.sort_key))
                    .skip(self.offset)
                    .limit(self.count)
                    .run(conn)
                )

                count = (
                    base
                    .count()
                    .run(conn)
                )

        except Exception as e:
            logger.exception(e)

        return(count, data)

    @db_create_close
    def by_status_and_sev(self, status, sev, conn=None):
        count = 0
        data = []
        map_hash = self._set_join_map_hash()
        base_filter = self._set_status_filter(status)
        try:
            base = (
                base_filter
                .map(self.joined_map_hash)
            )

            if self.show_hidden == CommonKeys.NO:
                base = (
                    base
                    .filter(
                        {
                            DbCommonAppKeys.Hidden: CommonKeys.NO
                        }
                    )
                )

                data = list(
                    base
                    .filter(
                        lambda x:
                        x[self.CurrentAppsKey.RvSeverity] == sev
                    )
                    .distinct()
                    .order_by(self.sort(self.sort_key))
                    .skip(self.offset)
                    .limit(self.count)
                    .run(conn)
                )

                count = (
                    base
                    .filter(
                        lambda x:
                        x[self.CurrentAppsKey.RvSeverity] == sev
                    )
                    .pluck(self.pluck_list)
                    .distinct()
                    .count()
                    .run(conn)
                )

        except Exception as e:
            logger.exception(e)

        return(count, data)

    @db_create_close
    def by_name(self, name, conn=None):
        count = 0
        data = []
        map_hash = self._set_join_map_hash()
        base_filter = self._set_base_filter()
        try:
            base = base_filter

            if self.show_hidden == CommonKeys.NO:
                base = (
                    base
                    .filter(
                        {
                            DbCommonAppKeys.Hidden: CommonKeys.NO
                        }
                    )
                )

            data = list(
                base
                .map(self.map_hash)
                .filter(
                    lambda x:
                    x[DbCommonAppKeys.Name].match("(?i)"+name)
                )
                .order_by(self.sort(self.sort_key))
                .skip(self.offset)
                .limit(self.count)
                .run(conn)
            )

            count = (
                base
                .filter(
                    lambda x:
                    x[DbCommonAppKeys.Name].match("(?i)"+name)
                )
                .pluck(self.CurrentAppsKey.AppId)
                .count()
                .run(conn)
            )

        except Exception as e:
            logger.exception(e)

        return(count, data)

    @db_create_close
    def by_status_and_name(self, status, name, conn=None):
        count = 0
        data = []
        map_hash = self._set_join_map_hash()
        base_filter = self._set_status_filter(status)
        try:
            base = (
                base_filter
                .map(self.joined_map_hash)
            )

            if self.show_hidden == CommonKeys.NO:
               base = base.filter({self.CurrentAppsKey.Hidden: CommonKeys.NO})

            data = list(
                base
                .filter(
                    lambda x:
                    x[DbCommonAppKeys.Name].match("(?i)"+name)
                )
                .distinct()
                .order_by(self.sort(self.sort_key))
                .skip(self.offset)
                .limit(self.count)
                .run(conn)
            )

            count = (
                base
                .filter(
                    lambda x:
                    x[DbCommonAppKeys.Name].match("(?i)"+name)
                )
                .pluck(self.CurrentAppsKey.AppId)
                .count()
                .run(conn)
            )

        except Exception as e:
            logger.exception(e)

        return(count, data)

    @db_create_close
    def by_status_and_name_and_sev(self, status, name, sev, conn=None):
        count = 0
        data = []
        map_hash = self._set_join_map_hash()
        base_filter = self._set_status_filter(status)
        try:
            base = (
                base_filter
                .map(self.joined_map_hash)
            )

            if self.show_hidden == CommonKeys.NO:
                base = (
                    base
                    .filter(
                        {
                            DbCommonAppKeys.Hidden: CommonKeys.NO
                        }
                    )
                )

                data = list(
                    base
                    .filter(
                        lambda x:
                        (x[DbCommonAppKeys.RvSeverity] == sev)
                        &
                        (x[DbCommonAppKeys.Name].match("(?i)"+name))
                    )
                    .distinct()
                    .order_by(self.sort(self.sort_key))
                    .skip(self.offset)
                    .limit(self.count)
                    .run(conn)
                )

                count = (
                    base
                    .pluck(self.CurrentAppsKey.RvSeverity, self.CurrentAppsKey.Name)
                    .distinct()
                    .filter(
                        lambda x:
                        (x[DbCommonAppKeys.RvSeverity] == sev)
                        &
                        (x[DbCommonAppKeys.Name].match("(?i)"+name))
                    )
                    .count()
                    .run(conn)
                )

        except Exception as e:
            logger.exception(e)

        return(count, data)


    def _set_join_map_hash(self):
        """ Set the global properties. """

        map_hash = (
            {
                DbCommonAppKeys.AppId:
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
        return map_hash

    def _set_map_hash(self):
        """ Set the global properties. """

        map_hash = (
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
        return map_hash

    def _set_base_filter(self):
        if self.view_name:
            base = (
                r
                .table(AgentCollections.Agents)
                .get_all(
                    self.view_name,
                    index=AgentIndexes.Views
                )
                .pluck(AgentKeys.AgentId)
                .eq_join(
                    lambda x:
                    x[AgentKeys.AgentId],
                    r.table(self.apps_per_agent_collection),
                    index=DbCommonAppPerAgentIndexes.AgentId
                )
                .zip()
                .eq_join(
                    DbCommonAppPerAgentKeys.AppId,
                    r.table(self.apps_collection)
                )
            )

        else:
            base = (
                r
                .table(AgentCollections.Agents)
                .pluck(AgentKeys.AgentId)
                .eq_join(
                    lambda x:
                    x[AgentKeys.AgentId],
                    r.table(self.apps_per_agent_collection),
                    index=DbCommonAppPerAgentIndexes.AgentId
                )
                .zip()
                .eq_join(
                    DbCommonAppPerAgentKeys.AppId,
                    r.table(self.apps_collection)
                )
            )

        return base

    def _set_sev_filter(self):
        if self.view_name:
            base = (
                r
                .table(AgentCollections.Agents)
                .get_all(
                    self.view_name,
                    index=AgentIndexes.Views
                )
                .pluck(AgentKeys.AgentId)
                .eq_join(
                    lambda x:
                    x[AgentKeys.AgentId],
                    r.table(self.apps_per_agent_collection),
                    index=DbCommonAppPerAgentIndexes.AgentId
                )
                .zip()
                .eq_join(
                    lambda x:
                    [
                        x[DbCommonAppKeys.AppId],
                        x[DbCommonAppKeys.RvSeverity]
                    ],
                    r.table(self.apps_collection),
                    index=DbCommonAppIndexes.AppIdAndRvSeverity
                )
            )

        else:
            base = (
                r
                .table(AgentCollections.Agents)
                .pluck(AgentKeys.AgentId)
                .eq_join(
                    lambda x:
                    x[AgentKeys.AgentId],
                    r.table(self.apps_per_agent_collection),
                    index=DbCommonAppPerAgentIndexes.AgentId
                )
                .zip()
                .eq_join(
                    lambda x:
                    [
                        x[DbCommonAppKeys.AppId],
                        x[DbCommonAppKeys.RvSeverity]
                    ],
                    r.table(self.apps_collection).
                    index=DbCommonAppIndexes.AppIdAndRvSeverity
                )
            )

        return base


    def _set_status_filter(self, status):
        if self.view_name:
            base = (
                r
                .table(AgentCollections.Agents)
                .get_all(
                    self.view_name,
                    index=AgentIndexes.Views
                )
                .pluck(AgentKeys.AgentId)
                .eq_join(
                    lambda x:
                    [status, x[AgentKeys.AgentId]],
                    r.table(self.apps_per_agent_collection),
                    index=DbCommonAppPerAgentIndexes.StatusAndAgentId
                )
                .zip()
                .eq_join(
                    DbCommonAppPerAgentKeys.AppId,
                    r.table(self.apps_collection)
                )
            )

        else:
            base = (
                r
                .table(AgentCollections.Agents)
                .pluck(AgentKeys.AgentId)
                .eq_join(
                    lambda x:
                    [status, x[AgentKeys.AgentId]],
                    r.table(self.apps_per_agent_collection),
                    index=DbCommonAppPerAgentIndexes.StatusAndAgentId
                )
                .zip()
                .eq_join(
                    DbCommonAppPerAgentKeys.AppId,
                    r.table(self.apps_collection)
                )
            )

        return base
