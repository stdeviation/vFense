import logging

import redis
from rq import Connection, Queue

from vFense import VFENSE_LOGGING_CONFIG
from vFense.core.agent._db import fetch_agent
from vFense.plugins.patching.apps.manager import (
   incoming_applications_from_agent
)
from vFense.plugins.patching.apps.custom_apps.custom_apps import (
    add_custom_app_to_agents
)
from vFense.plugins.patching.apps.supported_apps.syncer import (
    get_all_supported_apps_for_agent
)


RQ_HOST = 'localhost'
RQ_PORT = 6379
RQ_DB = 0
RQ_POOL = redis.StrictRedis(host=RQ_HOST, port=RQ_PORT, db=RQ_DB)

logging.config.fileConfig(VFENSE_LOGGING_CONFIG)
logger = logging.getLogger('rvapi')


class RvHandOff():

    def __init__(self, delete_afterwards=True):

        self.delete_afterwards = delete_afterwards

    def _get_agent_data(self, agent_id):
        return fetch_agent(agent_id)

    def _add_custom_apps(self, agent_id):
        rv_q = Queue('incoming_updates', connection=RQ_POOL)
        rv_q.enqueue_call(
            func=add_custom_app_to_agents,
            args=(
                None,
                agent_id
            ),
            timeout=3600
        )

    def _add_supported_apps(self, agent_id):
        rv_q = Queue('incoming_updates', connection=RQ_POOL)
        rv_q.enqueue_call(
            func=get_all_supported_apps_for_agent,
            args=(
                agent_id,
            ),
            timeout=3600
        )

    def _add_applications_from_agent(self, agent_id, apps):

        rv_q = Queue('incoming_updates', connection=RQ_POOL)
        rv_q.enqueue_call(
            func=incoming_applications_from_agent,
            args=(
                agent_id,
                apps,
                self.delete_afterwards,
            ),
            timeout=3600
        )

    def new_agent_operation(self, agent_id, apps_data):

        self._add_applications_from_agent(
            agent_id,
            apps_data,
            self.delete_afterwards,
        )
        self._add_custom_apps(
            agent_id
        )

        self._add_supported_apps(agent_id)

    def startup_operation(self, agent_id, apps_data, agent_data=None):

        if not agent_data:
            agent_data = self._get_agent_data(agent_id)

        self.refresh_apps_operation(agent_id, apps_data, agent_data)

    def refresh_apps_operation(self, agent_id, apps_data):

        self._add_applications_from_agent(
            agent_id,
            apps_data,
            self.delete_afterwards,
        )
        self._add_supported_apps(agent_id)

    def available_agent_update_operation(self, agent_id, app_data):
        apps_data = [app_data]
        self._add_applications_from_agent(
            agent_id,
            apps_data,
            self.delete_afterwards,
        )
