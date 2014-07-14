import logging

from vFense import VFENSE_LOGGING_CONFIG
from vFense.core._constants import SortValues, DefaultQueryValues
from vFense.result._constants import ApiResultKeys

from vFense.core.agent._constants import AgentCommonKeys
from vFense.core.view._constants import DefaultViews
from vFense.core.tag._db_model import TagKeys

from vFense.core.tag.search._db import FetchTags
from vFense.core.decorators import time_it
from vFense.core.status_codes import GenericCodes, GenericFailureCodes

logging.config.fileConfig(VFENSE_LOGGING_CONFIG)
logger = logging.getLogger('rvapi')


class RetrieveTags(object):
    def __init__(
        self, view_name=None,
        count=DefaultQueryValues.COUNT,
        offset=DefaultQueryValues.OFFSET,
        sort=SortValues.ASC,
        sort_key=TagKeys.TagName
        ):

        self.view_name = view_name
        self.count = count
        self.offset = offset
        self.sort = sort


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
        if sort_key in valid_keys_to_sort_by:
            self.sort_key = sort_key
        else:
            self.sort_key = TagKeys.TagName

        if self.view_name == DefaultViews.GLOBAL:
            self.view_name = None

        self.fetch_tags = (
            FetchTags(
                self.view_name, self.count, self.offset,
                self.sort, self.sort_key
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
        generic_status_code = GenericCodes.InformationRetrieved

        if count == 0:
            vfense_status_code = GenericFailureCodes.DataIsEmpty
            msg = 'dataset is empty'

        else:
            vfense_status_code = GenericCodes.InformationRetrieved
            msg = 'dataset retrieved'

        results = (
            self._set_results(
                generic_status_code, vfense_status_code,
                msg, count, data
            )
        )

        return(results)


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
        generic_status_code = GenericCodes.InformationRetrieved

        if count == 0:
            vfense_status_code = GenericFailureCodes.DataIsEmpty
            msg = 'dataset is empty'

        else:
            vfense_status_code = GenericCodes.InformationRetrieved
            msg = 'dataset retrieved'

        results = (
            self._set_results(
                generic_status_code, vfense_status_code,
                msg, count, data
            )
        )

        return(results)

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
        generic_status_code = GenericCodes.InformationRetrieved

        if count == 0:
            vfense_status_code = GenericFailureCodes.DataIsEmpty
            msg = 'dataset is empty'

        else:
            vfense_status_code = GenericCodes.InformationRetrieved
            msg = 'dataset retrieved'

        results = (
            self._set_results(
                generic_status_code, vfense_status_code,
                msg, count, data
            )
        )

        return(results)

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
        generic_status_code = GenericCodes.InformationRetrieved

        if count == 0:
            vfense_status_code = GenericFailureCodes.DataIsEmpty
            msg = 'dataset is empty'

        else:
            vfense_status_code = GenericCodes.InformationRetrieved
            msg = 'dataset retrieved'

        results = (
            self._set_results(
                generic_status_code, vfense_status_code,
                msg, count, data
            )
        )

        return(results)


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

            if count == 0:
                generic_status_code = GenericCodes.InformationRetrieved
                vfense_status_code = GenericFailureCodes.DataIsEmpty
                msg = 'dataset is empty'

            else:
                generic_status_code = GenericCodes.InformationRetrieved
                vfense_status_code = GenericCodes.InformationRetrieved
                msg = 'dataset retrieved'

        else:
            generic_status_code = GenericFailureCodes.FailedToRetrieveObject
            vfense_status_code = GenericFailureCodes.InvalidFilterKey

        results = (
            self._set_results(
                generic_status_code, vfense_status_code,
                msg, count, data
            )
        )

        return(results)


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
                self.fetch_tags.by_key_val_and_query(
                    key, val, query
                )
            )

            if count == 0:
                generic_status_code = GenericCodes.InformationRetrieved
                vfense_status_code = GenericFailureCodes.DataIsEmpty
                msg = 'dataset is empty'

            else:
                generic_status_code = GenericCodes.InformationRetrieved
                vfense_status_code = GenericCodes.InformationRetrieved
                msg = 'dataset retrieved'

        else:
            generic_status_code = GenericFailureCodes.FailedToRetrieveObject
            vfense_status_code = GenericFailureCodes.InvalidFilterKey

        results = (
            self._set_results(
                generic_status_code, vfense_status_code,
                msg, count, data
            )
        )

        return(results)

    def _set_results(self, gen_status_code, vfense_status_code,
                     msg, count, data):

        results = {
            ApiResultKeys.GENERIC_STATUS_CODE: gen_status_code,
            ApiResultKeys.VFENSE_STATUS_CODE: vfense_status_code,
            ApiResultKeys.MESSAGE: msg,
            ApiResultKeys.COUNT: count,
            ApiResultKeys.DATA: data,
        }

        return(results)
