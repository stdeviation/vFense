from time import time
import logging
import logging.config
from vFense import VFENSE_LOGGING_CONFIG

from vFense.core.decorators import time_it
from vFense.core.agent.agents import validate_agent_ids
from vFense.core.agent.status_codes import (
    AgentFailureCodes
)
from vFense.core.tag import Tag
from vFense.core.tag._db import (
    fetch_tag, insert_tag, add_agents_to_tag, delete_agent_ids_from_tag,
    delete_tag, fetch_agent_ids_in_tag, fetch_tag_by_name_and_view,
    update_tag
)
from vFense.core.view.views import validate_view_names
from vFense.core.results import ApiResults
from vFense.core.status_codes import (
    DbCodes, GenericCodes, GenericFailureCodes,
)
from vFense.core.tag.status_codes import (
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
        if self.tag_id:
            data = fetch_tag(self.tag_id)
            if data:
                tag = Tag(**data)
            else:
                tag = Tag()
        else:
            tag = Tag()
        return tag

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
            data = fetch_tag(self.tag_id)
            if data:
                tag = Tag(**data)
                tag_key = tag.to_dict().get(tag_attribute, None)

        return tag_key

    def get_agents(self):
        if self.tag_id:
            agents = fetch_agent_ids_in_tag(self.tag_id)
        else:
            agents = []
        return agents


    @time_it
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
            ApiResults instance
        """
        results = ApiResults()
        results.fill_in_defaults()
        if isinstance(tag, Tag):
            invalid_fields = tag.get_invalid_fields()
            tag.fill_in_defaults()
            views_are_validated, valid_view_names, invalid_view_names = (
                validate_view_names([tag.view_name])
            )
            tag_exist_for_view = (
                fetch_tag_by_name_and_view(tag.tag_name, tag.view_name)
            )
            if (views_are_validated and not invalid_fields and
                    not tag_exist_for_view):
                status_code, _, _, generated_ids = (
                    insert_tag(tag.to_dict_db())
                )
                if status_code == DbCodes.Inserted:
                    self.tag_id = generated_ids.pop()
                    tag.tag_id = self.tag_id
                    self.properties = self._tag_attributes()
                    #Add agents to this tag, if Agents exist
                    if tag.agents:
                        self.add_agents(tag.agents)

                    msg = (
                        'Tag {0} created successfully, tag id: {1}'
                        .format(tag.tag_name, self.tag_id)
                    )
                    results.generic_status_code = GenericCodes.ObjectCreated
                    results.vfense_status_code = TagCodes.TagCreated
                    results.message = msg
                    results.data.append(tag.to_dict())
                    results.generated_ids.append(self.tag_id)

                else:
                    msg = 'Failed to create tag {0}.'.format(tag.tag_name)
                    results.generic_status_code = (
                        GenericFailureCodes.FailedToCreateObject
                    )
                    results.vfense_status_code = (
                        TagFailureCodes.FailedToCreateTag
                    )
                    results.message = msg
                    results.data.append(tag.to_dict())

            elif invalid_fields:
                msg = (
                    'Failed to create tag {0}, invalid fields were passed.'
                    .format(tag.tag_name)
                )
                results.generic_status_code = (
                    GenericFailureCodes.FailedToCreateObject
                )
                results.vfense_status_code = TagFailureCodes.FailedToCreateTag
                results.errors = invalid_fields
                results.message = msg
                results.data.append(tag.to_dict())

            elif tag_exist_for_view:
                msg = (
                    'Tag {0} already exist in view {1}.'
                    .format(tag.tag_name, tag.view_name)
                )
                results.generic_status_code = (
                    GenericFailureCodes.FailedToCreateObject
                )
                results.vfense_status_code = TagFailureCodes.FailedToCreateTag
                results.errors = invalid_fields
                results.message = msg
                results.data.append(tag.to_dict())

            else:
                msg = (
                    'Failed to create tag {0}, invalid views were passed.'
                    .format(tag.tag_name)
                )
                results.generic_status_code = (
                    GenericFailureCodes.FailedToCreateObject
                )
                results.vfense_status_code = TagFailureCodes.FailedToCreateTag
                results.message = msg
                results.data.append(tag.to_dict())
                results.errors = invalid_view_names

        else:
            msg = (
                'Invalid {0} Instance, must pass an instance of tag.'
                .format(type(tag))
            )
            results.generic_status_code = (
                GenericFailureCodes.FailedToCreateObject
            )
            results.vfense_status_code = TagFailureCodes.FailedToCreateTag
            results.message = msg

        return results

    @time_it
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
            ApiResults instance
        """
        results = ApiResults()
        results.fill_in_defaults()
        tag_data = []
        if self.properties.tag_id:
            tag_name = self.properties.tag_name
            agents_are_valid, valid_agents, invalid_agents = (False, [], [])
            is_global = self.properties.is_global
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
                    tag = Tag()
                    tag.tag_id = self.tag_id
                    tag.agent_id = agent_id
                    tag.tag_name = tag_name
                    tag.view_name = self.properties.view_name
                    tag_data.append(tag.to_dict_per_agent())

                status_code, _, _, _ = add_agents_to_tag(tag_data)
                if status_code == DbCodes.Inserted:
                    self.properties = self._tag_attributes()
                    self.agents = self.get_agents()
                    msg = (
                        'Agent ids were added successfully to tag {0}:{1}'
                        .format(self.tag_id, self.properties.tag_name)
                    )
                    results.generic_status_code = GenericCodes.ObjectCreated
                    results.vfense_status_code = TagCodes.AgentsAddedToTag
                    results.message = msg
                    results.data = agent_ids
                    results.updated_ids.append(self.tag_id)

                else:
                    msg = (
                        'Failed to add agents to tag {0}:{1}.'
                        .format(self.tag_id, self.properties.tag_name)
                    )
                    results.generic_status_code = (
                        GenericFailureCodes.FailedToCreateObject
                    )
                    results.vfense_status_code = (
                        TagFailureCodes.FailedToAddAgentsToTag
                    )
                    results.message = msg
                    results.data = agent_ids
                    results.unchanged_ids.append(self.tag_id)

            elif agents_exist_in_tag:
                msg = (
                    'Some of the agent ids already exist for tag {0}:{1}.'
                    .format(self.tag_id, self.properties.tag_name)
                )
                results.generic_status_code = GenericFailureCodes.InvalidId
                results.vfense_status_code = GenericFailureCodes.InvalidId
                results.message = msg
                results.data = agent_ids

            else:
                msg = (
                    'Invalid agent ids were passed, for this tag {0}:{1}'
                    .format(self.tag_id, self.properties.tag_name)
                )
                results.generic_status_code = GenericFailureCodes.InvalidId
                results.vfense_status_code = GenericFailureCodes.InvalidId
                results.message = msg
                results.data = invalid_agents
                results.unchanged_ids.append(self.tag_id)

        else:
            msg = (
                'Tag id {0} does not exist.'.format(self.tag_id)
            )
            results.generic_status_code = GenericFailureCodes.InvalidId
            results.vfense_status_code = GenericFailureCodes.InvalidId
            results.message = msg
            results.data = agent_ids
            results.unchanged_ids.append(self.tag_id)

        return results

    @time_it
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
            ApiResults instance
        """
        results = ApiResults()
        results.fill_in_defaults()
        if self.properties.tag_id:
            status_code, _, _, _ = (
                delete_tag(self.tag_id)
            )
            if status_code == DbCodes.Deleted:
                delete_agent_ids_from_tag(self.tag_id)
                msg = (
                    'Tag {0}:{1} removed successfully'
                    .format(self.tag_id, self.properties.tag_name)
                )
                results.generic_status_code = GenericCodes.ObjectDeleted
                results.vfense_status_code = TagCodes.TagRemoved
                results.message = msg
                results.deleted_ids.append(self.tag_id)
                self.properties = Tag()

            else:
                msg = (
                    'Tag id {0} does not exist.'.format(self.tag_id)
                )
                results.generic_status_code = GenericFailureCodes.InvalidId
                results.vfense_status_code = GenericFailureCodes.InvalidId
                results.message = msg
                results.unchanged_ids.append(self.tag_id)

        else:
            msg = (
                'Tag id {0} does not exist.'.format(self.tag_id)
            )
            results.generic_status_code = GenericFailureCodes.InvalidId
            results.vfense_status_code = GenericFailureCodes.InvalidId
            results.message = msg
            results.unchanged_ids.append(self.tag_id)

        return results

    @time_it
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
            ApiResults instanace
        """
        results = ApiResults()
        results.fill_in_defaults()
        if self.properties.tag_id:
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
                        'Agents were removed successfully from tag {0}:{1}'
                        .format(self.tag_id, self.properties.tag_name)
                    )
                    results.generic_status_code = GenericCodes.ObjectDeleted
                    results.vfense_status_code = TagCodes.AgentsRemovedFromTag
                    results.message = msg
                    results.data = agent_ids
                    results.updated_ids.append(self.tag_id)

                else:
                    msg = (
                        'Failed to remove agents from tag {0}:{1}.'
                        .format(self.tag_id, self.properties.tag_name)
                    )
                    results.generic_status_code = (
                        GenericFailureCodes.FailedToDeleteObject
                    )
                    results.vfense_status_code = (
                        TagFailureCodes.FailedToRemoveAgentsFromTag
                    )
                    results.message = msg
                    results.data = agent_ids
                    results.unchanged_ids.append(self.tag_id)

            else:
                msg = (
                    'Invalid agent ids were passed for tag {0}:{1}'
                    .format(self.tag_id, self.properties.tag_name)
                )
                results.generic_status_code = GenericFailureCodes.InvalidId
                results.vfense_status_code = GenericFailureCodes.InvalidId
                results.message = msg
                results.data = agent_ids
                results.unchanged_ids.append(self.tag_id)

        else:
            msg = (
                'Tag id {0} does not exist.'.format(self.tag_id)
            )
            results.generic_status_code = GenericFailureCodes.InvalidId
            results.vfense_status_code = GenericFailureCodes.InvalidId
            results.message = msg
            results.unchanged_ids.append(self.tag_id)

        return results

    @time_it
    def edit_environment(self, environment):
        """Change the environment to which this tag belongs too.
        Args:
            environment (str): The environment name.

        Basic Usage:
            >>> from vFense.tag.manager import TagManager
            >>> tag_id = 'cac3f82c-d320-4e6f-9ee7-e28b1f527d76'
            >>> manager = TagManager(tag_id)
            >>> manager.edit_environment('Development')

        Returns:
            ApiResults instance
        """
        tag = Tag(environment=environment)
        results = self.__edit_properties(tag)
        return results

    @time_it
    def __edit_properties(self, tag):
        """ Edit the properties of this tag.
        Args:
            tag (Tag): The Tag instance with all of its properties.

        Basic Usage:
            >>> from vFense.tag import Tag
            >>> from vFense.tag.manager import TagManager
            >>> tag_id = 'cac3f82c-d320-4e6f-9ee7-e28b1f527d76'
            >>> tag = Tag(environment='Staging')
            >>> manager = TagManager(tag_id)
            >>> manager.__edit_properties(tag)

        Return:
            ApiResults instance
        """
        results = ApiResults()
        results.fill_in_defaults()
        if self.properties.tag_id and isinstance(tag, Tag):
            invalid_fields = tag.get_invalid_fields()
            if not invalid_fields:
                tag.date_modified = time()
                object_status, _, _, _ = (
                    update_tag(self.tag_id, tag.to_dict_db_update())
                )
                if object_status == DbCodes.Replaced:
                    msg = (
                        'Tag {0}:{1} was updated.'
                        .format(self.tag_id, self.properties.tag_name)
                    )
                    generic_status_code = GenericCodes.ObjectUpdated
                    vfense_status_code = TagCodes.TagUpdated
                    results.updated_ids.append(self.tag_id)
                    results.data.append(tag.to_dict_non_null())

                elif object_status == DbCodes.Unchanged:
                    msg = (
                        'Tag {0}:{1} was not updated'
                        .format(self.tag_id, self.properties.tag_name)
                    )
                    generic_status_code = GenericCodes.ObjectUnchanged
                    vfense_status_code = TagCodes.TagUnchanged
                    results.data.append(tag.to_dict_non_null())
                    results.unchanged_ids.append(self.tag_id)

            else:
                generic_status_code = GenericCodes.InvalidId
                vfense_status_code = TagFailureCodes.FailedToUpdateTag
                msg = (
                    'Tag {0}:{1} properties were invalid.'
                    .format(self.tag_id, self.properties.tag_name)
                )
                results.unchanged_ids.append(self.tag_id)
                results.data.append(tag.to_dict_non_null())
                results.errors = invalid_fields

        elif not isinstance(tag, Tag):
            generic_status_code = GenericCodes.InvalidId
            vfense_status_code = GenericFailureCodes.InvalidInstanceType
            msg = (
                'Tag {0} is not of instance Tag., instanced passed {1}'
                .format(self.tag_id, type(tag))
            )
            results.unchanged_ids.append(self.tag_id)

        else:
            generic_status_code = GenericCodes.InvalidId
            vfense_status_code = AgentFailureCodes.TagIdDoesNotExist
            msg = 'Tag %s does not exist - ' % (self.tag_id)
            results.unchanged_ids.append(self.tag_id)

        results.generic_status_code = generic_status_code
        results.vfense_status_code = vfense_status_code
        results.message = msg

        return results

