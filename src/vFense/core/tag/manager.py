from vFense.core.agent._db_model import *
import logging
import logging.config
from vFense import VFENSE_LOGGING_CONFIG

from vFense.core.agent.agents import validate_agent_ids_in_views
from vFense.core.tag import Tag
from vFense.core.tag._db import fetch_tag
from vFense.core.view.views import validate_view_names
from vFense.core.tag._db_model import TagKeys, TagMappedKeys
from vFense.errorz._constants import ApiResultKeys
from vFense.errorz.status_codes import (
    DbCodes, GenericCodes, GenericFailureCodes,
    TagFailureCodes, TagCodes
)

logging.config.fileConfig(VFENSE_LOGGING_CONFIG)
logger = logging.getLogger('rvapi')


class TagManager(object):
    def __init__(self, tag_id=None):
        self.tag_id = tag_id
        self.properties = self._tag_attributes()
        if self.properties:
            if self.properties.get(TagKeys.Agents):
                self.agents = (
                    map(
                        lambda x: x[AgentKeys.AgentId],
                        self.properties.get(TagKeys.Agents, [])
                    )
                )
            else:
                self.agents = []
        else:
            self.agents = []

    def _tag_attributes(self):
        tag_data = fetch_tag(self.tag_id)

        return tag_data

    def get_attribute(self, tag_attribute):
        tag_data = fetch_tag(self.tag_id)
        tag_key = None
        if tag_data:
            tag_key = tag_data.get(tag_attribute, None)

        return tag_key


    def create(self, tag):
        """Add a tag into vFense.
        Args:
            tag (Tag): An instance of Tag.

        Basic Usage:
            >>> from vFense.core.tag.manager import TagManager
            >>> from vFense.core.tag import Tag

        Returns:
            >>>
        """
        results = {}
        if isinstance(tag, Tag):
            tag.fill_in_defaults()
            tag_data = tag.to_dict()
            views_are_validated, valid_view_names, invalid_view_names = (
                validate_view_names([tag_data[TagKeys.ViewName]])
            )
            if views_are_validated:
                status_code, _, _, generated_ids = (
                    insert_tag(tag_data)
                )
                if status_code == DbCodes.Inserted:
                    self.tag_id = generated_ids.pop()
                    #Add agents to this tag, if Agents exist
                    if tag_data[TagMappedKeys.Agents]:
                        self.add_agents(tag_data[TagMappedKeys.Agents])

                    tag_data[TagKeys.TagId] = self.tag_id
                    msg = (
                        'Tag {0} created successfully, tag id: {1}'
                        .format(
                            tag_data[TagKeys.TagName], self.tag_id
                        )
                    )
                    results[ApiResultKeys.GENERIC_STATUS_CODE] = (
                        GenericCodes.ObjectCreated
                    )
                    results[ApiResultKeys.VFENSE_STATUS_CODE] = (
                        TagCodes.TagCreated
                    )
                    results[ApiResultKeys.MESSAGE] = msg
                    results[ApiResultKeys.DATA] = [tag_data]
                    results[ApiResultKeys.GENERATED_IDS] = [self.tag_id]

                else:
                    msg = (
                        'Failed to create tag {0}.'
                        .format(tag_data[TagKeys.TagName])
                    )
                    results[ApiResultKeys.GENERIC_STATUS_CODE] = (
                        GenericFailureCodes.FailedToCreateObject
                    )
                    results[ApiResultKeys.VFENSE_STATUS_CODE] = (
                        TagFailureCodes.FailedToCreateTag
                    )
                    results[ApiResultKeys.MESSAGE] = msg
                    results[ApiResultKeys.DATA] = tag_data

            else:
                msg = (
                    'Failed to create tag {0}, invalid views were passed: {1}.'
                    .format(
                        tag_data[TagKeys.TagName],
                        ', '.join(invalid_view_names)
                    )
                )
                results[ApiResultKeys.GENERIC_STATUS_CODE] = (
                    GenericFailureCodes.FailedToCreateObject
                )
                results[ApiResultKeys.VFENSE_STATUS_CODE] = (
                    TagFailureCodes.FailedToCreateTag
                )
                results[ApiResultKeys.MESSAGE] = msg
                results[ApiResultKeys.DATA] = tag_data

        else:
            msg = (
                'Invalid {0} Instance, must pass an instance of tag.'
                .format(type(tag))
            )
            results[ApiResultKeys.GENERIC_STATUS_CODE] = (
                GenericFailureCodes.FailedToCreateObject
            )
            results[ApiResultKeys.VFENSE_STATUS_CODE] = (
                TagFailureCodes.FailedToCreateTag
            )
            results[ApiResultKeys.MESSAGE] = msg

        return results

    def add_agents(self, agent_ids):
        """Add agents to this tag.
        Args:
            agent_ids (list): List of agent ids.

        Basic Usage:
            >>> from vFense.core.tag.manager import TagManager
            >>> from vFense.core.tag import Tag
            >>> agent_ids = ['agent_id']

        Returns:
            Dictionary
            >>>
        """
        results = {}
        tag_exist = self.properties
        tag_data = []
        if tag_exist:
            tag_name = tag_exist[TagKeys.TagName]
            agents_are_valid, invalid_agents = (False, [])
            is_global = tag_exist[TagKeys.Global]
            views = [tag_exist[TagKeys.ViewName]]
            if is_global:
                agents_are_valid = True

            else:
                agents_are_valid, _, invalid_agents = (
                    validate_agent_ids_in_views(agent_ids, views)
                )

            if agents_are_valid:
                for agent_id in agent_ids:
                    tag_data.append(
                        {
                            TagsPerAgentKeys.AgentId: agent_id,
                            TagsPerAgentKeys.TagId: self.tag_id,
                            TagsPerAgentKeys.TagName: tag_name,
                        }
                    )
                status_code, _, _, _ = add_agents_to_tag(tag_data)
                if status_code == DbCodes.Inserted:
                    self.properties = self._tag_attributes()
                    msg = (
                        'Agent ids {0} were added successfully to tag {1}'
                        .format(', '.join(agent_ids), self.tag_id)
                    )
                    results[ApiResultKeys.GENERIC_STATUS_CODE] = (
                        GenericCodes.ObjectCreated
                    )
                    results[ApiResultKeys.VFENSE_STATUS_CODE] = (
                        AgentCodes.TagsAddedToAgent
                   )
                    results[ApiResultKeys.MESSAGE] = msg
                    results[ApiResultKeys.DATA] = [tag_data]
                    results[ApiResultKeys.UPDATED_IDS] = [self.agent_id]

                else:
                    msg = (
                        'Failed to add tags: {0} to agent: {1}.'
                        .format(', '.join(tag_ids, self.agent_id))
                    )
                    results[ApiResultKeys.GENERIC_STATUS_CODE] = (
                        GenericFailureCodes.FailedToCreateObject
                    )
                    results[ApiResultKeys.VFENSE_STATUS_CODE] = (
                        AgentFailureCodes.FailedToAddTagsToAgent
                    )
                    results[ApiResultKeys.MESSAGE] = msg
                    results[ApiResultKeys.DATA] = [tag_data]
                    results[ApiResultKeys.UNCHANGED_IDS] = [self.agent_id]

            else:
                msg = (
                    'Invalid tag ids: {0}.'.format(', '.join(tag_ids))
                )
                results[ApiResultKeys.GENERIC_STATUS_CODE] = (
                    GenericFailureCodes.InvalidId
                )
                results[ApiResultKeys.VFENSE_STATUS_CODE] = (
                    GenericFailureCodes.InvalidId
                )
                results[ApiResultKeys.MESSAGE] = msg
                results[ApiResultKeys.UNCHANGED_IDS] = [self.agent_id]

        else:
            msg = (
                'Agent id {0} does not exist.'.format(self.agent_id)
            )
            results[ApiResultKeys.GENERIC_STATUS_CODE] = (
                GenericFailureCodes.InvalidId
            )
            results[ApiResultKeys.VFENSE_STATUS_CODE] = (
                GenericFailureCodes.InvalidId
            )
            results[ApiResultKeys.MESSAGE] = msg
            results[ApiResultKeys.UNCHANGED_IDS] = [self.agent_id]

        return results

    def remove(self):
        """Remove agents from this tag.
        Args:
            agent_ids (list): List of agent ids.

        Basic Usage:
            >>> from vFense.core.tag.manager import TagManager
            >>> from vFense.core.tag import Tag
            >>> agent_ids = ['agent_id']

        Returns:
            Dictionary
            >>>
        """
        results = {}
        tag_exist = self.properties
        if tag_exist:
            status_code, _, _, _ = (
                delete_tag(self.tag_id)
            )
            if status_code == DbCodes.Deleted:
                self.properties = self._tag_attributes()
                delete_agent_ids_from_tag(self.tag_id)
                msg = (
                    'Tag {0} removed successfully'.format(self.tag_id)
                )
                results[ApiResultKeys.GENERIC_STATUS_CODE] = (
                    GenericCodes.ObjectDeleted
                )
                results[ApiResultKeys.VFENSE_STATUS_CODE] = (
                    TagCodes.TagRemoved
                )
                results[ApiResultKeys.MESSAGE] = msg
                results[ApiResultKeys.UPDATED_IDS] = [self.tag_id]

            else:
                msg = (
                    'Tag id {0} does not exist.'.format(self.tag_id)
                )
                results[ApiResultKeys.GENERIC_STATUS_CODE] = (
                    GenericFailureCodes.InvalidId
                )
                results[ApiResultKeys.VFENSE_STATUS_CODE] = (
                    GenericFailureCodes.InvalidId
                )
                results[ApiResultKeys.MESSAGE] = msg
                results[ApiResultKeys.UNCHANGED_IDS] = [self.tag_id]

        else:
            msg = (
                'Tag id {0} does not exist.'.format(self.tag_id)
            )
            results[ApiResultKeys.GENERIC_STATUS_CODE] = (
                GenericFailureCodes.InvalidId
            )
            results[ApiResultKeys.VFENSE_STATUS_CODE] = (
                GenericFailureCodes.InvalidId
            )
            results[ApiResultKeys.MESSAGE] = msg
            results[ApiResultKeys.UNCHANGED_IDS] = [self.tag_id]

        return results


    def remove_agents(self, agent_ids):
        """Remove agents from this tag.
        Args:
            agent_ids (list): List of agent ids.

        Basic Usage:
            >>> from vFense.core.tag.manager import TagManager
            >>> from vFense.core.tag import Tag
            >>> agent_ids = ['agent_id']

        Returns:
            Dictionary
            >>>
        """
        results = {}
        tag_exist = self.properties
        if tag_exist:
            if set(agent_ids).issubset(self.agents):
                status_code, _, _, _ = (
                    delete_agent_ids_from_tag(agent_ids, self.tag_id)
                )
                if status_code == DbCodes.Deleted:
                    self.properties = self._tag_attributes()
                    msg = (
                        'Agent ids {0} were removed successfully from tag {1}'
                        .format(', '.join(agent_ids), self.tag_id)
                    )
                    results[ApiResultKeys.GENERIC_STATUS_CODE] = (
                        GenericCodes.ObjectDeleted
                    )
                    results[ApiResultKeys.VFENSE_STATUS_CODE] = (
                        TagCodes.AgentsRemovedFromTag
                   )
                    results[ApiResultKeys.MESSAGE] = msg
                    results[ApiResultKeys.UPDATED_IDS] = [self.tag_id]

                else:
                    msg = (
                        'Failed to remove agents: {0} from tag: {1}.'
                        .format(', '.join(agent_ids, self.tag_id))
                    )
                    results[ApiResultKeys.GENERIC_STATUS_CODE] = (
                        GenericFailureCodes.FailedToDeleteObject
                    )
                    results[ApiResultKeys.VFENSE_STATUS_CODE] = (
                        TagFailureCodes.FailedToRemoveAgentsFromTag
                    )
                    results[ApiResultKeys.MESSAGE] = msg
                    results[ApiResultKeys.UNCHANGED_IDS] = [self.tag_id]

            else:
                msg = (
                    'Invalid agent ids: {0}.'.format(', '.join(agent_ids))
                )
                results[ApiResultKeys.GENERIC_STATUS_CODE] = (
                    GenericFailureCodes.InvalidId
                )
                results[ApiResultKeys.VFENSE_STATUS_CODE] = (
                    GenericFailureCodes.InvalidId
                )
                results[ApiResultKeys.MESSAGE] = msg
                results[ApiResultKeys.UNCHANGED_IDS] = [self.tag_id]

        else:
            msg = (
                'Tag id {0} does not exist.'.format(self.tag_id)
            )
            results[ApiResultKeys.GENERIC_STATUS_CODE] = (
                GenericFailureCodes.InvalidId
            )
            results[ApiResultKeys.VFENSE_STATUS_CODE] = (
                GenericFailureCodes.InvalidId
            )
            results[ApiResultKeys.MESSAGE] = msg
            results[ApiResultKeys.UNCHANGED_IDS] = [self.tag_id]

        return results

