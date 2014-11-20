from vFense.core.agent._constants import agent_id
from vFense.core.stats.api.agent import GetAgentStats

def api_handlers():
    handlers = [
        ##### Stats API Handlers
        (r"/api/v1/agent/({0})/stats/(cpu|memory|filesystem)?"
         .format(agent_id()), GetAgentStats)
    ]
    return handlers
