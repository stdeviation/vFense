from vFense.core.agent._constants import agent_id
from vFense.plugins.patching.receiver.api.refresh_apps import (
    RefreshAppsV1, RefreshAppsV2
)
from vFense.plugins.patching.receiver.api.app_results import (
    AppsResultsV2, CustomAppsResultsV2, SupportedAppsResultsV2,
    vFenseAppsResultsV2, UninstallResultsV2
)
from vFense.plugins.patching.receiver.api.results import (
    InstallOsAppsResults, InstallCustomAppsResults,
    InstallSupportedAppsResults, InstallAgentAppsResults,
    UninstallAppsResults
)
from vFense.plugins.patching.receiver.api.agent_update import (
    AgentUpdateHandlerV1, AgentUpdateHandlerV2
)

def api_handlers():
    handlers = [
        #v1 APIS for application results
        (r"/rvl/v1/({0})/rv/updatesapplications/?".format(agent_id()),
            RefreshAppsV1),
        (r"/rvl/v1/({0})/rv/available_agent_update/?".format(agent_id()),
            AgentUpdateHandlerV1),
        (r"/rvl/v1/({0})/rv/results/install/apps/os?".format(agent_id()),
            InstallOsAppsResults),
        (r"/rvl/v1/({0})/rv/results/install/apps/custom?".format(agent_id()),
            InstallCustomAppsResults),
        (r"/rvl/v1/({0})/rv/results/install/apps/supported?".format(agent_id()),
            InstallSupportedAppsResults),
        (r"/rvl/v1/({0})/rv/results/install/apps/agent?".format(agent_id()),
            InstallAgentAppsResults),
        (r"/rvl/v1/({0})/rv/results/uninstall?".format(agent_id()),
            UninstallAppsResults),

        (r"/rvl/v2/apps/available_agent_update/?".format(agent_id()),
            AgentUpdateHandlerV2),

        #v2 APIS for applications results
        (r"/rvl/v2/({0})/apps/results/install/os?".format(agent_id()),
            AppsResultsV2),
        (r"/rvl/v2/({0})/apps/results/install/custom?".format(agent_id()),
            CustomAppsResultsV2),
        (r"/rvl/v2/({0})/apps/results/install/supported?".format(agent_id()),
            SupportedAppsResultsV2),
        (r"/rvl/v2/({0})/apps/results/install/agent?".format(agent_id()),
            vFenseAppsResultsV2),
        (r"/rvl/v2/({0})/apps/results/uninstall?".format(agent_id()),
            UninstallResultsV2),
        (r"/rvl/v2/({0})/apps/results/refresh_apps/?".format(agent_id()),
            RefreshAppsV2),
        (r"/rvl/v2/({0})/apps/available_agent_update/?".format(agent_id()),
            AgentUpdateHandlerV2),
    ]
    return handlers
