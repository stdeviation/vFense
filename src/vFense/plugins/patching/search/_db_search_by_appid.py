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

class FetchAgentsByAppId(object):
    """
        This class is used to get agent data from within the Packages Page
    """
    def __init__(self, app_id,
                 count=DefaultQueryValues.COUNT,
                 offset=DefaultQueryValues.OFFSET,
                 sort=SortValues.ASC,
                 sort_key=AgentKeys.ComputerName,
                 apps_collection=AppCollections.UniqueApplications,
                 apps_per_agent_collection=AppCollections.AppsPerAgent):
        """
        """
        self.count = count
        self.offset = offset
        self.app_id = app_id
        self.sort_key = sort_key

        if sort == SortValues.ASC:
            self.sort = r.asc
        else:
            self.sort = r.desc

        self.apps_collection = apps_collection
        self.apps_per_agent_collection = apps_per_agent_collection

        self.pluck_list = (
            [
                AgentKeys.ComputerName,
                AgentKeys.DisplayName,
                AgentKeys.AgentId,
            ]
        )

        if sort_key in self.pluck_list:
            self.sort_key = sort_key
        else:
            self.sort_key = AgentKeys.ComputerName


    @db_create_close
    def by_status(self, status, conn=None):
        count = 0
        data = []
        base_filter = self._set_status_filter(status)
        try:
            base = (
                base_filter
            )

            count = (
                base
                .count()
                .run(conn)
            )

            data = list(
                base
                .order_by(self.sort(self.sort_key))
                .skip(self.offset)
                .limit(self.count)
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

            data = list(
                base
                .filter(
                    lambda x:
                    (x[AgentKeys.ComputerName].match("(?i)"+name))
                    |
                    (x[AgentKeys.DisplayName].match("(?i)"+name))
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
                    (x[AgentKeys.ComputerName].match("(?i)"+name))
                    |
                    (x[AgentKeys.DisplayName].match("(?i)"+name))
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

            data = list(
                base
                .filter(
                    lambda x:
                    (x[AgentKeys.ComputerName].match("(?i)"+name))
                    |
                    (x[AgentKeys.DisplayName].match("(?i)"+name))
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
                    (x[AgentKeys.ComputerName].match("(?i)"+name))
                    |
                    (x[AgentKeys.DisplayName].match("(?i)"+name))
                )
                .count()
                .run(conn)
            )

        except Exception as e:
            logger.exception(e)

        return(count, data)

    def _set_map_hash(self):
        """ Set the global properties. """

        map_hash = (
            lambda x:
            {
                AgentKeys.ComputerName: x['right'][AgentKeys.ComputerName],
                AgentKeys.DisplayName: x['right'][AgentKeys.DisplayName],
                AgentKeys.AgentId: x['right'][AgentKeys.AgentId],
            }
        )

        return map_hash

    def _set_base_filter(self):
        map_hash = self._set_map_hash()
        base = (
            r
            .table(self.apps_per_agent_collection)
            .get_all(
                self.app_id,
                index=DbCommonAppPerAgentIndexes.AppId
            )
            .eq_join(
                lambda x:
                x[DbCommonAppPerAgentKeys.AgentId],
                r.table(AgentCollections.Agents)
            )
            .map(map_hash)
        )

        return base

    def _set_status_filter(self, status):
        map_hash = self._set_map_hash()
        base = (
            r
            .table(self.apps_per_agent_collection)
            .get_all(
                [self.app_id, status],
                index=DbCommonAppPerAgentIndexes.AppIdAndStatus
            )
            .eq_join(
                lambda x:
                x[DbCommonAppPerAgentKeys.AgentId],
                r.table(AgentCollections.Agents)
            )
            .map(map_hash)
        )

        return base
