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
        (r"/api/v1/agent/([a-f0-9]{8}-[a-f0-9]{4}-4[a-f0-9]{3}-[a-f0-9]{4}-[a-f0-9]{12})?", AgentHandler),
        (r"/api/v1/agent/([a-f0-9]{8}-[a-f0-9]{4}-4[a-f0-9]{3}-[a-f0-9]{4}-[a-f0-9]{12})/graphs/bar/severity?",AgentSeverityHandler),
        (r"/api/v1/agent/([a-f0-9]{8}-[a-f0-9]{4}-4[a-f0-9]{3}-[a-f0-9]{4}-[a-f0-9]{12})/graphs/column/range/apps/os?", AgentOsAppsOverTimeHandler),
        (r"/api/v1/agent/([a-f0-9]{8}-[a-f0-9]{4}-4[a-f0-9]{3}-[a-f0-9]{4}-[a-f0-9]{12})/tag?", AgentTagHandler),
        (r"/api/v1/agent/([a-f0-9]{8}-[a-f0-9]{4}-4[a-f0-9]{3}-[a-f0-9]{4}-[a-f0-9]{12})/apps/(os|agentupdates|custom|supported)?", AgentIdAppsHandler),
        (r"/api/v1/agent/([a-f0-9]{8}-[a-f0-9]{4}-4[a-f0-9]{3}-[a-f0-9]{4}-[a-f0-9]{12})/operations?", AgentOperationsHandler),
        (r"/api/v1/agent/([a-f0-9]{8}-[a-f0-9]{4}-4[a-f0-9]{3}-[a-f0-9]{4}-[a-f0-9]{12})/uris/response?", AgentResultURIs),

        ##### Agents API Handlers
        (r"/api/v1/agents", AgentsHandler)
    ]
    return handlers
