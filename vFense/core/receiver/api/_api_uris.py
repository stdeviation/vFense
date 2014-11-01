

def api_handlers():
    handlers = [
        #Operations for the New Core Plugin
        (r"/rvl/v1/core/newagent/?", NewAgentV1),
        (r"/rvl/v1/core/uris/response?", ResultURIs),
        (r"/rvl/v1/([a-f0-9]{8}-[a-f0-9]{4}-4[a-f0-9]{3}-[a-f0-9]{4}-[a-f0-9]{12})/core/startup/?", StartUpV1),
        (r"/rvl/v1/([a-f0-9]{8}-[a-f0-9]{4}-4[a-f0-9]{3}-[a-f0-9]{4}-[a-f0-9]{12})/core/uris/response/?", ResultURIs),
        (r"/rvl/v1/([a-f0-9]{8}-[a-f0-9]{4}-4[a-f0-9]{3}-[a-f0-9]{4}-[a-f0-9]{12})/core/checkin/?", CheckInV1),
        (r"/rvl/v1/([a-f0-9]{8}-[a-f0-9]{4}-4[a-f0-9]{3}-[a-f0-9]{4}-[a-f0-9]{12})/core/results/reboot/?",
                RebootResultsV1),
        (r"/rvl/v1/([a-f0-9]{8}-[a-f0-9]{4}-4[a-f0-9]{3}-[a-f0-9]{4}-[a-f0-9]{12})/core/results/shutdown/?",
                ShutdownResultsV1),

        #Patching Plugin
        (r"/rvl/v1/([a-f0-9]{8}-[a-f0-9]{4}-4[a-f0-9]{3}-[a-f0-9]{4}-[a-f0-9]{12})/rv/updatesapplications/?", UpdateApplicationsV1),
        (r"/rvl/v1/([a-f0-9]{8}-[a-f0-9]{4}-4[a-f0-9]{3}-[a-f0-9]{4}-[a-f0-9]{12})/rv/available_agent_update/?", AgentUpdateHandler),

        #New Operations for the New RV Plugin
        (r"/rvl/v1/([a-f0-9]{8}-[a-f0-9]{4}-4[a-f0-9]{3}-[a-f0-9]{4}-[a-f0-9]{12})/rv/results/install/apps/os?", InstallOsAppsResults),
        (r"/rvl/v1/([a-f0-9]{8}-[a-f0-9]{4}-4[a-f0-9]{3}-[a-f0-9]{4}-[a-f0-9]{12})/rv/results/install/apps/custom?", InstallCustomAppsResults),
        (r"/rvl/v1/([a-f0-9]{8}-[a-f0-9]{4}-4[a-f0-9]{3}-[a-f0-9]{4}-[a-f0-9]{12})/rv/results/install/apps/supported?", InstallSupportedAppsResults),
        (r"/rvl/v1/([a-f0-9]{8}-[a-f0-9]{4}-4[a-f0-9]{3}-[a-f0-9]{4}-[a-f0-9]{12})/rv/results/install/apps/agent?", InstallAgentAppsResults),
        (r"/rvl/v1/([a-f0-9]{8}-[a-f0-9]{4}-4[a-f0-9]{3}-[a-f0-9]{4}-[a-f0-9]{12})/rv/results/uninstall?", UninstallAppsResults),


        #v2 APIS for applications results
        (r"/rvl/v2/([a-f0-9]{8}-[a-f0-9]{4}-4[a-f0-9]{3}-[a-f0-9]{4}-[a-f0-9]{12})/apps/results/install/os?", AppsResultsV2),
        (r"/rvl/v2/([a-f0-9]{8}-[a-f0-9]{4}-4[a-f0-9]{3}-[a-f0-9]{4}-[a-f0-9]{12})/apps/results/install/custom?", CustomAppsResultsV2),
        (r"/rvl/v2/([a-f0-9]{8}-[a-f0-9]{4}-4[a-f0-9]{3}-[a-f0-9]{4}-[a-f0-9]{12})/apps/results/install/supported?", SupportedAppsResultsV2),
        (r"/rvl/v2/([a-f0-9]{8}-[a-f0-9]{4}-4[a-f0-9]{3}-[a-f0-9]{4}-[a-f0-9]{12})/apps/results/install/agent?", vFenseAppsResultsV2),
        (r"/rvl/v2/([a-f0-9]{8}-[a-f0-9]{4}-4[a-f0-9]{3}-[a-f0-9]{4}-[a-f0-9]{12})/apps/results/uninstall?", UninstallResultsV2),
        (r"/rvl/v2/([a-f0-9]{8}-[a-f0-9]{4}-4[a-f0-9]{3}-[a-f0-9]{4}-[a-f0-9]{12})/apps/results/refresh_apps/?", RefreshAppsV2),
        (r"/rvl/v2/([a-f0-9]{8}-[a-f0-9]{4}-4[a-f0-9]{3}-[a-f0-9]{4}-[a-f0-9]{12})/apps/available_agent_update/?", AgentUpdateHandlerV2),


        #v2 APIS
        #Operations for the New Core Plugin
        (r"/rvl/v2/core/newagent/?", NewAgentV2),
        (r"/rvl/v2/core/validate_token/?", ValidateToken),
        (r"/rvl/v2/core/uris/response?", ResultURIsV2),
        (r"/rvl/v2/apps/available_agent_update/?", AgentUpdateHandlerV2),
        (r"/rvl/v2/([a-f0-9]{8}-[a-f0-9]{4}-4[a-f0-9]{3}-[a-f0-9]{4}-[a-f0-9]{12})/core/startup", StartUpV2),
        (r"/rvl/v2/([a-f0-9]{8}-[a-f0-9]{4}-4[a-f0-9]{3}-[a-f0-9]{4}-[a-f0-9]{12})/core/uris/response/?", ResultURIsV2),
        (r"/rvl/v2/([a-f0-9]{8}-[a-f0-9]{4}-4[a-f0-9]{3}-[a-f0-9]{4}-[a-f0-9]{12})/core/checkin/?", CheckInV2),
        (r"/rvl/v2/([a-f0-9]{8}-[a-f0-9]{4}-4[a-f0-9]{3}-[a-f0-9]{4}-[a-f0-9]{12})/core/results/reboot/?", RebootResultsV2),
        (r"/rvl/v2/([a-f0-9]{8}-[a-f0-9]{4}-4[a-f0-9]{3}-[a-f0-9]{4}-[a-f0-9]{12})/core/results/shutdown/?", ShutdownResultsV2)
    ]
    return handlers
