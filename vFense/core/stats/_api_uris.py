from vFense.core.agent._constants import agent_id
from vFense.core.api.stats import AgentStats

def api_handlers():
    handlers = [
        ##### Stats API Handlers
        (r"/api/v1/agent/({0})/stats/(cpu|memory|filesystem)?"
         .format(agent_id()), AgentStats)
    ]
    return handlers
