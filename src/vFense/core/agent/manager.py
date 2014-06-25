import logging
import logging.config
from time import time
from copy import deepcopy
from vFense import VFENSE_LOGGING_CONFIG

from vFense.core._db_constants import DbTime
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
from vFense.core.tag._db_model import TagKeys, TagsPerAgentKeys
from vFense.core.tag.tags import validate_tag_ids_in_views
from vFense.core.tag._db import (
    add_tags_to_agent, delete_tag_ids_from_agent, fetch_tag,
    fetch_tag_ids_for_agent, delete_agent_from_tags_in_views
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
        self.tags = self.get_tags()
        self.views = self.get_views()

    def _agent_attributes(self):
        agent_data = {}
        if self.agent_id:
            agent_data = fetch_agent(self.agent_id)

        return agent_data

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
            Dictionary
            >>>
            {
                "data": {
                    "rebooted": true,
                    "views": [
                        "global"
                    ],
                    "last_agent_update": 1403100258.599256,
                    "agent_status": "up",
                    "bit_type": "64",
                    "agent_id": "cac3f82c-d320-4e6f-9ee7-e28b1f527d76",
                    "computer_name": "DISCIPLINE-1",
                    "date_added": 1403100258.599249,
                    "needs_reboot": false,
                    "hardware": {
                        "nic": [
                            {
                                "mac": "3085A925BFD6",
                                "ip_address": "10.0.0.2",
                                "name": "Local Area Connection"
                            },
                            {
                                "mac": "005056C00001",
                                "ip_address": "192.168.110.1",
                                "name": "VMware Network Adapter VMnet1"
                            },
                            {
                                "mac": "005056C00008",
                                "ip_address": "192.168.252.1",
                                "name": "VMware Network Adapter VMnet8"
                            }
                        ],
                        "display": [
                            {
                                "speed_mhz": "GeForce GTX 660M",
                                "name": "NVIDIA GeForce GTX 660M  ",
                                "ram_kb": 0
                            }
                        ],
                        "storage": [
                            {
                                "free_size_kb": 155600024,
                                "name": "C:",
                                "size_kb": 499872764,
                                "file_system": "NTFS"
                            }
                        ],
                        "cpu": [
                            {
                                "speed_mhz": 2401,
                                "name": "Intel(R) Core(TM) i7-3630QM CPU @ 2.40GHz",
                                "cpu_id": 1,
                                "bit_type": 64,
                                "cache_kb": 1024,
                                "cores": 4
                            }
                        ],
                        "memory": 25165824
                    },
                    "display_name": null,
                    "production_level": "production",
                    "os_code": "windows",
                    "version": "6.1.7601",
                    "os_string": "Windows 7 Professional N"
                },
                "message": "Agent cac3f82c-d320-4e6f-9ee7-e28b1f527d76 added successfully",
                "generated_ids": "cac3f82c-d320-4e6f-9ee7-e28b1f527d76",
                "vfense_status_code": 3200,
                "generic_status_code": 1010
            }
        """
        results = {}
        if isinstance(agent, Agent):
            invalid_fields = agent.get_invalid_fields()
            agent.fill_in_defaults()
            agent_data = agent.to_dict()
            last_agent_update = agent_data[AgentKeys.LastAgentUpdate]
            date_added = agent_data[AgentKeys.DateAdded]
            agent_data[AgentKeys.LastAgentUpdate] = (
                DbTime().epoch_time_to_db_time(
                    agent_data[AgentKeys.LastAgentUpdate]
                )
            )
            agent_data[AgentKeys.DateAdded] = (
                DbTime().epoch_time_to_db_time(
                    agent_data[AgentKeys.DateAdded]
                )
            )
            views_are_valid, valid_view_names, invalid_view_names = (
                validate_view_names(agent_data[AgentKeys.Views])
            )

            if views_are_valid and not invalid_fields:
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
                    results[ApiResultKeys.DATA] = agent_data
                    results[ApiResultKeys.GENERATED_IDS] = self.agent_id

                else:
                    msg = 'Failed to add agent.'
                    results[ApiResultKeys.GENERIC_STATUS_CODE] = (
                        GenericFailureCodes.FailedToCreateObject
                    )
                    results[ApiResultKeys.VFENSE_STATUS_CODE] = (
                        AgentFailureResultCodes.NewAgentFailed
                    )
                    results[ApiResultKeys.MESSAGE] = msg
                    results[ApiResultKeys.DATA] = agent_data

            elif invalid_fields:
                msg = (
                    'Failed to add agent, invalid fields were passed'
                )
                results[ApiResultKeys.GENERIC_STATUS_CODE] = (
                    GenericFailureCodes.FailedToCreateObject
                )
                results[ApiResultKeys.VFENSE_STATUS_CODE] = (
                    AgentFailureResultCodes.NewAgentFailed
                )
                results[ApiResultKeys.MESSAGE] = msg
                results[ApiResultKeys.ERRORS] = invalid_fields
                results[ApiResultKeys.DATA] = agent_data

            else:
                msg = (
                    'Failed to add agent, invalid views were passed: {0}.'
                    .format(', '.join(invalid_view_names))
                )
                results[ApiResultKeys.GENERIC_STATUS_CODE] = (
                    GenericFailureCodes.FailedToCreateObject
                )
                results[ApiResultKeys.VFENSE_STATUS_CODE] = (
                    AgentFailureResultCodes.NewAgentFailed
                )
                results[ApiResultKeys.MESSAGE] = msg
                results[ApiResultKeys.DATA] = agent_data

            results[ApiResultKeys.DATA][AgentKeys.LastAgentUpdate] = (
                last_agent_update
            )
            results[ApiResultKeys.DATA][AgentKeys.DateAdded] = (
                date_added
            )
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

        return results

    @time_it
    def update(self, agent, tags):
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
            >>> manager.update(agent)

        Returns:
            Dictionary
            >>>
            {
                "data": {
                    "rebooted": true,
                    "views": [
                        "global"
                    ],
                    "last_agent_update": 1403100258.599256,
                    "agent_status": "up",
                    "bit_type": "64",
                    "agent_id": "cac3f82c-d320-4e6f-9ee7-e28b1f527d76",
                    "computer_name": "DISCIPLINE-1",
                    "needs_reboot": false,
                    "hardware": {
                        "nic": [
                            {
                                "mac": "3085A925BFD6",
                                "ip_address": "10.0.0.2",
                                "name": "Local Area Connection"
                            },
                            {
                                "mac": "005056C00001",
                                "ip_address": "192.168.110.1",
                                "name": "VMware Network Adapter VMnet1"
                            },
                            {
                                "mac": "005056C00008",
                                "ip_address": "192.168.252.1",
                                "name": "VMware Network Adapter VMnet8"
                            }
                        ],
                        "display": [
                            {
                                "speed_mhz": "GeForce GTX 660M",
                                "name": "NVIDIA GeForce GTX 660M  ",
                                "ram_kb": 0
                            }
                        ],
                        "storage": [
                            {
                                "free_size_kb": 155600024,
                                "name": "C:",
                                "size_kb": 499872764,
                                "file_system": "NTFS"
                            }
                        ],
                        "cpu": [
                            {
                                "speed_mhz": 2401,
                                "name": "Intel(R) Core(TM) i7-3630QM CPU @ 2.40GHz",
                                "cpu_id": 1,
                                "bit_type": 64,
                                "cache_kb": 1024,
                                "cores": 4
                            }
                        ],
                        "memory": 25165824
                    },
                    "display_name": null,
                    "production_level": "production",
                    "os_code": "windows",
                    "version": "6.1.7601",
                    "os_string": "Windows 7 Professional N"
                },
                "message": "Agent cac3f82c-d320-4e6f-9ee7-e28b1f527d76 added successfully",
                "generated_ids": "cac3f82c-d320-4e6f-9ee7-e28b1f527d76",
                "vfense_status_code": 3200,
                "generic_status_code": 1010
            }
        """
        results = {}
        if isinstance(agent, Agent):
            agent_exist = self.properties
            invalid_fields = agent.get_invalid_fields()
            agent_data = agent.to_dict()
            last_agent_update = agent_data[AgentKeys.LastAgentUpdate]
            agent_data[AgentKeys.LastAgentUpdate] = (
                DbTime().epoch_time_to_db_time(
                    agent_data[AgentKeys.LastAgentUpdate]
                )
            )
            current_views = agent_data[AgentKeys.Views]
            views_are_valid, valid_view_names, invalid_view_names = (
                validate_view_names(current_views)
            )

            if views_are_valid and not invalid_fields and agent_exist:
                agent_data[AgentKeys.Views] = (
                    set(current_views).union(agent_exist[AgentKeys.Views])
                )
                agent_data[AgentKeys.DisplayName] = (
                    agent_exist[AgentKeys.DisplayName]
                )
                status_code, _, _, generated_ids = (
                    update_agent(agent_data)
                )
                if status_code == DbCodes.Replaced:
                    self.properties = self._agent_attributes()
                    self.add_hardware(agent_data[AgentKeys.Hardware])
                    if tags:
                        self.add_to_tags(tags)
                    agent_data[AgentKeys.AgentId] = self.agent_id
                    msg = (
                        'Agent {0} updated successfully'
                        .format(self.agent_id)
                    )
                    results[ApiResultKeys.GENERIC_STATUS_CODE] = (
                        GenericCodes.ObjectUpdated
                    )
                    results[ApiResultKeys.VFENSE_STATUS_CODE] = (
                        AgentResultCodes.StartUpSucceeded
                    )
                    results[ApiResultKeys.MESSAGE] = msg
                    results[ApiResultKeys.DATA] = agent_data
                    results[ApiResultKeys.GENERATED_IDS] = self.agent_id

                else:
                    msg = 'Failed to update agent {0}.'.format(self.agent_id)
                    results[ApiResultKeys.GENERIC_STATUS_CODE] = (
                        GenericFailureCodes.FailedToUpdateObject
                    )
                    results[ApiResultKeys.VFENSE_STATUS_CODE] = (
                        AgentFailureResultCodes.StartupFailed
                    )
                    results[ApiResultKeys.MESSAGE] = msg
                    results[ApiResultKeys.DATA] = agent_data

            elif invalid_fields:
                msg = (
                    'Failed to update agent {0}, invalid fields were passed'
                    .format(self.agent_id)
                )
                results[ApiResultKeys.GENERIC_STATUS_CODE] = (
                    GenericFailureCodes.FailedToUpdateObject
                )
                results[ApiResultKeys.VFENSE_STATUS_CODE] = (
                    AgentFailureResultCodes.StartupFailed
                )
                results[ApiResultKeys.MESSAGE] = msg
                results[ApiResultKeys.ERRORS] = invalid_fields
                results[ApiResultKeys.DATA] = agent_data

            elif not agent_exist:
                msg = (
                    'Failed to update, agent {0} does not exist'
                    .format(self.agent_id)
                )
                results[ApiResultKeys.GENERIC_STATUS_CODE] = (
                    GenericFailureCodes.InvalidId
                )
                results[ApiResultKeys.VFENSE_STATUS_CODE] = (
                    AgentFailureResultCodes.StartupFailed
                )
                results[ApiResultKeys.MESSAGE] = msg
                results[ApiResultKeys.DATA] = agent_data

            else:
                msg = (
                    'Failed to add agent, invalid views were passed: {0}.'
                    .format(', '.join(invalid_view_names))
                )
                results[ApiResultKeys.GENERIC_STATUS_CODE] = (
                    GenericFailureCodes.FailedToCreateObject
                )
                results[ApiResultKeys.VFENSE_STATUS_CODE] = (
                    AgentFailureResultCodes.NewAgentFailed
                )
                results[ApiResultKeys.MESSAGE] = msg
                results[ApiResultKeys.DATA] = agent_data

            results[ApiResultKeys.DATA][AgentKeys.LastAgentUpdate] = (
                last_agent_update
            )
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
            Dictionary
            >>>
        """
        results = {}
        agent_exist = self.properties
        if agent_exist:
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
                    results[ApiResultKeys.GENERIC_STATUS_CODE] = (
                        GenericCodes.ObjectCreated
                    )
                    results[ApiResultKeys.VFENSE_STATUS_CODE] = (
                        AgentCodes.ViewsAddedToAgent
                   )
                    results[ApiResultKeys.MESSAGE] = msg
                    results[ApiResultKeys.DATA] = views
                    results[ApiResultKeys.UPDATED_IDS] = [self.agent_id]

                else:
                    msg = (
                        'Failed to add viewstags: {0} to agent: {1}.'
                        .format(', '.join(views, self.agent_id))
                    )
                    results[ApiResultKeys.GENERIC_STATUS_CODE] = (
                        GenericFailureCodes.FailedToCreateObject
                    )
                    results[ApiResultKeys.VFENSE_STATUS_CODE] = (
                        AgentFailureCodes.FailedToAddViewsToAgent
                    )
                    results[ApiResultKeys.MESSAGE] = msg
                    results[ApiResultKeys.DATA] = views
                    results[ApiResultKeys.UNCHANGED_IDS] = [self.agent_id]

            elif views_exist_in_agent:
                msg = (
                    'Some of the views: {0} already exist for agent: {1}.'
                    .format(', '.join(views), self.agent_id)
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
                    'Invalid views: {0}.'.format(', '.join(views))
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
        results = {}
        agent_exist = self.properties
        if agent_exist:
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
                    results[ApiResultKeys.GENERIC_STATUS_CODE] = (
                        GenericCodes.ObjectDeleted
                    )
                    results[ApiResultKeys.VFENSE_STATUS_CODE] = (
                        AgentCodes.ViewsRemovedFromAgent
                   )
                    results[ApiResultKeys.MESSAGE] = msg
                    results[ApiResultKeys.UPDATED_IDS] = [self.agent_id]

                else:
                    msg = (
                        'Failed to remove views: {0} from agent: {1}.'
                        .format(', '.join(views), self.agent_id)
                    )
                    results[ApiResultKeys.GENERIC_STATUS_CODE] = (
                        GenericFailureCodes.FailedToDeleteObject
                    )
                    results[ApiResultKeys.VFENSE_STATUS_CODE] = (
                        AgentFailureCodes.FailedToRemoveViewsFromAgent
                    )
                    results[ApiResultKeys.MESSAGE] = msg
                    results[ApiResultKeys.UNCHANGED_IDS] = [self.agent_id]

            else:
                msg = (
                    'Invalid views: {0}.'.format(', '.join(views))
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
                "message": "Tag ids 0842c4c0-94ab-4fe4-9346-3b59fa53c316 were added successfully to agent cac3f82c-d320-4e6f-9ee7-e28b1f527d76",
                "vfense_status_code": 3013,
                "updated_ids": [
                    "cac3f82c-d320-4e6f-9ee7-e28b1f527d76"
                ],
                "generic_status_code": 1010
            }
        """
        results = {}
        agent_exist = self.properties
        tag_data = []
        if agent_exist:
            views = agent_exist[AgentKeys.Views]
            tags_are_valid, valid_tags, invalid_tags = (
                validate_tag_ids_in_views(tag_ids, views)
            )

            if tags_are_valid and not set(valid_tags).issubset(self.tags):
                for tag_id in tag_ids:
                    tag = fetch_tag(tag_id)
                    tag_data.append(
                        {
                            TagsPerAgentKeys.AgentId: self.agent_id,
                            TagsPerAgentKeys.TagId: tag_id,
                            TagsPerAgentKeys.TagName: (
                                tag[TagKeys.TagName]
                            ),
                            TagsPerAgentKeys.ViewName: (
                                tag[TagKeys.ViewName]
                            ),
                        }
                    )
                status_code, _, _, _ = add_tags_to_agent(tag_data)
                if status_code == DbCodes.Inserted:
                    self.properties = self._agent_attributes()
                    self.tags = self.get_tags()
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
                    results[ApiResultKeys.DATA] = tag_data
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
                    results[ApiResultKeys.DATA] = tag_data
                    results[ApiResultKeys.UNCHANGED_IDS] = [self.agent_id]

            elif set(valid_tags).issubset(self.tags):
                msg = (
                    'Some of the tag ids: {0} already exist for agent: {1}.'
                    .format(', '.join(tag_ids), self.agent_id)
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
            Dictionary
            >>>
            {
                "message": "Tag ids 0842c4c0-94ab-4fe4-9346-3b59fa53c316 were removed successfully from agent cac3f82c-d320-4e6f-9ee7-e28b1f527d76",
                "vfense_status_code": 3014,
                "updated_ids": [
                    "cac3f82c-d320-4e6f-9ee7-e28b1f527d76"
                ],
                "generic_status_code": 1012
            }
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
                    self.tags = self.get_tags()
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
                        .format(', '.join(tag_ids), self.agent_id)
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
            Dictionary
            >>>
        """
        results = {}
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

    @time_it
    def edit_production_level(self, production_level):
        """Change current or default view.
        Args:
            production_level (str): Production level you assigned to this
                agent.

        Basic Usage:
            >>> from vFense.agent.manager import AgentManager
            >>> agent_id = 'cac3f82c-d320-4e6f-9ee7-e28b1f527d76'
            >>> manager = AgentManager(agent_id)
            >>> manager.edit_production_level('Development')

        Returns:
            >>>
            {
                "vfense_status_code": 13001,
                "message": " User global_admin was updated - ",
                "data": [
                    {
                        "email": "shaolin_admin@shaolin.com"
                    }
                ],
                "updated_ids": [
                    "global_admin"
                ],
                "generic_status_code": 1008
            }
        """
        agent = Agent(production_level=production_level)
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
            >>>
            {
                "vfense_status_code": 13001,
                "message": " User global_admin was updated - ",
                "data": [
                    {
                        "email": "shaolin_admin@shaolin.com"
                    }
                ],
                "updated_ids": [
                    "global_admin"
                ],
                "generic_status_code": 1008
            }
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
            >>>
            {
                "vfense_status_code": 13001,
                "message": " User global_admin was updated - ",
                "data": [
                    {
                        "needs_reboot": true
                    }
                ],
                "updated_ids": [
                    "global_admin"
                ],
                "generic_status_code": 1008
            }
        """
        agent = Agent(needs_reboot=needs_reboot)
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
            >>>
            {
                "vfense_status_code": 13001,
                "message": " User global_admin was updated - ",
                "data": [
                    {
                        "last_agent_update": 22090992312
                    }
                ],
                "updated_ids": [
                    "global_admin"
                ],
                "generic_status_code": 1008
            }
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
            >>>
            {
                "vfense_status_code": 13001,
                "message": " Agent cac3f82c-d320-4e6f-9ee7-e28b1f527d76 was updated - ",
                "data": [
                    {
                        "token": "90sad8fg98j123"
                    }
                ],
                "updated_ids": [
                    "global_admin"
                ],
                "generic_status_code": 1008
            }
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
            Dictionary of the status of the operation.
            >>>
            {
                "vfense_status_code": 13001,
                "message": Agent global_admin was updated - ",
                "data": [
                    {
                        "display_name": "Web Server 1"
                    }
                ],
                "updated_ids": [
                    "cac3f82c-d320-4e6f-9ee7-e28b1f527d76"
                ],
                "generic_status_code": 1008
            }
        """

        agent_exist = self.properties
        results = {}
        data = {}
        results[ApiResultKeys.DATA] = []
        if agent_exist and isinstance(agent, Agent):
            invalid_fields = agent.get_invalid_fields()
            data = agent.to_dict_non_null()
            if not invalid_fields:
                if data.get(AgentKeys.LastAgentUpdate):
                    data[AgentKeys.LastAgentUpdate] = (
                        DbTime().epoch_time_to_db_time(
                            data[AgentKeys.LastAgentUpdate]
                        )
                    )
                object_status, _, _, _ = (
                    update_agent(self.agent_id, data)
                )
                if data.get(AgentKeys.LastAgentUpdate):
                    data[AgentKeys.LastAgentUpdate] = (
                        data[AgentKeys.LastAgentUpdate].to_epoch_time()
                    )

                if object_status == DbCodes.Replaced:
                    msg = 'Agent %s was updated - ' % (self.agent_id)
                    generic_status_code = GenericCodes.ObjectUpdated
                    vfense_status_code = AgentCodes.AgentUpdated
                    results[ApiResultKeys.UPDATED_IDS] = [self.agent_id]
                    results[ApiResultKeys.DATA] = [data]

                elif object_status == DbCodes.Unchanged:
                    msg = 'Agent %s was not updated - ' % (self.agent_id)
                    generic_status_code = GenericCodes.ObjectUnchanged
                    vfense_status_code = AgentCodes.AgentUnchanged
                    results[ApiResultKeys.UNCHANGED_IDS] = [self.agent_id]

            else:
                generic_status_code = GenericCodes.InvalidId
                vfense_status_code = AgentFailureCodes.FailedToUpdateAgent
                msg = 'Agent %s properties were invalid - ' % (self.agent_id)
                results[ApiResultKeys.UNCHANGED_IDS] = [self.agent_id]
                results[ApiResultKeys.ERRORS] = invalid_fields

        elif not isinstance(agent, Agent):
            generic_status_code = GenericCodes.InvalidId
            vfense_status_code = GenericFailureCodes.InvalidInstanceType
            msg = (
                'Agent {0} is not of instance Agent., instanced passed {1}'
                .format(self.agent_id, type(agent))
            )
            results[ApiResultKeys.UNCHANGED_IDS] = [self.agent_id]

        else:
            generic_status_code = GenericCodes.InvalidId
            vfense_status_code = AgentFailureCodes.AgentIdDoesNotExist
            msg = 'Agent %s does not exist - ' % (self.agent_id)
            results[ApiResultKeys.UNCHANGED_IDS] = [self.agent_id]

        results[ApiResultKeys.GENERIC_STATUS_CODE] = generic_status_code
        results[ApiResultKeys.VFENSE_STATUS_CODE] = vfense_status_code
        results[ApiResultKeys.MESSAGE] = msg

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
            Dictionary of the status of the operation.
            >>>
        """

        agent_exist = self.properties
        results = {}
        if agent_exist:
            delete_tag_ids_from_agent(self.agent_id, self.tags)
            delete_hardware_for_agent(self.agent_id)
            status_code, _, _, _ = delete_agent(self.agent_id)
            if status_code == DbCodes.Deleted:
                msg = 'Agent %s was deleted - ' % (self.agent_id)
                results[ApiResultKeys.MESSAGE] = msg
                results[ApiResultKeys.GENERIC_STATUS_CODE] = (
                    GenericCodes.ObjectDeleted
                )
                results[ApiResultKeys.VFENSE_STATUS_CODE] = (
                    AgentCodes.AgentDeleted
                )
                results[ApiResultKeys.DELETED_IDS] = [self.agent_id]

            else:
                msg = 'Invalid agent id %s' % (self.agent_id)
                results[ApiResultKeys.MESSAGE] = msg
                results[ApiResultKeys.GENERIC_STATUS_CODE] = (
                    GenericCodes.InvalidId
                )
                results[ApiResultKeys.VFENSE_STATUS_CODE] = (
                    GenericCodes.InvalidId
                )
                results[ApiResultKeys.UNCHANGED_IDS] = [self.agent_id]

        else:
            msg = 'Invalid agent id %s' % (self.agent_id)
            results[ApiResultKeys.MESSAGE] = msg
            results[ApiResultKeys.GENERIC_STATUS_CODE] = (
                GenericCodes.InvalidId
            )
            results[ApiResultKeys.VFENSE_STATUS_CODE] = (
                GenericCodes.InvalidId
            )
            results[ApiResultKeys.UNCHANGED_IDS] = [self.agent_id]

        return results
