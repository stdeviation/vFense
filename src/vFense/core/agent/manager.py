import logging
import logging.config
from vFense import VFENSE_LOGGING_CONFIG

from vFense.core._db_constants import DbTime
from vFense.core.agent import Agent
from vFense.core.agent._db import (
    fetch_agent, insert_agent
)
from vFense.core.agent._db_model import AgentKeys
from vFense.core.tag._db_model import TagKeys
from vFense.core.tag._db import (
    add_tags_to_agent, delete_agent_ids_from_tag
)
from vFense.core.view.views import validate_view_names
from vFense.errorz._constants import ApiResultKeys
from vFense.errorz.status_codes import (
    DbCodes, GenericCodes, AgentResultCodes, GenericFailureCodes,
    AgentFailureResultCodes
)

logging.config.fileConfig(VFENSE_LOGGING_CONFIG)
logger = logging.getLogger('rvapi')


class AgentManager(object):
    def __init__(self, agent_id=None):
        self.agent_id = agent_id
        self.properties = self._agent_attributes()
        if self.properties:
            if self.properties.get(AgentKeys.Tags):
                self.tags = (
                    map(
                        lambda x: x[TagKeys.TagId],
                        self.properties.get(AgentKeys.Tags, [])
                    )
                )
            else:
                self.tags = []
        else:
            self.tags = []

    def _agent_attributes(self):
        agent_data = fetch_agent(self.agent_id)

        return agent_data

    def get_attribute(self, agent_attribute):
        agent_data = fetch_agent(self.agent_id)
        agent_key = None
        if agent_data:
            agent_key = agent_data.get(agent_attribute, None)

        return agent_key


    def new(self, agent, tags=None):
        """Add an agent into vFense.
        Args:
            agent (Agent): An instance of Agent.
        Kwargs:
            tags (list): List of tag ids.

        Basic Usage:
            >>> from vFense.core.agent.manager import AgentManager
            >>> from vFense.core.agent import Agent

        Returns:
            Dictionary
            >>>
        """
        results = {}
        if isinstance(agent, Agent):
            agent.fill_in_defaults()
            agent_data = agent.to_dict()
            agent_data[AgentKeys.LastAgentUpdate] = (
                DbTime().epoch_time_to_db_time(
                    agent_data[AgentKeys.LastAgentUpdate]
                )
            )
            valid_views, valid_view_names, invalid_view_names = (
                validate_view_names(agent[AgentKeys.Views])
            )

            status_code, _, _, generated_ids = (
                insert_agent(agent_data)
            )
            if status_code == DbCodes.Inserted:
                self.agent_id = generated_ids.pop()
                self.properties = self._agent_attributes()
                Hardware().add(self.agent_id, agent_data[AgentKeys.Hardware])
                agent_data[AgentKeys.AgentId] = self.agent_id
                msg = 'Agent {0} added successfully'.format(self.agent_id)
                results[ApiResultKeys.GENERIC_STATUS_CODE] = (
                    GenericCodes.ObjectCreated
                )
                results[ApiResultKeys.VFENSE_STATUS_CODE] = (
                    AgentResultCodes.NewAgentSucceeded
                )
                results[ApiResultKeys.MESSAGE] = msg
                results[ApiResultKeys.DATA] = [agent_data]
                results[ApiResultKeys.GENERATED_IDS] = [self.agent_id]

            else:
                msg = 'Failed to add agent.'
                results[ApiResultKeys.GENERIC_STATUS_CODE] = (
                    GenericFailureCodes.FailedToCreateObject
                )
                results[ApiResultKeys.VFENSE_STATUS_CODE] = (
                    AgentFailureResultCodes.NewAgentFailed
                )
                results[ApiResultKeys.MESSAGE] = msg
                results[ApiResultKeys.DATA] = [agent_data]
        else:
            msg = (
                'Invalid {0} Instance, must pass an instance of Agent.'
                .format(type(agent))
            )
            results[ApiResultKeys.GENERIC_STATUS_CODE] = (
                    GenericFailureCodes.FailedToCreateObject
            )
            results[ApiResultKeys.VFENSE_STATUS_CODE] = (
                    AgentFailureResultCodes.NewAgentFailed
            )
            results[ApiResultKeys.MESSAGE] = msg
            results[ApiResultKeys.DATA] = [agent_data]

        return results

    def add_tags(self, tag_ids):
        """Add tags to an agent.
        Args:
            tag_ids (list): List of tag ids.

        Basic Usage:
            >>> from vFense.core.agent.manager import AgentManager
            >>> from vFense.core.agent import Agent
            >>> tag_ids = ['tag_id']

        Returns:
            Dictionary
            >>>
        """
        results = {}
        agent_exist = self.properties
        if agent_exist:

