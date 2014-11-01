import os
import sys
import importlib
import traceback
from vFense.receiver.api.core.newagent import NewAgentV1, NewAgentV2
from vFense.receiver.api.core.checkin import CheckInV1, CheckInV2
from vFense.receiver.api.core.startup import StartUpV1, StartUpV2
from vFense.receiver.api.core.result_uris import (
    ResultURIs, ResultURIsV2
)
from vFense.receiver.api.core.results import (
    RebootResultsV1, ShutdownResultsV1, RebootResultsV2, ShutdownResultsV2
)

from vFense.receiver.api.rv.results import (
    InstallOsAppsResults, InstallCustomAppsResults,
    InstallSupportedAppsResults, InstallAgentAppsResults,
    UninstallAppsResults
)

from vFense.receiver.api.rv.app_results import (
    AppsResultsV2, CustomAppsResultsV2,
    SupportedAppsResultsV2, vFenseAppsResultsV2,
    UninstallResultsV2
)
from vFense.receiver.api.rv.updateapplications import UpdateApplicationsV1
from vFense.receiver.api.rv.refresh_apps import RefreshAppsV2
from vFense.receiver.api.rv.agent_update import (
    AgentUpdateHandler, AgentUpdateHandlerV2
)
from vFense.core.api.reports_api import (
    AgentsOsDetailsHandler, AgentsHardwareDetailsHandler,
    AgentsCPUDetailsHandler, AgentsMemoryDetailsHandler,
    AgentsDiskDetailsHandler,AgentsNetworkDetailsHandler
)

class CoreLoader():

    def get_core_listener_api_handlers(self):
        handlers = [

        ]

        return handlers

    def get_core_web_api_handlers(self):
        handlers = [

            ##### Reports Api
            (r"/api/v1/reports/osdetails?", AgentsOsDetailsHandler),
            (r"/api/v1/reports/hardwaredetails?",AgentsHardwareDetailsHandler),
            (r"/api/v1/reports/cpudetails?",AgentsCPUDetailsHandler),
            (r"/api/v1/reports/memorydetails?",AgentsMemoryDetailsHandler),
            (r"/api/v1/reports/diskdetails?",AgentsDiskDetailsHandler),
            (r"/api/v1/reports/networkdetails?",AgentsNetworkDetailsHandler),

        ]

        return handlers
