from vFense.core.status_codes import GenericCodes, GenericFailureCodes

class ViewCodes(GenericCodes):
    ViewCreated = 14000
    ViewUpdated = 14001
    ViewDeleted = 14002
    ViewUnchanged = 14003
    ViewsAddedToUser = 14004
    ViewsRemovedFromUser = 14005
    ViewsAddedToGroup = 14006
    ViewsRemovedFromGroup = 14007
    ViewsUnchanged = 14008
    ViewsDeleted = 14009
    ViewsRemovedFromAgent = 14010
    AgentsAddedToView = 14011
    AgentsRemovedFromView = 14012
    AgentsMovedToView = 14013
    ValidPreviousToken = 14014


class ViewFailureCodes(GenericFailureCodes):
    ViewExists = 14500
    ViewDoesNotExist = 14501
    FailedToCreateView = 14502
    FailedToRemoveView = 14503
    FailedToRemoveUserFromView = 14504
    FailedToUpdateView = 14505
    InvalidViewName = 14506
    UsersExistForView = 14507
    UsersDoNotExistForView = 14508
    CantDeleteDefaultView = 124509
    InvalidNetworkThrottle = 124509
    InvalidCpuThrottle = 124510
    InvalidOperationTTL = 124511
    InvalidServerQueueThrottle = 124512
    InvalidAgentQueueThrottle = 124513
    InvalidFields = 124514
    InvalidValue = 124515
    GroupsDoNotExistInThisView = 124516
    FailedToDeleteAllViews = 124517
    AgentsDoNotExistForView = 14518
    CantRemoveAgentsFromGlobalView = 14519
    InvalidToken = 14520
    InvalidTimeZone = 14521



