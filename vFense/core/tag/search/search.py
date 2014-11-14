from vFense.core.agent._constants import AgentCommonKeys
from vFense.core.decorators import time_it
from vFense.core.tag._db_model import TagKeys
from vFense.core.tag.search._db import FetchTags
from vFense.search.base import RetrieveBase


class RetrieveTags(RetrieveBase):
    def __init__(self, sort_key=TagKeys.TagName, **kwargs):
        super(RetrieveTags, self).__init__(**kwargs)

        self.list_of_valid_keys = [
            TagKeys.TagName, TagKeys.ViewName,
            TagKeys.Environment, AgentCommonKeys.AVAIL_UPDATES,
            AgentCommonKeys.AVAIL_VULN,
        ]

        self.valid_keys_to_filter_by = (
            [
                TagKeys.ViewName,
                TagKeys.TagName,
                TagKeys.Environment
            ]
        )

        valid_keys_to_sort_by = (
            [
                TagKeys.ViewName,
                TagKeys.TagName,
                TagKeys.Environment,
                AgentCommonKeys.AVAIL_VULN,
                AgentCommonKeys.AVAIL_UPDATES,
            ]
        )
        if self.sort_key not in valid_keys_to_sort_by:
            self.sort_key = TagKeys.TagName

        self.fetch_tags = (
            FetchTags(
                view_name=self.view_name, count=self.count,
                offset=self.offset, sort=self.sort, sort_key=self.sort_key
            )
        )

    @time_it
    def by_id(self, tag_id):
        """Retrieve tag by id.
        Args:
            tag_id (str): 36 character UUID of the tag.

        Basic Usage:
            >>> from vFense.core.tag.search.search import RetrieveTags
            >>> view_name = 'default'
            >>> search_tags = RetrieveTags(view_name='default')
            >>> search_tags.by_id('45bbd659-cbdd-4669-9276-b226e31c7520')

        Returns:
            List of dictionairies.
        """
        count, data = self.fetch_tags.by_id(tag_id)
        return self._base(count, data)

    @time_it
    def by_name(self, query):
        """Query tags by tag name.
        Args:
            name (str): The regex you are searching by

        Basic Usage:
            >>> from vFense.core.tag.search.search import RetrieveTags
            >>> view_name = 'default'
            >>> search_tags = RetrieveTags(view_name='default')
            >>> search_tags.by_name('ubu')

        Returns:
            List of dictionairies.
        """
        count, data = self.fetch_tags.by_name(query)
        return self._base(count, data)

    @time_it
    def by_agent_id(self, agent_id):
        """Retrieve Tags for agent id.
        Args:
            agent_id (str): The 36 character UUID of the agent.

        Basic Usage:
            >>> from vFense.core.tag.search.search import RetrieveTags
            >>> view_name = 'default'
            >>> search_tags = RetrieveTags(view_name='default')
            >>> search_tags.by_agent_id('2155acc3-f7e7-4b51-90eb-415eee698a65')

        Returns:
            List of dictionairies.
        """
        count, data = self.fetch_tags.by_agent_id(agent_id)
        return self._base(count, data)

    @time_it
    def all(self):
        """Retrieve all agents.
        Basic Usage:
            >>> from vFense.core.agent.search.search import RetrieveAgents
            >>> view_name = 'default'
            >>> search_agents = RetrieveAgents(view_name='default')
            >>> search_agents.all()

        Returns:
            List of dictionairies.
        """
        count, data = self.fetch_tags.all()
        return self._base(count, data)

    @time_it
    def by_key_val(self, key, val):
        """Filter agents by a key and value.
        Args:
            key (str): The key you are filtering on.
            val (str): The value for the key you are filtering on.

        Basic Usage:
            >>> from vFense.core.tag.search.search import RetrieveTags
            >>> view_name = 'default'
            >>> key = 'environment'
            >>> val = 'Development'
            >>> search_tags = RetrieveTags(view_name='default')
            >>> search_tags.by_key_and_val(key, val)

        Returns:
            List of dictionairies.
        """
        count = 0
        data = []

        if key in self.valid_keys_to_filter_by:
            count, data = self.fetch_tags.by_key_val(key, val)
            return self._base(count, data)

        else:
            return self._set_results_invalid_filter_key(key)

    @time_it
    def by_key_val_and_query(self, key, val, query):
        """Filter tags based on a key and value, while searching for a tag.
        Args:
            fkey (str): The key you are filtering on.
            fval (str): The value for the key you are filtering on.

        Basic Usage:
            >>> from vFense.core.tag.search.search import RetrieveTags
            >>> view_name = 'default'
            >>> key = 'environment'
            >>> val = 'Development'
            >>> query = 'ubu'
            >>> search_tags = RetrieveTags(view_name='default')
            >>> search_tags.by_key_val_and_query(key, val, query)

        Returns:
            List of dictionairies.
        """
        count = 0
        data = []

        if key in self.valid_keys_to_filter_by:
            count, data = (
                self.fetch_tags.by_key_val_and_query(key, val, query)
            )
            return self._base(count, data)

        else:
            return self._set_results_invalid_filter_key(key)
