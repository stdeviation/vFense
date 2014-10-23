import logging
import logging.config
from time import time
from copy import deepcopy
from vFense import VFENSE_LOGGING_CONFIG

from vFense.core.agent import Agent
from vFense.core.agent._db import (
    fetch_agent, insert_agent, insert_hardware,
    delete_hardware_for_agent, update_agent, update_views_for_agent,
    delete_views_from_agent, delete_agent
)
from vFense.core.decorators import time_it
from vFense.core.agent._db_model import (
    AgentKeys, HardwarePerAgentKeys
)
from vFense.core.tag import Tag
from vFense.core.tag.tags import validate_tag_ids_in_views
from vFense.core.tag._db import (
    add_tags_to_agent, delete_tag_ids_from_agent, fetch_tag,
    fetch_tag_ids_for_agent, delete_agent_from_tags_in_views
)
from vFense.core.view.views import validate_view_names
from vFense.core.results import ApiResults
from vFense.core.status_codes import (
    DbCodes, GenericCodes, GenericFailureCodes,
)
from vFense.core.agent.status_codes import (
    AgentFailureCodes, AgentCodes
)
from vFense.receiver.status_codes import (
    AgentFailureResultCodes, AgentResultCodes
)

logging.config.fileConfig(VFENSE_LOGGING_CONFIG)
logger = logging.getLogger('rvapi')


