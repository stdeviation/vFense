from vFense.core.agent._db_model import *
import logging
import logging.config
from vFense import VFENSE_LOGGING_CONFIG

from vFense.core.agent.agents import validate_agent_ids
from vFense.core.tag import Tag
from vFense.core.tag._db import (
    fetch_tag, insert_tag, add_agents_to_tag, delete_agent_ids_from_tag,
    delete_tag, fetch_agent_ids_in_tag, fetch_tag_by_name_and_view
)
from vFense.core.view.views import validate_view_names
from vFense.core.tag._db_model import (
    TagKeys, TagMappedKeys, TagsPerAgentKeys
)
from vFense.result._constants import ApiResultKeys
from vFense.result.status_codes import (
    DbCodes, GenericCodes, GenericFailureCodes,
    TagFailureCodes, TagCodes
)

logging.config.fileConfig(VFENSE_LOGGING_CONFIG)
logger = logging.getLogger('rvapi')


class TagManager(object):
    """Manage anything related to this tag."""
    def __init__(self, tag_id=None):
        self.tag_id = tag_id
        self.properties = self._tag_attributes()
        self.agents = self.get_agents()

    def _tag_attributes(self):
        tag_data = {}
        if self.tag_id:
            tag_data = fetch_tag(self.tag_id)
        return tag_data

    def get_attribute(self, tag_attribute):
        """Retrieve an attribute for this tag.
        Args:
            trag_attribute (str): The name of the attribute you want.

        Basic Usage:
            >>> from vFense.core.tag.manager import TagManager
            >>> manager = TagManager('0842c4c0-94ab-4fe4-9346-3b59fa53c316')
            >>> manager.get_attribute('tag_name')

        Returns:
            String
            >>> u'Test Tag 1'
        """
        tag_key = None
        if self.tag_id:
            tag_data = fetch_tag(self.tag_id)
            if tag_data:
                tag_key = tag_data.get(tag_attribute, None)

        return tag_key

    def get_agents(self):
        if self.tag_id:
            agents = fetch_agent_ids_in_tag(self.tag_id)
        else:
            agents = []
        return agents


    def create(self, tag):
        """Add a tag into vFense.
        Args:
            tag (Tag): An instance of Tag.

        Basic Usage:
            >>> from vFense.core.tag.manager import TagManager
            >>> from vFense.core.tag import Tag
            >>> manager = TagManager()
            >>> tag = (
                Tag(
                    'Test Tag 1',
                    agents=['cac3f82c-d320-4e6f-9ee7-e28b1f527d76'],
                    is_global=True
                )
            )
            >>> manager.create(tag)

        Returns:
            >>>
                {
                    "data": [
                        {
                            "environment": "production",
                            "global": true,
                            "view_name": "global",
                            "tag_id": "0842c4c0-94ab-4fe4-9346-3b59fa53c316",
                            "tag_name": "Test Tag 1"
                        }
                    ],
                    "message": "Tag Test Tag 1 created successfully, tag id: 0842c4c0-94ab-4fe4-9346-3b59fa53c316",
                    "generated_ids": [
                        "0842c4c0-94ab-4fe4-9346-3b59fa53c316"
                    ],
                    "vfense_status_code": 4000,
                    "generic_status_code": 1010
                }
        """
        results = {}
        if isinstance(tag, Tag):
            invalid_fields = tag.get_invalid_fields()
            tag.fill_in_defaults()
            tag_data = tag.to_dict()
            views_are_validated, valid_view_names, invalid_view_names = (
                validate_view_names([tag_data[TagKeys.ViewName]])
            )
            tag_exist_for_view = (
                fetch_tag_by_name_and_view(tag.tag_name, tag.view_name)
            )
            if (views_are_validated and not invalid_fields and
                    not tag_exist_for_view):
                agents = tag_data.pop(TagMappedKeys.Agents)
                status_code, _, _, generated_ids = (
                    insert_tag(tag_data)
                )
                if status_code == DbCodes.Inserted:
                    self.tag_id = generated_ids.pop()
                    self.properties = self._tag_attributes()
                    #Add agents to this tag, if Agents exist
                    if agents:
                        self.add_agents(agents)

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

            elif invalid_fields:
                msg = (
                    'Failed to create tag {0}, invalid fields were passed.'
                    .format(tag_data[TagKeys.TagName])
                )
                results[ApiResultKeys.GENERIC_STATUS_CODE] = (
                    GenericFailureCodes.FailedToCreateObject
                )
                results[ApiResultKeys.VFENSE_STATUS_CODE] = (
                    TagFailureCodes.FailedToCreateTag
                )
                results[ApiResultKeys.ERRORS] = invalid_fields
                results[ApiResultKeys.MESSAGE] = msg
                results[ApiResultKeys.DATA] = tag_data

            elif tag_exist_for_view:
                msg = (
                    'Tag {0} already exist in view {1}.'
                    .format(
                        tag_data[TagKeys.TagName],
                        tag_data[TagKeys.ViewName]
                    )
                )
                results[ApiResultKeys.GENERIC_STATUS_CODE] = (
                    GenericFailureCodes.FailedToCreateObject
                )
                results[ApiResultKeys.VFENSE_STATUS_CODE] = (
                    TagFailureCodes.FailedToCreateTag
                )
                results[ApiResultKeys.ERRORS] = invalid_fields
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
            >>> manager = TagManager('0842c4c0-94ab-4fe4-9346-3b59fa53c316')
            >>> agent_ids = ['cac3f82c-d320-4e6f-9ee7-e28b1f527d76']
            >>> manager.add_agents(agent_ids)

        Returns:
            Dictionary
            >>>
            {
                "data": [
                    {
                        "tag_name": "Test Tag 1",
                        "agent_id": "cac3f82c-d320-4e6f-9ee7-e28b1f527d76",
                        "tag_id": "0842c4c0-94ab-4fe4-9346-3b59fa53c316"
                    }
                ],
                "message": "Agent ids cac3f82c-d320-4e6f-9ee7-e28b1f527d76 were added successfully to tag 0842c4c0-94ab-4fe4-9346-3b59fa53c316",
                "vfense_status_code": 4009,
                "updated_ids": [
                    "0842c4c0-94ab-4fe4-9346-3b59fa53c316"
                ],
                "generic_status_code": 1010
            }

        """
        results = {}
        tag_exist = self.properties
        tag_data = []
        if tag_exist:
            tag_name = tag_exist[TagKeys.TagName]
            agents_are_valid, valid_agents, invalid_agents = (False, [], [])
            is_global = tag_exist[TagKeys.Global]
            if is_global:
                agents_are_valid = True

            else:
                agents_are_valid, valid_agents, invalid_agents = (
                    validate_agent_ids(agent_ids)
                )
            agents_exist_in_tag = (
                bool(set(agent_ids).intersection(self.agents))
            )
            if agents_are_valid and not agents_exist_in_tag:
                for agent_id in agent_ids:
                    tag_data.append(
                        {
                            TagsPerAgentKeys.AgentId: agent_id,
                            TagsPerAgentKeys.TagId: self.tag_id,
                            TagsPerAgentKeys.TagName: tag_name,
                            TagsPerAgentKeys.ViewName: (
                                tag_exist[TagKeys.ViewName]
                            ),
                        }
                    )
                status_code, _, _, _ = add_agents_to_tag(tag_data)
                if status_code == DbCodes.Inserted:
                    self.properties = self._tag_attributes()
                    self.agents = self.get_agents()
                    msg = (
                        'Agent ids {0} were added successfully to tag {1}'
                        .format(', '.join(agent_ids), self.tag_id)
                    )
                    results[ApiResultKeys.GENERIC_STATUS_CODE] = (
                        GenericCodes.ObjectCreated
                    )
                    results[ApiResultKeys.VFENSE_STATUS_CODE] = (
                        TagCodes.AgentsAddedToTag
                   )
                    results[ApiResultKeys.MESSAGE] = msg
                    results[ApiResultKeys.DATA] = tag_data
                    results[ApiResultKeys.UPDATED_IDS] = [self.tag_id]

                else:
                    msg = (
                        'Failed to add agents: {0} to tag: {1}.'
                        .format(', '.join(agent_ids, self.tag_id))
                    )
                    results[ApiResultKeys.GENERIC_STATUS_CODE] = (
                        GenericFailureCodes.FailedToCreateObject
                    )
                    results[ApiResultKeys.VFENSE_STATUS_CODE] = (
                        TagFailureCodes.FailedToAddAgentsToTag
                    )
                    results[ApiResultKeys.MESSAGE] = msg
                    results[ApiResultKeys.DATA] = tag_data
                    results[ApiResultKeys.UNCHANGED_IDS] = [self.tag_id]

            elif agents_exist_in_tag:
                msg = (
                    'Some of the agent ids: {0} already exist for tag: {1}.'
                    .format(', '.join(agent_ids), self.tag_id)
                )
                results[ApiResultKeys.GENERIC_STATUS_CODE] = (
                    GenericFailureCodes.InvalidId
                )
                results[ApiResultKeys.VFENSE_STATUS_CODE] = (
                    GenericFailureCodes.InvalidId
                )
                results[ApiResultKeys.MESSAGE] = msg

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

    def remove(self):
        """Remove agents from this tag.
        Args:
            agent_ids (list): List of agent ids.

        Basic Usage:
            >>> from vFense.core.tag.manager import TagManager
            >>> from vFense.core.tag import Tag
            >>> manager = TagManager('f671467d-de69-474d-b3eb-86d7c55eb1f2')
            >>> manager.remove()

        Returns:
            Dictionary
            >>>
            {
                "message": "Tag f671467d-de69-474d-b3eb-86d7c55eb1f2 removed successfully",
                "vfense_status_code": 4001,
                "deleted_ids": [
                    "f671467d-de69-474d-b3eb-86d7c55eb1f2"
                ],
                "generic_status_code": 1012
            }
        """
        results = {}
        tag_exist = self.properties
        if tag_exist:
            status_code, _, _, _ = (
                delete_tag(self.tag_id)
            )
            if status_code == DbCodes.Deleted:
                delete_agent_ids_from_tag(self.tag_id)
                self.properties =  {}
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
                results[ApiResultKeys.DELETED_IDS] = [self.tag_id]

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
            >>> manager = TagManager('0842c4c0-94ab-4fe4-9346-3b59fa53c316')
            >>> agent_ids = ['cac3f82c-d320-4e6f-9ee7-e28b1f527d76']
            >>> manager.remove_agents(agent_ids)

        Returns:
            Dictionary
            >>>
            {
                "message": "Agent ids cac3f82c-d320-4e6f-9ee7-e28b1f527d76 were removed successfully from tag 0842c4c0-94ab-4fe4-9346-3b59fa53c316",
                "vfense_status_code": 4010,
                "updated_ids": [
                    "0842c4c0-94ab-4fe4-9346-3b59fa53c316"
                ],
                "generic_status_code": 1012
            }

        """
        results = {}
        tag_exist = self.properties
        if tag_exist:
            agents_exist_in_tag = (
                bool(set(agent_ids).intersection(self.agents))
            )
            if agents_exist_in_tag:
                status_code, _, _, _ = (
                    delete_agent_ids_from_tag(self.tag_id, agent_ids)
                )
                if status_code == DbCodes.Deleted:
                    self.properties = self._tag_attributes()
                    self.agents = self.get_agents()
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
                        .format(', '.join(agent_ids), self.tag_id)
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
