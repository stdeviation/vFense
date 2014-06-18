import logging
import logging.config
from copy import deepcopy
from vFense import VFENSE_LOGGING_CONFIG

from vFense.core._db_constants import DbTime
from vFense.core.agent import Agent
from vFense.core.agent._db import (
    fetch_agent, insert_agent, insert_hardware,
    delete_hardware_for_agent
)
from vFense.core.agent._db_model import (
    AgentKeys, HardwarePerAgentKeys
)
from vFense.core.tag._db_model import TagKeys, TagsPerAgentKeys
from vFense.core.tag.tags import validate_tag_ids_in_views
from vFense.core.tag._db import (
    add_tags_to_agent, delete_tag_ids_from_agent
)
from vFense.core.view.views import validate_view_names
from vFense.errorz._constants import ApiResultKeys
from vFense.errorz.status_codes import (
    DbCodes, GenericCodes, AgentResultCodes, GenericFailureCodes,
    AgentFailureResultCodes, AgentFailureCodes, AgentCodes
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
                self.add_hardware(agent_data[AgentKeys.Hardware])
                if tags:
                    self.add_to_tags(tags)
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

    def add_to_tags(self, tag_ids):
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
        tag_data = []
        if agent_exist:
            views = agent_exist[AgentKeys.Views]
            tags_valid, _, invalid_tags = (
                validate_tag_ids_in_views(tag_ids, views)
            )
            if tags_valid:
                for tag_id in tag_ids:
                    tag_data.append(
                        {
                            TagsPerAgentKeys.AgentId: self.agent_id,
                            TagsPerAgentKeys.TagId: tag_id,
                        }
                    )
                status_code, _, _, _ = add_tags_to_agent(tag_data)
                if status_code == DbCodes.Inserted:
                    self.properties = self._agent_attributes()
                    msg = (
                        'Tag ids {0} were added successfully to agent {1}'
                        .format(', '.join(tag_ids), self.agent_id)
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

    def remove_from_tags(self, tag_ids):
        """Remove tags from an agent.
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
            if set(tag_ids).issubset(self.tags):
                status_code, _, _, _ = (
                    delete_tag_ids_from_agent(self.agent_id, tag_ids)
                )
                if status_code == DbCodes.Deleted:
                    self.properties = self._agent_attributes()
                    msg = (
                        'Tag ids {0} were removed successfully from agent {1}'
                        .format(', '.join(tag_ids), self.agent_id)
                    )
                    results[ApiResultKeys.GENERIC_STATUS_CODE] = (
                        GenericCodes.ObjectDeleted
                    )
                    results[ApiResultKeys.VFENSE_STATUS_CODE] = (
                        AgentCodes.TagsRemovedFromAgent
                   )
                    results[ApiResultKeys.MESSAGE] = msg
                    results[ApiResultKeys.UPDATED_IDS] = [self.agent_id]

                else:
                    msg = (
                        'Failed to remove tags: {0} from agent: {1}.'
                        .format(', '.join(tag_ids, self.agent_id))
                    )
                    results[ApiResultKeys.GENERIC_STATUS_CODE] = (
                        GenericFailureCodes.FailedToDeleteObject
                    )
                    results[ApiResultKeys.VFENSE_STATUS_CODE] = (
                        AgentFailureCodes.FailedToRemoveTagsFromAgent
                    )
                    results[ApiResultKeys.MESSAGE] = msg
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


    def add_hardware(self, hardware):
        """Add hardware to an agent.
        Args:
            hardware (dict): Dictionary of devices to add.

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
        hw_data = []
        if agent_exist:
            if isinstance(hardware, dict):
                for hw in hw_data.keys():
                    hw_info = (
                        {
                            HardwarePerAgentKeys.AgentId: self.agent_id,
                            HardwarePerAgentKeys.Type: hw,
                        }
                    )
                    if hw != 'memory':
                        for info in hardware[hw]:
                            custominfo = deepcopy(hw_info)
                            for key, val in info.items():
                                custominfo[key] = val
                            hw_data.append(custominfo)
                    else:
                        custominfo = deepcopy(hw_info)
                        custominfo['total_memory'] = hardware[hw]
                        custominfo['name'] = hw
                        hw_data.append(custominfo)

                if hw_data:
                    delete_hardware_for_agent(self.agent_id)
                    status_code, _, _, _ = insert_hardware(hw_data)

                    if status_code == DbCodes.Inserted:
                        self.properties = self._agent_attributes()
                        msg = (
                            'Hardware added successfully to agent {1}'
                            .format(self.agent_id)
                        )
                        results[ApiResultKeys.GENERIC_STATUS_CODE] = (
                            GenericCodes.ObjectCreated
                        )
                        results[ApiResultKeys.VFENSE_STATUS_CODE] = (
                            AgentCodes.HardwareAddedToAgent
                        )
                        results[ApiResultKeys.MESSAGE] = msg
                        results[ApiResultKeys.DATA] = [hw_data]
                        results[ApiResultKeys.UPDATED_IDS] = [self.agent_id]

                else:
                    msg = (
                        'Empty hardware list, agent {0} could not be updated.'
                        .format(self.agent_id)
                    )
                    results[ApiResultKeys.GENERIC_STATUS_CODE] = (
                        GenericFailureCodes.FailedToCreateObject
                    )
                    results[ApiResultKeys.VFENSE_STATUS_CODE] = (
                        AgentFailureCodes.FailedToAddHardwareToAgent
                    )
                    results[ApiResultKeys.MESSAGE] = msg
                    results[ApiResultKeys.DATA] = [hw_data]
                    results[ApiResultKeys.UNCHANGED_IDS] = [self.agent_id]

            else:
                msg = (
                    'Hardware needs to be a dictionary and not a {0}.'
                    .format(type(hardware))
                )
                results[ApiResultKeys.GENERIC_STATUS_CODE] = (
                    GenericFailureCodes.InvalidValue
                )
                results[ApiResultKeys.VFENSE_STATUS_CODE] = (
                    GenericFailureCodes.InvalidValue
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
