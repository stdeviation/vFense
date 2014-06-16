from vFense.core.agent._db_model import *
import logging
import logging.config
from vFense import VFENSE_LOGGING_CONFIG

from vFense.utils.common import *
from vFense.core._db_constants import DbTime
from vFense.core.agent import Agent
from vFense.core.agent.agents import update_agent_field, get_agent_info
from vFense.core.agent._db import fetch_agent
from vFense.core.agent import Agent
from vFense.core.view.views import validate_view_names
from vFense.core.tag.tagManager import get_tags_by_agent_id, delete_agent_from_all_tags
from vFense.core.tag.tagManager import delete_agent_from_all_tags
from vFense.core.tag import *
from vFense.db.client import db_create_close, r
from vFense.plugins.patching._constants import CommonAppKeys
from vFense.plugins.patching._db_model import *
from vFense.plugins.patching.patching import (
    remove_all_app_data_for_agent,
    update_all_app_data_for_agent
)
from vFense.plugins.patching._db_stats import  get_all_app_stats_by_agentid
from vFense.errorz.error_messages import GenericResults
from vFense.server.hierarchy import Collection
import redis
from rq import Queue

rq_host = 'localhost'
rq_port = 6379
rq_db = 0
rq_pool = redis.StrictRedis(host=rq_host, port=rq_port, db=rq_db)

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
                        lambda x: x[TagsKey.TagId],
                        self.properties.get(AgentKeys.Tags, [])
                    )
                )
            else:
                self.tags = []
        else:
            self.tags = []

    def _agent_attributes(self):
        agent_data = fetch_agent(agent_id)

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
                insert_agent_data(agent_data)
            )
            if status_code == DbCodes.Inserted:
                agent_id = generated_ids.pop()
                Hardware().add(agent_id, agent_data[AgentKeys.Hardware])
                agent_data[AgentKeys.AgentId] = agent_id
                msg = 'new agent_operation succeeded'
                results[ApiResultKeys.GENERIC_STATUS_CODE] = (
                    GenericCodes.ObjectCreated
                )
                results[ApiResultKeys.VFENSE_STATUS_CODE] = (
                    AgentResultCodes.NewAgentSucceeded
                )
                results[ApiResultKeys.MESSAGE] = msg
                results[ApiResultKeys.DATA] = [agent_data]
                results[ApiResultKeys.GENERATED_IDS] = [agent_id]

