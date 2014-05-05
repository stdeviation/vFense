import logging

import redis
from rq import Connection, Queue

from vFense.core.agent.agents import get_agent_info
from vFense.plugins.patching.os_apps.incoming_updates import \
   incoming_packages_from_agent 
from vFense.plugins.patching.custom_apps.custom_apps import \
    add_custom_app_to_agents

from vFense.plugins.patching.supported_apps.syncer import \
    get_all_supported_apps_for_agent, get_all_agent_apps_for_agent

from vFense.operations._constants import AgentOperations

rq_host = 'localhost'
rq_port = 6379
rq_db = 0
rq_pool = redis.StrictRedis(host=rq_host, port=rq_port, db=rq_db)
logging.config.fileConfig('/opt/TopPatch/conf/logging.config')
logger = logging.getLogger('rvapi')


class RvHandOff():

    def __init__(self, username, customer_name, uri, method,
                 agent_id, apps_data, agent_data=None,
                 oper_type='newagent', delete_afterwards=True):

        self.delete_afterwards = delete_afterwards
        self.customer_name = customer_name

        if not agent_data:
            agent_data = get_agent_info(agent_id)

        self.add_packages_from_agent(
            username, agent_id,
            agent_data, apps_data
        )

        if oper_type == AgentOperations.NEWAGENT:
            self.add_custom_apps(
                username, customer_name,
                uri, method, agent_id
            )
            self.add_supported_apps(agent_id)
            self.add_os_apps(agent_id)

        elif oper_type == AgentOperations.REFRESH_APPS:
            self.add_supported_apps(agent_id)
            self.add_os_apps(agent_id)

        elif oper_type == AgentOperations.AVAILABLE_AGENT_UPDATE:
            pass

    def add_custom_apps(self, username, customer_name,
                        uri, method, agent_id):
        rv_q = Queue('incoming_updates', connection=rq_pool)
        rv_q.enqueue_call(
            func=add_custom_app_to_agents,
            args=(
                username, customer_name,
                uri, method, None, agent_id
            ),
            timeout=3600
        )

    def add_supported_apps(self, agent_id):
        rv_q = Queue('incoming_updates', connection=rq_pool)
        rv_q.enqueue_call(
            func=get_all_supported_apps_for_agent,
            args=(
                agent_id,
            ),
            timeout=3600
        )

    def add_os_apps(self, agent_id):
        rv_q = Queue('incoming_updates', connection=rq_pool)
        rv_q.enqueue_call(
            func=get_all_agent_apps_for_agent,
            args=(
                agent_id,
            ),
            timeout=3600
        )


    def add_packages_from_agent(self, username, agent_id, agent_data, apps):
        rv_q = Queue('incoming_updates', connection=rq_pool)
        rv_q.enqueue_call(
            func=incoming_packages_from_agent,
            args=(
                username, agent_id,
                self.customer_name,
                agent_data['os_code'], agent_data['os_string'],
                apps, self.delete_afterwards
            ),
            timeout=3600
        )
