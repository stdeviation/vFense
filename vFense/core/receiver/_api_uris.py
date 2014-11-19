from vFense.core.agent._constants import agent_id
from vFense.core.receiver.api.generics import ValidateToken
from vFense.core.api.base import (
    RootHandler, RvlLoginHandler, RvlLogoutHandler
)
from vFense.core.receiver.api.checkin import CheckInV1, CheckInV2
from vFense.core.receiver.api.newagent import NewAgentV1, NewAgentV2
from vFense.core.receiver.api.startup import StartUpV1, StartUpV2
from vFense.core.receiver.api.stats import (
    UpdateMonitoringStatsV1, UpdateMonitoringStatsV2
)
from vFense.core.receiver.api.result_uris import (
    ResultURIs, ResultURIsV2
)
from vFense.core.receiver.api.results import (
    RebootResultsV1, RebootResultsV2, ShutdownResultsV1, ShutdownResultsV2
)

def api_handlers():
    handlers = [
        #Login and Logout Operations
        (r"/rvl/?", RootHandler),
        (r"/rvl/login/?", RvlLoginHandler),
        (r"/rvl/logout/?", RvlLogoutHandler),
        (r"/rvl/validate?", ValidateToken),
        #Operations for the New Core Plugin
        (r"/rvl/v1/core/newagent/?", NewAgentV1),
        (r"/rvl/v1/core/uris/response?", ResultURIs),
        (r"/rvl/v1/({0})/core/startup/?".format(agent_id()), StartUpV1),
        (r"/rvl/v1/({0})/core/uris/response/?".format(agent_id()), ResultURIs),
        (r"/rvl/v1/({0})/core/checkin/?".format(agent_id()), CheckInV1),
        (r"/rvl/v1/({0})/core/results/reboot/?".format(agent_id()), RebootResultsV1),
        (r"/rvl/v1/({0})/core/results/shutdown/?".format(agent_id()), ShutdownResultsV1),
        (r"/rvl/v1/({0})/stats/monitordata/?".format(agent_id()), UpdateMonitoringStatsV1),
        #v2 APIS
        #Operations for the New Core Plugin
        (r"/rvl/v2/core/newagent/?", NewAgentV2),
        (r"/rvl/v2/core/validate_token/?", ValidateToken),
        (r"/rvl/v2/core/uris/response?", ResultURIsV2),
        (r"/rvl/v2/({0})/core/startup".format(agent_id()), StartUpV2),
        (r"/rvl/v2/({0})/core/uris/response/?".format(agent_id()), ResultURIsV2),
        (r"/rvl/v2/({0})/core/checkin/?".format(agent_id()), CheckInV2),
        (r"/rvl/v2/({0})/core/results/reboot/?".format(agent_id()), RebootResultsV2),
        (r"/rvl/v2/({0})/core/results/shutdown/?".format(agent_id()), ShutdownResultsV2),
        (r"/rvl/v2/({0})/core/stats/monitordata/?".format(agent_id()), UpdateMonitoringStatsV2)
    ]
    return handlers
