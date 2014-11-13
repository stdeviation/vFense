from vFense.db.client import db_create_close, r
from vFense.core.agent._constants import AgentCommonKeys
from vFense.core.agent._db_model import (
    AgentKeys, AgentCollections
)
from vFense.core.tag._db_model import (
    TagCollections, TagKeys, TagsPerAgentKeys, TagsPerAgentIndexes
)
from vFense.plugins.patching._db_model import (
    AppCollections, AppsKey, AppsPerAgentIndexes
)
from vFense.plugins.patching._db_model import *
from vFense.plugins.patching._constants import CommonAppKeys
from vFense.core.decorators import time_it, catch_it
from vFense.search._db_base import FetchBase


class FetchTags(FetchBase):
    """Tag database queries"""
    def __init__(self, sort_key=TagKeys.TagName, **kwargs):
        super(FetchTags, self).__init__(**kwargs)

        self.keys_to_pluck = [
            TagKeys.TagName, TagKeys.TagId, TagKeys.ViewName,
            TagKeys.Environment, AgentCommonKeys.AVAIL_UPDATES,
            AgentCommonKeys.AVAIL_VULN, AgentCollections.Agents
        ]

    @time_it
    @catch_it((0, []))
    @db_create_close
    def by_id(self, tag_id, conn=None):
        """Retrieve a tag by its id and all of its properties.

        Basic Usage:
            >>> from vFense.tag.search._db import FetchTags
            >>> tag = FetchTags()
            >>> tag.by_id('96f02bcf-2ada-465c-b175-0e5163b36e1c')

        Returns:
            Tuple
            (count, group_data)
        >>>
        """
        count = 0
        data = []
        base_filter = (
            r
            .table(TagCollections.Tags)
        )
        agent_merge_query = self._set_agent_merge_query(tag_id)
        tag_merge_query = self._set_tag_merge_query(tag_id)

        count = (
            base_filter
            .get_all(tag_id)
            .count()
            .run(conn)
        )

        data = (
            base_filter
            .get(tag_id)
            .merge(agent_merge_query)
            .merge(tag_merge_query)
            .run(conn)
        )

        return(count, data)

    @time_it
    @catch_it((0, []))
    @db_create_close
    def by_agent_id(self, agent_id, conn=None):
        """Retrieve a tags by agent id and all of its properties.

        Basic Usage:
            >>> from vFense.tag.search._db import FetchTags
            >>> tag = FetchTags()
            >>> tag.by_agent_id('96f02bcf-2ada-465c-b175-0e5163b36e1c')

        Returns:
            Tuple
            (count, tag_data)
        >>>
        """
        count = 0
        data = []
        base_filter = (
            r
            .table(TagCollections.TagsPerAgent)
            .get_all(agent_id, index=TagsPerAgentIndexes.AgentId)
        )
        count = (
                base_filter
                .count()
                .run(conn)
        )

        data = list(
            base_filter
            .eq_join(
                lambda x:
                x[TagsPerAgentKeys.TagId],
                r.table(TagCollections.Tags)
            )
            .zip()
            .pluck(
                TagKeys.TagName, TagKeys.TagId,
                TagKeys.ViewName, TagKeys.Environment
            )
            .run(conn)
        )

        return(count, data)

    @time_it
    @catch_it((0, []))
    @db_create_close
    def by_name(self, name, conn=None):
        """Query tags by the tag name.
        Args:
            name (str): The regex you are searching by

        Basic Usage:
            >>> from vFense.core.tag.search._db import FetchTags
            >>> search_tags = FetchTags(view_name='default')
            >>> search_tags.by_name('ubu')

        Returns:
            List of dictionairies.
        """
        count = 0
        data = []
        merge_query = self._set_merge_query()
        agent_merge_count = self._set_agent_merge_count()
        base_filter = self._set_base_query()
        count = (
            base_filter
            .filter(r.row[TagKeys.TagName].match("(?i)^"+name))
            .count()
            .run(conn)
        )

        data = list(
            base_filter
            .filter(r.row[TagKeys.TagName].match("(?i)^"+name))
            .merge(merge_query)
            .merge(agent_merge_count)
            .pluck(self.keys_to_pluck)
            .order_by(self.sort(self.sort_key))
            .skip(self.offset)
            .limit(self.count)
            .run(conn)
        )

        return(count, data)

    @time_it
    @catch_it((0, []))
    @db_create_close
    def all(self, conn=None):
        """Retrieve all tags.
        Basic Usage:
            >>> from vFense.core.tag.search._db import FetchTags
            >>> search_tags = FetchTags(view_name='default')
            >>> search_tags.all()

        Returns:
            List of dictionairies.
        """
        count = 0
        data = []
        base_filter = self._set_base_query()
        query_merge = self._set_merge_query()
        agent_merge_count = self._set_agent_merge_count()
        count = (
            base_filter
            .count()
            .run(conn)
        )

        data = list(
            base_filter
            .merge(query_merge)
            .merge(agent_merge_count)
            .pluck(self.keys_to_pluck)
            .order_by(self.sort(self.sort_key))
            .skip(self.offset)
            .limit(self.count)
            .run(conn)
        )

        return(count, data)

    @time_it
    @catch_it((0, []))
    @db_create_close
    def by_key_val(self, key, val, conn=None):
        """Retrieve all tags by filtering by key and value.
        Basic Usage:
            >>> from vFense.core.tag.search._db import FetchTags
            >>> search_tags = FetchTags(view_name='default')
            >>> search_tags.by_key_val('environment', 'Development')

        Returns:
            List of dictionairies.
        """
        count = 0
        data = []
        base_filter = self._set_base_query()
        query_merge = self._set_merge_query()
        agent_merge_count = self._set_agent_merge_count()
        count = (
            base_filter
            .filter(
                {
                    key: val
                }
            )
            .count()
            .run(conn)
        )

        data = list(
            base_filter
            .filter(
                {
                    key: val
                }
            )
            .merge(query_merge)
            .merge(agent_merge_count)
            .pluck(self.keys_to_pluck)
            .order_by(self.sort(self.sort_key))
            .skip(self.offset)
            .limit(self.count)
            .run(conn)
        )

        return(count, data)

    @time_it
    @catch_it((0, []))
    @db_create_close
    def by_key_val_and_query(self, key, val, query, conn=None):
        """Retrieve all tags by filtering by key and value while
            searching by name.
        Basic Usage:
            >>> from vFense.core.tag.search._db import FetchTags
            >>> search_tags = FetchTags(view_name='default')
            >>> search_tags.by_key_val(
                'environment', 'Development', 'Test'
            )

        Returns:
            List of dictionairies.
        """
        count = 0
        data = []
        agent_merge_count = self._set_agent_merge_count()
        base_filter = self._set_base_query()
        query_merge = self._set_merge_query()
        count = (
            base_filter
            .filter(
                {
                    key: val
                }
            )
            .filter(r.row[TagKeys.TagName].match("(?i)^"+query))
            .count()
            .run(conn)
        )

        data = list(
            base_filter
            .filter(
                {
                    key: val
                }
            )
            .filter(r.row[TagKeys.TagName].match("(?i)^"+query))
            .merge(query_merge)
            .merge(agent_merge_count)
            .pluck(self.keys_to_pluck)
            .order_by(self.sort(self.sort_key))
            .skip(self.offset)
            .limit(self.count)
            .run(conn)
        )

        return(count, data)

    def _set_agent_merge_count(self):
        merge_query = (
            lambda x:
            {
                AgentCollections.Agents: (
                    r
                    .table(TagCollections.TagsPerAgent)
                    .get_all(
                        x[TagsPerAgentKeys.TagId],
                        index=TagsPerAgentIndexes.TagId
                    )
                    .count()
                )
            }
        )
        return merge_query


    def _set_agent_merge_query(self, tag_id):
        merge_query = (
            lambda x:
            {
                AgentCollections.Agents: (
                    r
                    .table(TagCollections.TagsPerAgent)
                    .get_all(
                        tag_id,
                        index=TagsPerAgentIndexes.TagId
                    )
                    .pluck(TagsPerAgentKeys.AgentId)
                    .eq_join(
                        TagsPerAgentKeys.AgentId,
                        r.table(AgentCollections.Agents)
                    )
                    .map(
                        lambda y:
                        {
                            TagsPerAgentKeys.AgentId: (
                                y['right'][TagsPerAgentKeys.AgentId]
                            ),
                            AgentKeys.ComputerName: (
                                y['right'][AgentKeys.ComputerName]
                            ),
                            AgentKeys.LastAgentUpdate: (
                                y['right'][AgentKeys.LastAgentUpdate]
                                .to_epoch_time()
                            ),
                            AgentKeys.DisplayName: (
                                y['right'][AgentKeys.DisplayName]
                            )
                        }
                    )
                    .coerce_to('array')
                )
            }
        )
        return merge_query

    def _set_tag_merge_query(self, tag_id):
        merge_query = (
            lambda x:
            {
                CommonAppKeys.APP_STATS: (
                    [
                        {
                            CommonAppKeys.COUNT: (
                                r
                                .table(TagCollections.TagsPerAgent)
                                .get_all(
                                    tag_id,
                                    index=TagsPerAgentIndexes.TagId
                                )
                                .pluck(TagsPerAgentKeys.AgentId)
                                .eq_join(
                                    TagsPerAgentKeys.AgentId,
                                    r.table(AgentCollections.Agents)
                                )
                                .eq_join(
                                    lambda y:
                                    [
                                        CommonAppKeys.INSTALLED,
                                        y['right'][AgentKeys.AgentId]
                                    ],
                                    r.table(AppCollections.AppsPerAgent),
                                    index=AppsPerAgentIndexes.StatusAndAgentId
                                )
                                .count()
                            ),
                            CommonAppKeys.STATUS: CommonAppKeys.INSTALLED,
                            CommonAppKeys.NAME: CommonAppKeys.SOFTWAREINVENTORY
                        },
                        {
                            CommonAppKeys.COUNT: (
                                r
                                .table(TagCollections.TagsPerAgent)
                                .get_all(
                                    tag_id,
                                    index=TagsPerAgentIndexes.TagId
                                )
                                .pluck(TagsPerAgentKeys.AgentId)
                                .eq_join(
                                    TagsPerAgentKeys.AgentId,
                                    r.table(AgentCollections.Agents)
                                )
                                .eq_join(
                                    lambda y:
                                    [
                                        CommonAppKeys.AVAILABLE,
                                        y['right'][AgentKeys.AgentId]
                                    ],
                                    r.table(AppCollections.AppsPerAgent),
                                    index=AppsPerAgentIndexes.StatusAndAgentId
                                )
                                .count()
                            ),
                            CommonAppKeys.STATUS: CommonAppKeys.AVAILABLE,
                            CommonAppKeys.NAME: CommonAppKeys.OS
                        },
                        {
                            CommonAppKeys.COUNT: (
                                r
                                .table(TagCollections.TagsPerAgent)
                                .get_all(
                                    tag_id,
                                    index=TagsPerAgentIndexes.TagId
                                )
                                .pluck(TagsPerAgentKeys.AgentId)
                                .eq_join(
                                    TagsPerAgentKeys.AgentId,
                                    r.table(AgentCollections.Agents)
                                )
                                .eq_join(
                                    lambda y:
                                    [
                                        CommonAppKeys.AVAILABLE,
                                        y['right'][AgentKeys.AgentId]
                                    ],
                                    r.table(AppCollections.CustomAppsPerAgent),
                                    index=AppsPerAgentIndexes.StatusAndAgentId
                                )
                                .count()
                            ),
                            CommonAppKeys.STATUS: CommonAppKeys.AVAILABLE,
                            CommonAppKeys.NAME: CommonAppKeys.CUSTOM
                        },
                        {
                            CommonAppKeys.COUNT: (
                                r
                                .table(TagCollections.TagsPerAgent)
                                .get_all(
                                    tag_id,
                                    index=TagsPerAgentIndexes.TagId
                                )
                                .pluck(TagsPerAgentKeys.AgentId)
                                .eq_join(
                                    TagsPerAgentKeys.AgentId,
                                    r.table(AgentCollections.Agents)
                                )
                                .eq_join(
                                    lambda y:
                                    [
                                        CommonAppKeys.AVAILABLE,
                                        y['right'][AgentKeys.AgentId]
                                    ],
                                    r.table(AppCollections.SupportedAppsPerAgent),
                                    index=AppsPerAgentIndexes.StatusAndAgentId
                                )
                                .count()
                            ),
                            CommonAppKeys.STATUS: CommonAppKeys.AVAILABLE,
                            CommonAppKeys.NAME: CommonAppKeys.SUPPORTED
                        },
                        {
                            CommonAppKeys.COUNT: (
                                r
                                .table(TagCollections.TagsPerAgent)
                                .get_all(
                                    tag_id,
                                    index=TagsPerAgentIndexes.TagId
                                )
                                .pluck(TagsPerAgentKeys.AgentId)
                                .eq_join(
                                    TagsPerAgentKeys.AgentId,
                                    r.table(AgentCollections.Agents)
                                )
                                .eq_join(
                                    lambda y:
                                    [
                                        CommonAppKeys.AVAILABLE,
                                        y['right'][AgentKeys.AgentId]
                                    ],
                                    r.table(AppCollections.vFenseAppsPerAgent),
                                    index=AppsPerAgentIndexes.StatusAndAgentId
                                )
                                .count()
                            ),
                            CommonAppKeys.STATUS: CommonAppKeys.AVAILABLE,
                            CommonAppKeys.NAME: CommonAppKeys.AGENT_UPDATES
                        },
                    ]
                ),
            }
        )

        return merge_query

    def _set_merge_query(self):
        merge_query = (
            lambda x:
            {
                AgentCommonKeys.AVAIL_UPDATES: (
                    r
                    .table(TagCollections.TagsPerAgent)
                    .get_all(
                        x[TagsPerAgentKeys.TagId],
                        index=TagsPerAgentIndexes.TagId
                    )
                    .pluck(TagsPerAgentKeys.AgentId)
                    .eq_join(
                        lambda x: [
                            CommonAppKeys.AVAILABLE,
                            x[TagsPerAgentKeys.AgentId]
                        ],
                        r.table(AppCollections.AppsPerAgent),
                        index=AppsPerAgentIndexes.StatusAndAgentId
                    )
                    .count()
                ),
                AgentCommonKeys.AVAIL_VULN: (
                    r
                    .table(TagCollections.TagsPerAgent)
                    .get_all(
                        x[TagsPerAgentKeys.TagId],
                        index=TagsPerAgentIndexes.TagId
                    )
                    .pluck(TagsPerAgentKeys.AgentId)
                    .eq_join(
                        lambda x: [
                            CommonAppKeys.AVAILABLE,
                            x[TagsPerAgentKeys.AgentId]
                        ],
                        r.table(AppCollections.AppsPerAgent),
                        index=AppsPerAgentIndexes.StatusAndAgentId
                    )
                    .eq_join(
                        lambda y:
                        y['right'][AppsKey.AppId],
                        r.table(AppCollections.UniqueApplications)
                    )
                    .filter(
                        lambda z:
                        z['right'][AppsKey.VulnerabilityId] != ''
                    )
                    .count()
                ),
            }
        )

        return merge_query

    def _set_base_query(self):
        base_filter = (
            r
            .table(TagCollections.Tags)
        )
        if self.view_name:
            base_filter = (
                r
                .table(TagCollections.Tags)
                .get_all(
                    self.view_name,
                    index=TagKeys.ViewName
                )
            )

        return base_filter
