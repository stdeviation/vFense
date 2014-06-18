from vFense.core.agent._db_model import *
import logging
import logging.config
from vFense import VFENSE_LOGGING_CONFIG

from vFense.utils.common import *
from vFense.core._db_constants import DbTime
from vFense.core.tag import Tag
from vFense.core.tag._db import fetch_tag
from vFense.core.agent import Agent
from vFense.core.view.views import validate_view_names
from vFense.core.tag._db_model import TagKeys, TagMappedKeys
from vFense.errorz.error_messages import GenericResults

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
                    tag_data[TagKeys.AgentId] = self.tag_id
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

