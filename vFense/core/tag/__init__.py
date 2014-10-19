from time import time
from vFense import Base
from vFense.core._db_constants import DbTime
from vFense.core.tag._db_model import (
    TagKeys, TagMappedKeys, TagsPerAgentKeys
)
from vFense.core.tag._constants import (
    TagDefaults
)
from vFense.core._constants import (
    CommonKeys
)
from vFense.core.results import ApiResultKeys
from vFense.core.status_codes import GenericCodes


class Tag(Base):
    """Used to represent an instance of a tag."""

    def __init__(self, tag_id=None, tag_name=None, environment=None,
                 view_name=None, is_global=None, agents=None, date_added=None,
                 date_modified=None, agent_id=None
                 ):
        """
        Kwargs:
            tag_id (str): The id of the tag
            tag_name (str): The name of the tag
            environment (str): User defined environment.
            view_name (str): The name of the view, this tag belongs too.
            is_global (bool): If this tag is a global tag. A global tag,
                is a tag that allows agents from any view to be a
                part of this tag.
            date_added (epoch_time): time in epoch.
            date_modified (epoch_time): time in epoch.
        """
        self.tag_id = tag_id
        self.tag_name = tag_name
        self.environment = environment
        self.view_name = view_name
        self.is_global = is_global
        self.agents = agents
        self.date_added = date_added
        self.date_modified = date_modified
        self.agent_id = agent_id


    def fill_in_defaults(self):
        """Replace all the fields that have None as their value with
        the hardcoded default values.
        """
        now = time()

        if not self.environment:
            self.environment = TagDefaults.ENVIRONMENT

        if not self.is_global:
            self.is_global = TagDefaults.IS_GLOBAL

        if self.is_global and not self.view_name:
            self.view_name = TagDefaults.VIEW_NAME

        if not self.agents:
            self.agents = TagDefaults.AGENTS

        if not self.date_added:
            self.date_added = now

        if not self.date_modified:
            self.date_modified = now

    def get_invalid_fields(self):
        """Check for invalid fields.
        Returns:
            List
        """
        invalid_fields = []

        if self.is_global:
            if not isinstance(self.is_global, bool):
                invalid_fields.append(
                    {
                        TagKeys.IsGlobal: self.is_global,
                        CommonKeys.REASON: 'Must be a boolean value',
                        ApiResultKeys.VFENSE_STATUS_CODE: (
                            GenericCodes.InvalidValue
                        )
                    }
                )

        if self.tag_name:
            if not isinstance(self.tag_name, basestring):
                invalid_fields.append(
                    {
                        TagKeys.TagName: self.tag_name,
                        CommonKeys.REASON: 'Must be a string',
                        ApiResultKeys.VFENSE_STATUS_CODE: (
                            GenericCodes.InvalidValue
                        )
                    }
                )

        if self.view_name:
            if not isinstance(self.view_name, basestring):
                invalid_fields.append(
                    {
                        TagKeys.ViewName: self.view_name,
                        CommonKeys.REASON: 'Must be a string',
                        ApiResultKeys.VFENSE_STATUS_CODE: (
                            GenericCodes.InvalidValue
                        )
                    }
                )

        if self.environment:
            if not isinstance(self.environment, basestring):
                invalid_fields.append(
                    {
                        TagKeys.Environment: self.environment,
                        CommonKeys.REASON: 'Must be a string',
                        ApiResultKeys.VFENSE_STATUS_CODE: (
                            GenericCodes.InvalidValue
                        )
                    }
                )

        if self.agents:
            if not isinstance(self.agents, list):
                invalid_fields.append(
                    {
                        TagMappedKeys.Agents: self.agents,
                        CommonKeys.REASON: 'Must be a list',
                        ApiResultKeys.VFENSE_STATUS_CODE: (
                            GenericCodes.InvalidValue
                        )
                    }
                )


        return invalid_fields

    def to_dict(self):
        """ Turn the fields into a dictionary.

        Returns:
            Dictionary
        """

        return {
            TagKeys.Environment: self.environment,
            TagKeys.TagName: self.tag_name,
            TagKeys.ViewName: self.view_name,
            TagKeys.IsGlobal: self.is_global,
            TagKeys.DateAdded: self.date_added,
            TagKeys.DateModified: self.date_modified,
            TagKeys.TagId: self.tag_id,
            TagMappedKeys.Agents: self.agents,
        }

    def to_dict_per_agent(self):
        """ Turn the fields into a dictionary.

        Returns:
            Dictionary
        """

        return {
            TagsPerAgentKeys.TagId: self.tag_id,
            TagsPerAgentKeys.TagName: self.tag_name,
            TagsPerAgentKeys.ViewName: self.view_name,
            TagsPerAgentKeys.AgentId: self.agent_id,
        }

    def to_dict_db(self):
        """ Turn the fields into a dictionary, with db related fields.

        Returns:
            (dict): A dictionary with the fields.

        """

        data = {
            TagKeys.DateAdded: (
                DbTime.epoch_time_to_db_time(self.date_added)
            ),
            TagKeys.DateModified: (
                DbTime.epoch_time_to_db_time(self.date_modified)
            ),
        }

        combined_data = dict(self.to_dict_non_null().items() + data.items())
        combined_data.pop(TagKeys.TagId, None)
        return combined_data

    def to_dict_db_update(self):
        """ Turn the fields into a dictionary, with db related fields.

        Returns:
            (dict): A dictionary with the fields.

        """

        data = {
            TagKeys.DateModified: (
                DbTime.epoch_time_to_db_time(self.date_modified)
            ),
        }

        combined_data = dict(self.to_dict_non_null().items() + data.items())
        combined_data.pop(TagKeys.TagId, None)
        return combined_data
