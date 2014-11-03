from vFense.core.agent._constants import agent_id
from vFense.core.api.agent import AgentHandler, AgentsHandler, AgentTagHandler
from vFense.receiver.api.core.result_uris import AgentResultURIs
from vFense.plugins.patching.api.os_apps import AgentIdAppsHandler
from vFense.core.api.agent_operations import AgentOperationsHandler
from vFense.plugins.patching.api.stats_api import (
    AgentSeverityHandler, AgentOsAppsOverTimeHandler
)

def api_handlers():
    handlers = [
        ##### Agent API Handlers
        (r"/api/v1/agent/({0})?".format(agent_id()), AgentHandler),
        (r"/api/v1/agent/({0})/graphs/bar/severity?".format(agent_id()),
            AgentSeverityHandler),
        (r"/api/v1/agent/({0})/graphs/column/range/apps/os?".format(agent_id()),
            AgentOsAppsOverTimeHandler),
        (r"/api/v1/agent/({0})/tag?".format(agent_id()),
            AgentTagHandler),
        (r"/api/v1/agent/({0})/apps/(os|agentupdates|custom|supported)?".format(agent_id()),
            AgentIdAppsHandler),
        (r"/api/v1/agent/({0})/operations?".format(agent_id()),
            AgentOperationsHandler),
        (r"/api/v1/agent/({0})/uris/response?".format(agent_id()),
            AgentResultURIs),
        ##### Agents API Handlers
        (r"/api/v1/agents", AgentsHandler)
    ]
    return handlers
