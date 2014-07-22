from vFense.db.client import r, db_create_close
from vFense.core._constants import (
    CommonKeys
)
from vFense.plugins.patching._constants import (
    CommonAppKeys
)

from vFense.core.tag._db_model import (
    TagCollections, TagsPerAgentKeys, TagsPerAgentIndexes
)
from vFense.plugins.patching._db_model import (
    DbCommonAppPerAgentKeys, AppCollections, DbCommonAppPerAgentIndexes,
    DbCommonAppIndexes, DbCommonAppKeys
)

class FetchAppsIdsForSchedule(object):
    def __init__(self, app_collection=AppCollections.UniqueApplications,
                 apps_per_agent_collection=AppCollections.AppsPerAgent):
        """
        Kwargs:
            app_collection (str): The table to use for querying applications
                default='unique_applications'
            apps_per_agent_collection (str): The table to use for querying
                applications per agent.
                default='apps_per_agent'

        Basic Usage:
            >>> from vFense.plugins.patching.scheduler._db import FetchAppsIdsForSchedule
            >>> fetch = FetchAppsIdsForSchedule()
        """
        self.app_collection = app_collection
        self.apps_per_agent_collection = apps_per_agent_collection

    @db_create_close
    def by_sev_for_agent(sev, agent_id, conn=None):
        """Fetch all application ids by severity for an agent.
        Args:
            sev (str): The severity of the applications you are searching for.
            agent_id (str): The 36 character UUID of the agent.

        Basic Usage:
            >>> from vFense.plugins.patching.scheduler._db import FetchAppsIdsForSchedule
            >>> fetch = FetchAppsIdsForSchedule()
            >>> fetch.by_sev_for_agent('critical', 'agent_id')

        Returns:

        """
        sev = sev.capitalize()
        app_ids = (
            r
            .table(self.apps_per_agent_collection)
            .get_all(
                [
                    CommonAppKeys.AVAILABLE, agent_id
                ],
                index=DbCommonAppPerAgentIndexes.StatusAndAgentId
            )
            .eq_join(
                lambda x:
                [
                    x[DbCommonAppKeys.AppId], sev, CommonKeys.NO
                ],
                index=DbCommonAppIndexes.AppIdAndvFenseSeverityAndHidden
            )
            .map(
                lambda x: x['right'][DbCommonAppKeys.AppId]
            )
            .run(conn)
        )

        return app_ids

    @db_create_close
    def by_sev_for_tag(sev, tag_id, conn=None):
        """Fetch all application ids by severity for an agent.
        Args:
            sev (str): The severity of the applications you are searching for.
            tag_id (str): The 36 character UUID of the tag.

        Basic Usage:
            >>> from vFense.plugins.patching.scheduler._db import FetchAppsIdsForSchedule
            >>> fetch = FetchAppsIdsForSchedule()
            >>> fetch.by_sev_for_tag('tag_id')

        Returns:

        """
        sev = sev.capitalize()
        app_ids = (
            r
            .table(TagCollections.TagsPerAgent)
            .get_all(tag_id, index=TagsPerAgentIndexes.TagId)
            .pluck(TagsPerAgentKeys.AgentId)
            .eq_join(
                lambda x:
                [
                    CommonAppKeys.AVAILABLE,
                    x[DbCommonAppPerAgentKeys.AgentId]
                ],
                r.table(self.apps_per_agent_collection),
                index=DbCommonAppPerAgentIndexes.StatusAndAgentId
            )
            .eq_join(
                lambda x:
                [
                    x['right'][DbCommonAppKeys.AppId], sev, CommonKeys.NO
                ],
                r.table(self.app_collection),
                index=DbCommonAppIndexes.AppIdAndvFenseSeverityAndHidden
            )
            .map(
                lambda x: x['right'][DbCommonAppKeys.AppId]
            )
            .run(conn)
        )

        return app_ids

class FetchCustomAppsIdsForSchedule(FetchAppsIdsForSchedule):
    def __init__(self):
        self.app_collection = AppCollections.CustomApps
        self.apps_per_agent_collection = AppCollections.CustomAppsPerAgent

class FetchSupportedAppsIdsForSchedule(FetchAppsIdsForSchedule):
    def __init__(self):
        self.app_collection = AppCollections.SupportedApps
        self.apps_per_agent_collection = AppCollections.SupportedAppsPerAgent


