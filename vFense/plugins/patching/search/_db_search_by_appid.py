from vFense.db.client import db_create_close, r
from vFense.core.decorators import time_it, catch_it
from vFense.plugins.patching._db_model import (
    AppCollections, DbCommonAppPerAgentKeys, DbCommonAppPerAgentIndexes
)
from vFense.core.agent._db_model import (
    AgentCollections, AgentKeys
)
from vFense.plugins.patching.search._db_base_search import FetchAppsBase

class FetchAgentsByAppId(FetchAppsBase):
    """
        This class is used to get agent data from within the Packages Page
    """
    def __init__(
        self, app_id=None, sort_key=AgentKeys.ComputerName,
        apps_collection=AppCollections.UniqueApplications,
        apps_per_agent_collection=AppCollections.AppsPerAgent, **kwargs
    ):
        self.app_id = app_id

        self.apps_collection = apps_collection
        self.apps_per_agent_collection = apps_per_agent_collection

        self.pluck_list = (
            [
                AgentKeys.ComputerName,
                AgentKeys.DisplayName,
                AgentKeys.AgentId,
            ]
        )

        if self.sort_key not in self.pluck_list:
            self.sort_key = AgentKeys.ComputerName

    @time_it
    @catch_it((0, []))
    @db_create_close
    def by_status(self, status, conn=None):
        base = self._set_status_filter(status)
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

        return(count, data)

    @time_it
    @catch_it((0, []))
    @db_create_close
    def by_name(self, name, conn=None):
        base = self._set_base_filter()
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
        return(count, data)

    @time_it
    @catch_it((0, []))
    @db_create_close
    def by_status_and_name(self, status, name, conn=None):
        base = self._set_status_filter(status)
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
