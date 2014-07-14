from vFense.core.status_codes import GenericCodes, GenericFailureCodes


class GroupCodes(GenericCodes):
    GroupCreated = 12000
    GroupUpdated = 12001
    GroupDeleted = 12002
    GroupUnchanged = 12003
    GroupsAddedToUser = 12004
    RemovedUsersFromGroup = 12005
    RemovedViewsFromGroup = 12006
    AddedViewsToGroup = 12007
    AddedUsersToGroup = 12008
    PermissionsUpdated = 12009
    PermissionsUnchanged = 12010
    GroupsDeleted = 12011
    GroupsUnchanged = 12012


class GroupFailureCodes(GenericFailureCodes):
    GroupIdExists = 12500
    InvalidPermissions = 12501
    FailedToRemoveGroup = 12502
    FailedToRemoveGroupFromUser = 12503
    FailedToCreateGroup = 12504
    FailedToAddGroupToUser = 12505
    FailedToUpdateGroup = 12506
    InvalidGroupName = 12507
    InvalidGroupId = 12508
    GroupExistForUser = 12509
    GroupDoesNotExistForUser = 12510
    CantRemoveAdminFromGroup = 12511
    UsersExistForGroup = 12512
    UsersDoNotExistForGroup = 12513
    CantRemoveGlobalUsersFromGroup = 12514
    InvalidFields = 12515
    CantRemoveViewsFromGlobalGroup = 12516
    CantAddUsersToGlobalGroup = 12517
    CantAddLocalUsersToGlobalGroup = 12518
    InvalidValue = 12519
    FailedToDeleteAllGroups = 12520



