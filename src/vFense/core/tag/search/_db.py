import logging

from vFense import VFENSE_LOGGING_CONFIG
from vFense.db.client import db_create_close, r
from vFense.core._constants import SortValues, DefaultQueryValues
from vFense.core.agent._constants import AgentCommonKeys
from vFense.core.agent._db_model import (
    AgentKeys, AgentCollections,
    HardwarePerAgentIndexes, HardwarePerAgentKeys
)
from vFense.core.tag._db_model import (
    TagCollections, TagKeys, TagsPerAgentKeys, TagsPerAgentIndexes
)
from vFense.plugins.patching._db_model import (
    AppCollections, AppsKey, AppsPerAgentIndexes
)
from vFense.plugins.patching._db_model import *
from vFense.plugins.patching._constants import CommonAppKeys
from vFense.core.decorators import time_it

logging.config.fileConfig(VFENSE_LOGGING_CONFIG)
logger = logging.getLogger('rvapi')


class FetchTags(object):
    """Tag database queries"""
    def __init__(
        self, view_name=None,
        count=DefaultQueryValues.COUNT,
        offset=DefaultQueryValues.OFFSET,
        sort=SortValues.ASC,
        sort_key=TagKeys.TagName
        ):
        """
        Kwargs:
            view_name (str): Fetch all agents in this view.
            count (int): The number of results to return.
            offset (int): The next set of results beginning at offset.
            sort (str): asc or desc.
            sort_key (str): The key you are going to sort the results by.
        """

        self.view_name = view_name
        self.count = count
        self.offset = offset
        self.sort_key = sort_key

        self.keys_to_pluck = [
            TagKeys.TagName, TagKeys.TagId, TagKeys.ViewName,
            TagKeys.ProductionLevel, AgentCommonKeys.AVAIL_UPDATES,
            AgentCommonKeys.AVAIL_VULN,
        ]

        if sort == SortValues.ASC:
            self.sort = r.asc
        else:
            self.sort = r.desc

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
        merge_query = self._set_merge_query()

        try:
            count = (
                base_filter
                .get_all(tag_id)
                .count()
                .run(conn)
            )

            data = list(
                base_filter
                .get_all(tag_id)
                .order_by(self.sort(self.sort_key))
                .skip(self.offset)
                .limit(self.count)
                .merge(agent_merge_query)
                .merge(merge_query)
                .run(conn)
            )

        except Exception as e:
            logger.exception(e)

        return(count, data)


    @time_it
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
        try:
            base_filter = self._set_base_query()
            count = (
                base_filter
                .filter(
                    r.row[TagKeys.TagName].match("(?i)^"+name)
                )
                .count()
                .run(conn)
            )

            data = list(
                base_filter
                .filter(
                    r.row[TagKeys.TagName].match("(?i)^"+name)
                )
                .merge(merge_query)
                .pluck(self.keys_to_pluck)
                .order_by(self.sort(self.sort_key))
                .skip(self.offset)
                .limit(self.count)
                .run(conn)
            )

        except Exception as e:
            logger.exception(e)

        return(count, data)

    @time_it
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
        try:
            base_filter = self._set_base_query()
            query_merge = self._set_merge_query()
            count = (
                base_filter
                .count()
                .run(conn)
            )

            data = list(
                base_filter
                .merge(query_merge)
                .pluck(self.keys_to_pluck)
                .order_by(self.sort(self.sort_key))
                .skip(self.offset)
                .limit(self.count)
                .run(conn)
            )

        except Exception as e:
            logger.exception(e)

        return(count, data)

    @time_it
    @db_create_close
    def by_key_val(self, key, val, conn=None):
        """Retrieve all tags by filtering by key and value.
        Basic Usage:
            >>> from vFense.core.tag.search._db import FetchTags
            >>> search_tags = FetchTags(view_name='default')
            >>> search_tags.by_key_val('production_level', 'Development')

        Returns:
            List of dictionairies.
        """
        count = 0
        data = []
        try:
            base_filter = self._set_base_query()
            query_merge = self._set_merge_query()
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
                .pluck(self.keys_to_pluck)
                .order_by(self.sort(self.sort_key))
                .skip(self.offset)
                .limit(self.count)
                .run(conn)
            )

        except Exception as e:
            logger.exception(e)

        return(count, data)

    @time_it
    @db_create_close
    def by_key_val_and_query(self, key, val, query, conn=None):
        """Retrieve all tags by filtering by key and value while
            searching by name.
        Basic Usage:
            >>> from vFense.core.tag.search._db import FetchTags
            >>> search_tags = FetchTags(view_name='default')
            >>> search_tags.by_key_val(
                'production_level', 'Development', 'Test'
            )

        Returns:
            List of dictionairies.
        """
        count = 0
        data = []
        try:
            base_filter = self._set_base_query()
            query_merge = self._set_merge_query()
            count = (
                base_filter
                .filter(
                    {
                        key: val
                    }
                )
                .filter(
                    r.row[TagKeys.TagName].match("(?i)^"+query)
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
                .filter(
                    r.row[TagKeys.TagName].match("(?i)^"+query)
                )
                .merge(query_merge)
                .pluck(self.keys_to_pluck)
                .order_by(self.sort(self.sort_key))
                .skip(self.offset)
                .limit(self.count)
                .run(conn)
            )

        except Exception as e:
            logger.exception(e)

        return(count, data)

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
                    .pluck(
                        x['right'][TagsPerAgentKeys.AgentId],
                        x['right'][AgentKeys.ComputerName],
                        x['right'][AgentKeys.LastAgentUpdate].to_epoch_time(),
                        x['right'][AgentKeys.DisplayName]
                    )
                    .coerce_to('array')
                )
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
                    .pluck(TagsPerAgentKeys.TagId)
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
                    .pluck(TagsPerAgentKeys.TagId)
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
                        z['left']['right'][AppsKey.VulnerabilityId] != ''
                    )
                    .count()
                ),
            }
        )

        return(merge_query)

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

        return(base_filter)

