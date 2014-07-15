from vFense.core.status_codes import GenericCodes, GenericFailureCodes

class AgentCodes(GenericCodes):
    NewAgent = 3001
    NewAgentFailed = 3002
    CheckIn = 3003
    CheckInFailed = 3004
    Startup = 3005
    StartupFailed = 3006
    InstallUpdateResults = 3007
    InstallSupportedAppResults = 3008
    InstallCustomAppResults = 3009
    InstallAgentAppResults = 3010
    AgentsDeleted = 3011
    AgentsUpdated = 3012
    TagsAddedToAgent = 3013
    TagsRemovedFromAgent = 3014
    HardwareAddedToAgent = 3015
    AgentDeleted = 3016
    AgentUpdated = 3017
    AgentUnchanged = 3018
    ViewsAddedToAgent = 3019
    ViewsRemovedFromAgent = 3020
    ViewsRemovedFromAgents = 3021
    Disabled = 3022


class AgentFailureCodes(GenericFailureCodes):
    AgentsFailedToDelete = 3500
    AgentsFailedToUpdate = 3501
    AgentsDoNotExist = 3502
    AgentsDoesNotExist = 3503
    AgentsExist = 3504
    FailedToAddTagsToAgent = 3505
    FailedToRemoveTagsFromAgent = 3506
    FailedToAddHardwareToAgent = 3507
    FailedToDeleteAgent = 3508
    FailedToUpdateAgent = 3509
    AgentIdDoesNotExist = 3510
    FailedToAddViewsToAgent = 3511
    FailedToRemoveViewsFromAgent = 3512
    FailedToAddViewsToAgents = 3513
    FailedToRemoveViewsFromAgents = 3514
    FailedToDeleteAgents = 3515