class AgentManager(object):
    def __init__(self, agent_id=None):
        self.agent_id = agent_id
        self.properties = self._agent_attributes()
        self.tags = self.get_tags()
        self.views = self.get_views()

    def _agent_attributes(self):
        agent = Agent()
        if self.agent_id:
            agent_data = fetch_agent(self.agent_id)
            if agent_data:
                agent = Agent(**agent_data)

        return agent

    def get_attribute(self, agent_attribute):
        agent_key = None
        if self.agent_id:
            agent_data = fetch_agent(self.agent_id)
            if agent_data:
                agent_key = agent_data.get(agent_attribute, None)

        return agent_key

    def get_tags(self):
        tags = []
        if self.agent_id:
            tags = fetch_tag_ids_for_agent(self.agent_id)
        return tags

    def get_views(self):
        views = self.get_attribute(AgentKeys.Views)
        if not views:
            views = []
        return views

    @time_it
    def create(self, agent, tags=None):
        """Add an agent into vFense.
        Args:
            agent (Agent): An instance of Agent.
        Kwargs:
            tags (list): List of tag ids.

        Basic Usage:
            >>> from vFense.core.agent.manager import AgentManager
            >>> from vFense.core.agent import Agent
            >>> agent = Agent(computer_name='DISCIPLINE-1', etc...)
            >>> manager = AgentManager()
            >>> manager.create(agent)

        Returns:
            ApiResults instance
        """
        results = ApiResults()
        results.fill_in_defaults()
        if isinstance(agent, Agent):
            invalid_fields = agent.get_invalid_fields()
            agent.fill_in_defaults()
            agent.enabled = True
            _, valid_view_names, _ = (
                validate_view_names(agent.views)
            )
            if not invalid_fields:
                if valid_view_names:
                    agent.views = valid_view_names

                status_code, _, _, generated_ids = (
                    insert_agent(agent.to_dict_db())
                )
                if status_code == DbCodes.Inserted:
                    self.agent_id = generated_ids.pop()
                    agent.agent_id = self.agent_id
                    self.properties = self._agent_attributes()
                    self.add_hardware(agent.hardware)
                    if tags:
                        self.add_to_tags(tags)
                    msg = 'Agent {0} added successfully'.format(self.agent_id)
                    results.generic_status_code = GenericCodes.ObjectCreated
                    results.vfense_status_code = (
                        AgentResultCodes.NewAgentSucceeded
                    )
                    results.message = msg
                    results.data.append(agent.to_dict())
                    results.generated_ids = self.agent_id

                else:
                    msg = (
                        'Failed to add agent {0}.'.format(agent.computer_name)
                    )
                    results.generic_status_code = (
                        GenericFailureCodes.FailedToCreateObject
                    )
                    results.vfense_status_code = (
                        AgentFailureResultCodes.NewAgentFailed
                    )
                    results.message = msg
                    results.data.append(agent.to_dict())

            else:
                msg = (
                    'Failed to add agent, invalid fields were passed'
                )
                results.generic_status_code = (
                    GenericFailureCodes.FailedToCreateObject
                )
                results.vfense_status_code = (
                    AgentFailureResultCodes.NewAgentFailed
                )
                results.message = msg
                results.errors = invalid_fields
                results.data.append(agent.to_dict())

        else:
            msg = (
                'Invalid {0} Instance, must pass an instance of Agent.'
                .format(type(agent))
            )
            results.generic_status_code = (
                GenericFailureCodes.FailedToCreateObject
            )
            results.vfense_status_code = (
                AgentFailureResultCodes.NewAgentFailed
            )
            results.message = msg

        return results

    @time_it
    def update(self, agent, tags):
        """Update an agent into vFense.
        Args:
            agent (Agent): An instance of Agent.
        Kwargs:
            tags (list): List of tag ids.

        Basic Usage:
            >>> from vFense.core.agent.manager import AgentManager
            >>> from vFense.core.agent import Agent
            >>> agent = Agent(computer_name='DISCIPLINE-1', etc...)
            >>> tags = ['foo']
            >>> manager = AgentManager()
            >>> manager.update(agent, tags)

        Returns:
            ApiResults instance
        """
        results = ApiResults()
        results.fill_in_defaults()
        if isinstance(agent, Agent):
            agent_exist = self.properties
            invalid_fields = agent.get_invalid_fields()
            last_agent_update = time()
            agent.last_agent_update = last_agent_update
            if not agent.views:
                agent.views = self.views

            views_are_valid, valid_view_names, invalid_view_names = (
                validate_view_names(agent.views)
            )

            if views_are_valid and not invalid_fields and agent_exist.agent_id:
                agent.views = list(set(agent.views).union(self.views))
                agent.display_name = agent_exist[AgentKeys.DisplayName]
                status_code, _, errors, generated_ids = (
                    update_agent(self.agent_id, agent.to_dict_db_update())
                )
                if status_code == DbCodes.Replaced:
                    self.properties = self._agent_attributes()
                    self.add_hardware(agent.hardware)
                    if tags:
                        self.add_to_tags(tags)
                    msg = (
                        'Agent {0} updated successfully'
                        .format(self.agent_id)
                    )
                    results.generic_status_code = GenericCodes.ObjectUpdated
                    results.vfense_status_code = (
                        AgentResultCodes.StartUpSucceeded
                    )
                    results.message = msg
                    results.data.append(agent.to_dict_non_null())

                else:
                    msg = 'Failed to update agent {0}.'.format(self.agent_id)
                    results.generic_status_code = (
                        GenericFailureCodes.FailedToUpdateObject
                    )
                    results.vfense_status_code = (
                        AgentFailureResultCodes.StartupFailed
                    )
                    results.message = msg
                    results.data.append(agent.to_dict_non_null())

            elif invalid_fields:
                msg = (
                    'Failed to update agent {0}, invalid fields were passed'
                    .format(self.agent_id)
                )
                results.generic_status_code = (
                    GenericFailureCodes.FailedToUpdateObject
                )
                results.vfense_status_code = (
                    AgentFailureResultCodes.StartupFailed
                )
                results.message = msg
                results.errors = invalid_fields
                results.data.append(agent.to_dict_non_null())

            elif not agent_exist:
                msg = (
                    'Failed to update, agent {0} does not exist'
                    .format(self.agent_id)
                )
                results.generic_status_code = GenericFailureCodes.InvalidId
                results.vfense_status_code = (
                    AgentFailureResultCodes.StartupFailed
                )
                results.message = msg
                results.data.append(agent.to_dict_non_null())

            else:
                msg = (
                    'Failed to update agent, invalid views were passed: {0}.'
                    .format(', '.join(invalid_view_names))
                )
                results.generic_status_code = (
                    GenericFailureCodes.FailedToCreateObject
                )
                results.vfense_status_code = (
                    AgentFailureResultCodes.NewAgentFailed
                )
                results.message = msg
                results.data.append(agent.to_dict_non_null())

        else:
            msg = (
                'Invalid {0} Instance, must pass an instance of Agent.'
                .format(type(agent))
            )
            results.generic_status_code = (
                GenericFailureCodes.FailedToCreateObject
            )
            results.vfense_status_code = (
                AgentFailureResultCodes.NewAgentFailed
            )
            results.message = msg

        return results


    @time_it
    def add_to_views(self, views):
        """Add views to this agent.
        Args:
            views (list): List of views.

        Basic Usage:
            >>> from vFense.core.agent.manager import AgentManager
            >>> from vFense.core.agent import Agent
            >>> views = ['MIAMI', 'NYC']
            >>> manager = AgentManager('cac3f82c-d320-4e6f-9ee7-e28b1f527d76')
            >>> manager.add_to_views(views)

        Returns:
            ApiResults instance
        """
        results = ApiResults()
        results.fill_in_defaults()
        agent_exist = self.properties
        if agent_exist.agent_id:
            views_are_valid, valid_views, invalid_views = (
                validate_view_names(views)
            )
            views_exist_in_agent = (
                bool(set(views).intersection(self.views))
            )

            if views_are_valid and not views_exist_in_agent:
                status_code, _, _, _ = (
                    update_views_for_agent(views, self.agent_id)
                )
                if status_code == DbCodes.Replaced:
                    self.properties = self._agent_attributes()
                    self.views = self.get_views()
                    msg = (
                        'Views {0} were added successfully to agent {1}'
                        .format(', '.join(views), self.agent_id)
                    )
                    results.generic_status_code = GenericCodes.ObjectCreated
                    results.vfense_status_code = AgentCodes.ViewsAddedToAgent
                    results.message = msg
                    results.data = views
                    results.updated_ids.append(self.agent_id)

                else:
                    msg = (
                        'Failed to add viewstags: {0} to agent: {1}.'
                        .format(', '.join(views, self.agent_id))
                    )
                    results.generic_status_code = (
                        GenericFailureCodes.FailedToCreateObject
                    )
                    results.vfense_status_code = (
                        AgentFailureCodes.FailedToAddViewsToAgent
                    )
                    results.message = msg
                    results.data = views
                    results.unchanged_ids.append(self.agent_id)

            elif views_exist_in_agent:
                msg = (
                    'Some of the views: {0} already exist for agent: {1}.'
                    .format(', '.join(views), self.agent_id)
                )
                results.generic_status_code = GenericFailureCodes.InvalidId
                results.vfense_status_code = GenericFailureCodes.InvalidId
                results.message = msg
                results.unchanged_ids.append(self.agent_id)

            else:
                msg = (
                    'Invalid views: {0}.'.format(', '.join(views))
                )
                results.generic_status_code = GenericFailureCodes.InvalidId
                results.vfense_status_code = GenericFailureCodes.InvalidId
                results.message = msg
                results.unchanged_ids.append(self.agent_id)

        else:
            msg = (
                'Agent id {0} does not exist.'.format(self.agent_id)
            )
            results.generic_status_code = GenericFailureCodes.InvalidId
            results.vfense_status_code = GenericFailureCodes.InvalidId
            results.message = msg
            results.unchanged_ids.append(self.agent_id)

        return results

    @time_it
    def remove_from_views(self, views):
        """Remove views from this agent.
        Args:
            views (list): List of views.

        Basic Usage:
            >>> from vFense.core.agent.manager import AgentManager
            >>> views = ['MIAMI']
            >>> manager = AgentManager('cac3f82c-d320-4e6f-9ee7-e28b1f527d76')
            >>> manager.remove_from_views(views)

        Returns:
            Dictionary
            >>>
        """
        results = ApiResults()
        results.fill_in_defaults()
        if self.properties.agent_id:
            views_exist_in_agent = (
                bool(set(views).intersection(self.views))
            )
            if views_exist_in_agent:
                status_code, _, _, _ = (
                    delete_views_from_agent(views, self.agent_id)
                )
                delete_agent_from_tags_in_views(self.agent_id, views)
                if status_code == DbCodes.Replaced:
                    self.properties = self._agent_attributes()
                    self.views = self.get_views()
                    msg = (
                        'Views {0} were removed successfully from agent {1}'
                        .format(', '.join(views), self.agent_id)
                    )
                    results.generic_status_code = GenericCodes.ObjectDeleted
                    results.vfense_status_code = (
                        AgentCodes.ViewsRemovedFromAgent
                   )
                    results.message = msg
                    results.data = views
                    results.updated_ids.append(self.agent_id)

                else:
                    msg = (
                        'Failed to remove views: {0} from agent: {1}.'
                        .format(', '.join(views), self.agent_id)
                    )
                    results.generic_status_code = (
                        GenericFailureCodes.FailedToDeleteObject
                    )
                    results.vfense_status_code = (
                        AgentFailureCodes.FailedToRemoveViewsFromAgent
                    )
                    results.message = msg
                    results.data = views
                    results.unchanged_id.append(self.agent_id)

            else:
                msg = (
                    'Invalid views: {0}.'.format(', '.join(views))
                )
                results.generic_status_code = GenericFailureCodes.InvalidId
                results.vfense_status_code = GenericFailureCodes.InvalidId
                results.message = msg
                results.data = views
                results.unchanged_ids.append(self.agent_id)

        else:
            msg = (
                'Agent id {0} does not exist.'.format(self.agent_id)
            )
            results.generic_status_code = GenericFailureCodes.InvalidId
            results.vfense_status_code = GenericFailureCodes.InvalidId
            results.message = msg
            results.unchanged_ids.append(self.agent_id)

        return results

    @time_it
    def add_to_tags(self, tag_ids):
        """Add tags to this agent.
        Args:
            tag_ids (list): List of tag ids.

        Basic Usage:
            >>> from vFense.core.agent.manager import AgentManager
            >>> from vFense.core.agent import Agent
            >>> tag_ids = ['0842c4c0-94ab-4fe4-9346-3b59fa53c316']
            >>> manager = AgentManager('cac3f82c-d320-4e6f-9ee7-e28b1f527d76')
            >>> manager.add_to_tags(tag_ids)

        Returns:
            ApiResults instance
        """
        results = ApiResults()
        results.fill_in_defaults()
        tag_data = []
        if self.properties.agent_id:
            views = self.properties.views
            tags_are_valid, valid_tags, invalid_tags = (
                validate_tag_ids_in_views(tag_ids, views)
            )

            if tags_are_valid and not set(valid_tags).issubset(self.tags):
                for tag_id in tag_ids:
                    tag = Tag(**fetch_tag(tag_id))
                    tag.agent_id = self.agent_id
                    tag_data.append(tag.to_dict_per_agent())
                status_code, _, _, _ = add_tags_to_agent(tag_data)
                if status_code == DbCodes.Inserted:
                    self.properties = self._agent_attributes()
                    self.tags = self.get_tags()
                    msg = (
                        'Tag ids {0} were added successfully to agent {1}'
                        .format(', '.join(tag_ids), self.agent_id)
                    )
                    results.generic_status_code = GenericCodes.ObjectCreated
                    results.vfense_status_code = AgentCodes.TagsAddedToAgent
                    results.message = msg
                    results.data = tag_data
                    results.updated_ids.append(self.agent_id)

                else:
                    msg = (
                        'Failed to add tags to agent: {0}.'
                        .format(self.agent_id)
                    )
                    results.generic_status_code = (
                        GenericFailureCodes.FailedToCreateObject
                    )
                    results.vfense_status_code = (
                        AgentFailureCodes.FailedToAddTagsToAgent
                    )
                    results.message = msg
                    results.data = tag_data
                    results.unchanged_ids.append(self.agent_id)

            elif set(valid_tags).issubset(self.tags):
                msg = (
                    'Some of the tags already exist for agent: {0}.'
                    .format(self.agent_id)
                )
                results.generic_status_code = GenericFailureCodes.InvalidId
                results.vfense_status_code = GenericFailureCodes.InvalidId
                results.message = msg
                results.data = tag_ids
                results.unchanged_ids.append(self.agent_id)

            else:
                results.generic_status_code = GenericFailureCodes.InvalidId
                results.vfense_status_code = GenericFailureCodes.InvalidId
                results.message = 'Invalid tags'
                results.data = tag_ids
                results.unchanged_ids.append(self.agent_id)

        else:
            msg = (
                'Agent id {0} does not exist.'.format(self.agent_id)
            )
            results.generic_status_code = GenericFailureCodes.InvalidId
            results.vfense_status_code = GenericFailureCodes.InvalidId
            results.message = msg
            results.unchanged_ids.append(self.agent_id)

        return results

    @time_it
    def remove_from_tags(self, tag_ids):
        """Remove tags from this agent.
        Args:
            tag_ids (list): List of tag ids.

        Basic Usage:
            >>> from vFense.core.agent.manager import AgentManager
            >>> tag_ids = ['0842c4c0-94ab-4fe4-9346-3b59fa53c316']
            >>> manager = AgentManager('cac3f82c-d320-4e6f-9ee7-e28b1f527d76')
            >>> manager.remove_from_tags(tag_ids)

        Returns:
            ApiResults instance
        """
        results = ApiResults()
        results.fill_in_defaults()
        agent_exist = self.properties
        if agent_exist:
            if set(tag_ids).issubset(self.tags):
                status_code, _, _, _ = (
                    delete_tag_ids_from_agent(self.agent_id, tag_ids)
                )
                if status_code == DbCodes.Deleted:
                    self.properties = self._agent_attributes()
                    self.tags = self.get_tags()
                    msg = (
                        'Tags were removed successfully from agent {0}'
                        .format(self.agent_id)
                    )
                    results.generic_status_code = GenericCodes.ObjectDeleted
                    results.vfense_status_code = (
                        AgentCodes.TagsRemovedFromAgent
                   )
                    results.message = msg
                    results.data = tag_ids
                    results.updated_ids.append(self.agent_id)

                else:
                    msg = (
                        'Failed to remove tags from agent: {0}.'
                        .format(self.agent_id)
                    )
                    results.generic_status_code = (
                        GenericFailureCodes.FailedToDeleteObject
                    )
                    results.vfense_status_code = (
                        AgentFailureCodes.FailedToRemoveTagsFromAgent
                    )
                    results.message = msg
                    results.data = tag_ids
                    results.unchanged_ids.append(self.agent_id)

            else:
                results.generic_status_code = GenericFailureCodes.InvalidId
                results.vfense_status_code = GenericFailureCodes.InvalidId
                results.message = 'Invalid tags'
                results.data = tag_ids
                results.unchanged_ids.append(self.agent_id)

        else:
            msg = (
                'Agent id {0} does not exist.'.format(self.agent_id)
            )
            results.generic_status_code = GenericFailureCodes.InvalidId
            results.vfense_status_code = GenericFailureCodes.InvalidId
            results.message = msg
            results.unchanged_ids.append(self.agent_id)

        return results

    @time_it
    def add_hardware(self, hardware):
        """Add hardware to an agent.
        Args:
            hardware (dict): Dictionary of devices to add.

        Basic Usage:
            >>> from vFense.core.agent.manager import AgentManager
            >>> from vFense.core.agent import Agent
            >>> hardware = {
                "display": [
                    {
                        "speed_mhz": "GeForce GTX 660M",
                        "name": "NVIDIA GeForce GTX 660M  ",
                        "ram_kb": 0
                    }
                ]
            }
            >>> manager = AgentManager()
            >>> manager.add_hardware(hardware)

        Returns:
            ApiResults instance
        """
        results = ApiResults()
        results.fill_in_defaults()
        agent_exist = self.properties
        hw_data = []
        if agent_exist:
            if isinstance(hardware, dict):
                for hw in hardware.keys():
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
                            'Hardware added successfully to agent {0}'
                            .format(self.agent_id)
                        )
                        results.generic_status_code = (
                            GenericCodes.ObjectCreated
                        )
                        results.vfense_status_code = (
                            AgentCodes.HardwareAddedToAgent
                        )
                        results.message = msg
                        results.data.append(hw_data)
                        results.updated_ids.append(self.agent_id)

                else:
                    msg = (
                        'Empty hardware list, agent {0} could not be updated.'
                        .format(self.agent_id)
                    )
                    results.generic_status_code = (
                        GenericFailureCodes.FailedToCreateObject
                    )
                    results.vfense_status_code = (
                        AgentFailureCodes.FailedToAddHardwareToAgent
                    )
                    results.message = msg
                    results.data = [hw_data]
                    results.unchanged_ids = [self.agent_id]

            else:
                msg = (
                    'Hardware needs to be a dictionary and not a {0}.'
                    .format(type(hardware))
                )
                results.generic_status_code = GenericFailureCodes.InvalidValue
                results.vfense_status_code = GenericFailureCodes.InvalidValue
                results.message = msg
                results.unchanged_ids = [self.agent_id]

        else:
            msg = (
                'Agent id {0} does not exist.'.format(self.agent_id)
            )
            results.generic_status_code = GenericFailureCodes.InvalidId
            results.vfense_status_code = GenericFailureCodes.InvalidId
            results.message = msg
            results.unchanged_ids = [self.agent_id]

        return results

    @time_it
    def edit_environment(self, environment):
        """Change current or default view.
        Args:
            environment (str): Production level you assigned to this
                agent.

        Basic Usage:
            >>> from vFense.agent.manager import AgentManager
            >>> agent_id = 'cac3f82c-d320-4e6f-9ee7-e28b1f527d76'
            >>> manager = AgentManager(agent_id)
            >>> manager.edit_environment('Development')

        Returns:
            ApiResults instance
        """
        agent = Agent(environment=environment)
        results = self.__edit_properties(agent)
        return results


    @time_it
    def edit_display_name(self, display_name):
        """Change current or default view.
        Args:
            display_name (str): The vFense display name of this agent.

        Basic Usage:
            >>> from vFense.agent.manager import AgentManager
            >>> agent_id = 'cac3f82c-d320-4e6f-9ee7-e28b1f527d76'
            >>> manager = AgentManager(agent_id)
            >>> manager.edit_display_name('Test agent 3')

        Returns:
            ApiResults instance
        """
        agent = Agent(display_name=display_name)
        results = self.__edit_properties(agent)
        return results

    @time_it
    def edit_needs_reboot(self, needs_reboot):
        """Change the reboot status of this agent. Does this agent
            require a reboot?
        Args:
            needs_reboot (bool): This agent require a reboot or not.

        Basic Usage:
            >>> from vFense.agent.manager import AgentManager
            >>> agent_id = 'cac3f82c-d320-4e6f-9ee7-e28b1f527d76'
            >>> manager = AgentManager(agent_id)
            >>> manager.edit_needs_reboot(True)

        Returns:
            ApiResults instance
        """
        agent = Agent(needs_reboot=needs_reboot)
        results = self.__edit_properties(agent)
        return results

    @time_it
    def assign_new_token(self, new_token=False):
        """Allow the agent with a previously valid token to
            get a current valid token.
        Args:
            new_token (bool): Allow this agent to authenticate once
                and pick up a new token.
                default=False

        Basic Usage:
            >>> from vFense.agent.manager import AgentManager
            >>> agent_id = 'cac3f82c-d320-4e6f-9ee7-e28b1f527d76'
            >>> manager = AgentManager(agent_id)
            >>> manager.assign_new_token(True)

        Returns:
            ApiResults instance
        """
        agent = Agent(assign_new_token=new_token)
        results = self.__edit_properties(agent)
        return results


    @time_it
    def update_last_checkin_time(self):
        """Update the timestamp for the last time the agent communicated.
        Basic Usage:
            >>> from vFense.agent.manager import AgentManager
            >>> agent_id = 'cac3f82c-d320-4e6f-9ee7-e28b1f527d76'
            >>> manager = AgentManager(agent_id)
            >>> manager.update_checkin_time()

        Returns:
            ApiResults instance
        """
        now = time()
        agent = Agent(last_agent_update=now)
        results = self.__edit_properties(agent)
        return results

    @time_it
    def update_token(self, token):
        """Update the token that the agent is using.

        Basic Usage:
            >>> from vFense.agent.manager import AgentManager
            >>> agent_id = 'cac3f82c-d320-4e6f-9ee7-e28b1f527d76'
            >>> manager = AgentManager(agent_id)
            >>> manager.update_checkin_time()

        Returns:
            ApiResults instance
        """
        agent = Agent(token=token)
        results = self.__edit_properties(agent)
        return results


    @time_it
    def __edit_properties(self, agent):
        """ Edit the properties of this agent.
        Args:
            agent (Agent): The Agent instance with all of its properties.

        Basic Usage:
            >>> from vFense.agent import Agent
            >>> from vFense.agent.manager import AgentManager
            >>> agent_id = 'cac3f82c-d320-4e6f-9ee7-e28b1f527d76'
            >>> agent = (
                    Agent(display_name='Web Server 1')
                )
            >>> manager = AgentManager(agent_id)
            >>> manager.__edit_agent_properties(agent)

        Return:
            ApiResults instance
        """

        results = ApiResults()
        results.fill_in_defaults()
        if self.properties.agent_id and isinstance(agent, Agent):
            invalid_fields = agent.get_invalid_fields()
            if not invalid_fields:
                object_status, _, _, _ = (
                    update_agent(self.agent_id, agent.to_dict_db_update())
                )

                if object_status == DbCodes.Replaced:
                    msg = 'Agent %s was updated - ' % (self.agent_id)
                    generic_status_code = GenericCodes.ObjectUpdated
                    vfense_status_code = AgentCodes.AgentUpdated
                    results.updated_ids.append(self.agent_id)
                    results.data.append(agent.to_dict_non_null())

                elif object_status == DbCodes.Unchanged:
                    msg = 'Agent %s was not updated - ' % (self.agent_id)
                    generic_status_code = GenericCodes.ObjectUnchanged
                    vfense_status_code = AgentCodes.AgentUnchanged
                    results.unchanged_ids.append(self.agent_id)

            else:
                results.generic_status_code = GenericCodes.InvalidId
                results.vfense_status_code = (
                    AgentFailureCodes.FailedToUpdateAgent
                )
                results.message = (
                    'Agent {0} properties were invalid'.format(self.agent_id)
                )
                results.unchanged_ids.append(self.agent_id)
                results.errors = invalid_fields

        elif not isinstance(agent, Agent):
            results.generic_status_code = GenericCodes.InvalidId
            results.vfense_status_code = GenericFailureCodes.InvalidInstanceType
            results.message = (
                'Agent {0} is not of instance Agent., instanced passed {1}'
                .format(self.agent_id, type(agent))
            )
            results.unchanged_ids.append(self.agent_id)

        else:
            results.generic_status_code = GenericCodes.InvalidId
            results.vfense_status_code = AgentFailureCodes.AgentIdDoesNotExist
            results.message = 'Agent %s does not exist - ' % (self.agent_id)
            results.unchanged_id.append(self.agent_id)

        return results

    @time_it
    def remove(self):
        """Remove this agent from the system.

        Basic Usage:
            >>> from vFense.agent import Agent
            >>> from vFense.agent.manager import AgentManager
            >>> agent_id = 'cac3f82c-d320-4e6f-9ee7-e28b1f527d76'
            >>> manager = AgentManager(agent_id)
            >>> manager.remove()

        Return:
            ApiResults instance
        """

        results = ApiResults()
        results.fill_in_defaults()
        if self.properties.agent_id:
            delete_tag_ids_from_agent(self.agent_id, self.tags)
            delete_hardware_for_agent(self.agent_id)
            status_code, _, _, _ = delete_agent(self.agent_id)
            if status_code == DbCodes.Deleted:
                msg = 'Agent %s was deleted - ' % (self.agent_id)
                results.message = msg
                results.generic_status_code = GenericCodes.ObjectDeleted
                results.vfense_status_code = AgentCodes.AgentDeleted
                results.deleted_ids.append(self.agent_id)

            else:
                msg = 'Invalid agent id %s' % (self.agent_id)
                results.message = msg
                results.generic_status_code = GenericCodes.InvalidId
                results.vfense_status_code = GenericCodes.InvalidId
                results.unchanged_ids.append(self.agent_id)

        else:
            msg = 'Invalid agent id %s' % (self.agent_id)
            results.message = msg
            results.generic_status_code = GenericCodes.InvalidId
            results.vfense_status_code = GenericCodes.InvalidId
            results.unchanged_ids.append(self.agent_id)

        return results
