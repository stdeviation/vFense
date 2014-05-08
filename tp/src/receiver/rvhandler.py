import logging

import redis
from rq import Connection, Queue

from vFense.core.agent.agents import get_agent_info
from vFense.plugins.patching.apps.incoming_apps import \
   incoming_applications_from_agent 
from vFense.plugins.patching.apps.custom_apps.custom_apps import \
    add_custom_app_to_agents
from vFense.plugins.patching.apps.supported_apps.syncer import \
    get_all_supported_apps_for_agent
from vFense.plugins.patching.apps.vFense_apps.vFense_apps import \
    add_vFense_apps_to_agent

#from vFense.plugins.patching.apps.supported_apps.syncer import \
#    get_all_supported_apps_for_agent, get_all_vFense_apps_for_agent

#from vFense.operations._constants import AgentOperations

RQ_HOST = 'localhost'
RQ_PORT = 6379
RQ_DB = 0
RQ_POOL = redis.StrictRedis(host=RQ_HOST, port=RQ_PORT, db=RQ_DB)

logging.config.fileConfig('/opt/TopPatch/conf/logging.config')
logger = logging.getLogger('rvapi')


class RvHandOff():

    #def __init__(self, username, customer_name, uri, method,
    #             agent_id, apps_data, agent_data=None,
    #             oper_type=AgentOperations.NEW_AGENT, delete_afterwards=True):

    def __init__(self, agent_data=None, delete_afterwards=True):

        self.delete_afterwards = delete_afterwards
        self.agent_data = agent_data

        #if not self.agent_data:
        #    self.agent_data = get_agent_info(agent_id)

        #self.add_packages_from_agent(username, agent_id, agent_data, apps_data)

        #if oper_type == AgentOperations.NEW_AGENT:
        #    self.add_custom_apps(username, customer_name, uri, method, agent_id)
        #    self.add_supported_apps(agent_id)

        #elif oper_type == AgentOperations.REFRESH_APPS:
        #    self.add_supported_apps(agent_id)

        #elif oper_type == AgentOperations.AVAILABLE_AGENT_UPDATE:
        #    self.add_vFense_apps(agent_id)

    def new_agent_operation(self, username, customer_name, uri, method,
            agent_id, apps_data):

        self._add_applications_from_agent(
            username, customer_name, agent_id, self.agent_data, apps_data
        )
        self._add_custom_apps(username, customer_name, uri, method, agent_id)
        self._add_supported_apps(agent_id)

    def startup_operation(self, username, customer_name, uri, method,
            agent_id, apps_data):
        self.refresh_apps_operation(
            username, customer_name, uri, method, agent_id, apps_data
        )

    def refresh_apps_operation(self, username, customer_name, uri, method,
            agent_id, apps_data):

        self._add_applications_from_agent(
            username, customer_name, agent_id, self.agent_data, apps_data
        )
        self._add_supported_apps(agent_id)

    def available_agent_update_operation(self, agent_id, app_data):
        self._add_vFense_apps(agent_id, app_data)

    def _add_custom_apps(self, username, customer_name, uri, method, agent_id):
        rv_q = Queue('incoming_updates', connection=RQ_POOL)
        rv_q.enqueue_call(
            func=add_custom_app_to_agents,
            args=(
                username,
                customer_name,
                uri,
                method,
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

    def _add_vFense_apps(self, agent_id, apps_data):
        rv_q = Queue('incoming_updates', connection=RQ_POOL)
        rv_q.enqueue_call(
            func=add_vFense_apps_to_agent,
            args=(
                agent_id,
                apps_data
            ),
            timeout=3600
        )

    def _add_applications_from_agent(self, username, customer_name, agent_id,
            agent_data, apps):
        rv_q = Queue('incoming_updates', connection=RQ_POOL)
        rv_q.enqueue_call(
            func=incoming_applications_from_agent,
            args=(
                username,
                agent_id,
                customer_name,
                agent_data['os_code'],
                agent_data['os_string'],
                apps,
                self.delete_afterwards
            ),
            timeout=3600
        )
