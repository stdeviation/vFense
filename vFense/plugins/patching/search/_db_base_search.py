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

logging.config.fileConfig(VFENSE_LOGGING_CONFIG)
logger = logging.getLogger('rvapi')

class FetchAppsBase(object):
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
                DbCommonAppKeys.vFenseSeverity,
                DbCommonAppKeys.VulnerabilityId,
            ]
        )

        if sort_key in self.pluck_list:
            self.sort_key = sort_key
        else:
            self.sort_key = DbCommonAppKeys.Name


    @db_create_close
    def all(self, conn=None):
        count = 0
        data = []
        base_filter = self._set_base_filter()
        try:
            base = (
                base_filter
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
        base_filter = self._set_status_filter(pkg_status)
        try:
            base = (
                base_filter
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

            count = (
                base
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
        base_filter = self._set_sev_filter(sev)
        try:
            base = (
                base_filter
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
        base_filter = self._set_status_and_sev_filter(status, sev)
        try:
            base = (
                base_filter
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
                .distinct()
                .order_by(self.sort(self.sort_key))
                .skip(self.offset)
                .limit(self.count)
                .run(conn)
            )

            count = (
                base
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
        base_filter = self._set_base_filter()
        try:
            base = (
                base_filter
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
        base_filter = self._set_status_filter(status)
        try:
            base = (
                base_filter
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
        base_filter = self._set_status_filter(status)
        try:
            base = (
                base_filter
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
                    (x[DbCommonAppKeys.vFenseSeverity] == sev)
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
                .filter(
                    lambda x:
                    (x[DbCommonAppKeys.vFenseSeverity] == sev)
                    &
                    (x[DbCommonAppKeys.Name].match("(?i)"+name))
                )
                .distinct()
                .count()
                .run(conn)
            )

        except Exception as e:
            logger.exception(e)

        return(count, data)

    @db_create_close
    def by_status_and_name_and_sev_and_vuln(self, status, name,
                                            sev, conn=None):
        count = 0
        data = []
        base_filter = self._set_status_filter(status)
        try:
            base = (
                base_filter
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
                    (x[DbCommonAppKeys.vFenseSeverity] == sev)
                    &
                    (x[DbCommonAppKeys.Name].match("(?i)"+name))
                )
                .filter(
                    lambda x:
                    x[DbCommonAppKeys.VulnerabilityId] != ''
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
                    (x[DbCommonAppKeys.vFenseSeverity] == sev)
                    &
                    (x[DbCommonAppKeys.Name].match("(?i)"+name))
                )
                .filter(
                    lambda x:
                    x[DbCommonAppKeys.VulnerabilityId] != ''
                )
                .distinct()
                .count()
                .run(conn)
            )

        except Exception as e:
            logger.exception(e)

        return(count, data)

    @db_create_close
    def by_status_and_name_and_vuln(self, status, name, conn=None):
        count = 0
        data = []
        base_filter = self._set_status_filter(status)
        try:
            base = (
                base_filter
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
                    x[DbCommonAppKeys.Name].match("(?i)"+name)
                )
                .filter(
                    lambda x:
                    x[DbCommonAppKeys.VulnerabilityId] != ''
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
                .filter(
                    lambda x:
                    x[DbCommonAppKeys.VulnerabilityId] != ''
                )
                .distinct()
                .count()
                .run(conn)
            )

        except Exception as e:
            logger.exception(e)

        return(count, data)

    @db_create_close
    def by_sev_and_name(self, sev, name, conn=None):
        count = 0
        data = []
        base_filter = self._set_sev_filter(sev)
        try:
            base = (
                base_filter
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
                .count()
                .run(conn)
            )

        except Exception as e:
            logger.exception(e)

        return(count, data)

    @db_create_close
    def by_status_and_vuln(self, status, conn=None):
        count = 0
        data = []
        base_filter = self._set_status_filter(status)
        try:
            base = (
                base_filter
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
                    x[DbCommonAppKeys.VulnerabilityId] != ''
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
                    x[DbCommonAppKeys.VulnerabilityId] != ''
                )
                .count()
                .run(conn)
            )

        except Exception as e:
            logger.exception(e)

        return(count, data)

    @db_create_close
    def by_name_and_vuln(self, name, conn=None):
        count = 0
        data = []
        base_filter = self._set_base_filter()
        try:
            base = (
                base_filter
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
                    x[DbCommonAppKeys.VulnerabilityId] != ''
                )
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
                    x[DbCommonAppKeys.VulnerabilityId] != ''
                )
                .filter(
                    lambda x:
                    x[DbCommonAppKeys.Name].match("(?i)"+name)
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
            lambda x:
            {
                DbCommonAppKeys.AppId:
                    x['right'][DbCommonAppKeys.AppId],
                DbCommonAppKeys.Version:
                    x['right'][DbCommonAppKeys.Version],
                DbCommonAppKeys.Name:
                    x['right'][DbCommonAppKeys.Name],
                DbCommonAppKeys.ReleaseDate:
                    x['right'][DbCommonAppKeys.ReleaseDate].to_epoch_time(),
                DbCommonAppKeys.vFenseSeverity:
                    x['right'][DbCommonAppKeys.vFenseSeverity],
                DbCommonAppKeys.VulnerabilityId:
                    x['right'][DbCommonAppKeys.VulnerabilityId],
                DbCommonAppKeys.Hidden:
                    x['right'][DbCommonAppKeys.Hidden],
            }
        )

        return map_hash

    def _set_map_hash(self):
        """ Set the global properties. """

        map_hash = (
            {
                DbCommonAppKeys.AppId:
                    r.row[DbCommonAppKeys.AppId],
                DbCommonAppKeys.Version:
                    r.row[DbCommonAppKeys.Version],
                DbCommonAppKeys.Name:
                    r.row[DbCommonAppKeys.Name],
                DbCommonAppKeys.ReleaseDate:
                    r.row[DbCommonAppKeys.ReleaseDate].to_epoch_time(),
                DbCommonAppKeys.vFenseSeverity:
                    r.row[DbCommonAppKeys.vFenseSeverity],
                DbCommonAppKeys.VulnerabilityId:
                    r.row[DbCommonAppKeys.VulnerabilityId],
                DbCommonAppKeys.Hidden:
                    r.row[DbCommonAppKeys.Hidden],
            }
        )

        return map_hash

    def _set_base_filter(self):
        if self.view_name:
            map_hash = self._set_join_map_hash()
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
                .pluck('right')
                .eq_join(
                    lambda x:
                    x['right'][DbCommonAppPerAgentKeys.AppId],
                    r.table(self.apps_collection)
                )
                .map(map_hash)
            )

        else:
            map_hash = self._set_map_hash()
            base = (
                r
                .table(self.apps_collection)
                .map(map_hash)
            )

        return base

    def _set_sev_filter(self, sev):
        if self.view_name:
            map_hash = self._set_join_map_hash()
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
                .pluck('right')
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

        else:
            map_hash = self._set_map_hash()
            base = (
                r
                .table(self.apps_collection)
                .get_all(
                    sev,
                    index=DbCommonAppIndexes.vFenseSeverity
                )
                .map(map_hash)
            )

        return base

    def _set_status_filter(self, status):
        if self.view_name:
            map_hash = self._set_join_map_hash()
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
                .pluck('right')
                .eq_join(
                    lambda x:
                    x['right'][DbCommonAppPerAgentKeys.AppId],
                    r.table(self.apps_collection)
                )
                .map(map_hash)
            )

        else:
            map_hash = self._set_join_map_hash()
            base = (
                r
                .table(self.apps_per_agent_collection)
                .get_all(
                    status,
                    index=DbCommonAppPerAgentIndexes.Status
                )
                .eq_join(
                    lambda x:
                    x[DbCommonAppPerAgentKeys.AppId],
                    r.table(self.apps_collection)
                )
                .pluck('right')
                .map(map_hash)
            )

        return base

    def _set_status_and_sev_filter(self, status, sev):
        if self.view_name:
            map_hash = self._set_join_map_hash()
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
                .pluck('right')
                .eq_join(
                    lambda x:
                    [
                        x['right'][DbCommonAppPerAgentKeys.AppId], sev
                    ],
                    r.table(self.apps_collection),
                    index=DbCommonAppIndexes.AppIdAndvFenseSeverity
                )
                .map(map_hash)
            )

        else:
            map_hash = self._set_join_map_hash()
            base = (
                r
                .table(self.apps_per_agent_collection)
                .get_all(
                    status,
                    index=DbCommonAppPerAgentIndexes.Status
                )
                .eq_join(
                    lambda x:
                    [
                        x[DbCommonAppPerAgentKeys.AppId], sev
                    ],
                    r.table(self.apps_collection),
                    index=DbCommonAppIndexes.AppIdAndvFenseSeverity
                )
                .pluck('right')
                .map(map_hash)
            )

        return base
