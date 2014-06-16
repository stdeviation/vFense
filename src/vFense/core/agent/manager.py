from vFense.core.agent._db_model import *
import logging
import logging.config
from vFense import VFENSE_LOGGING_CONFIG

from vFense.utils.common import *
from vFense.core.agent.agents import update_agent_field, get_agent_info
from vFense.core.agent._db import fetch_agent
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


    #def new(agent):
