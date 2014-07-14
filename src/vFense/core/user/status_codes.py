from vFense.core.status_codes import GenericCodes, GenericFailureCodes


class UserCodes(GenericCodes):
    UserCreated = 13000
    UserUpdated = 13001
    UserDeleted = 13002
    UserUnchanged = 13003
    PasswordChanged = 13004
    UsersAddedToView = 13005
    UsersRemovedFromView = 13006
    UsersAddedToGroup = 13007
    UsersRemovedFromGroup = 13008
    UsersDeleted = 13009
    UsersUnchanged = 13010


class UserFailureCodes(GenericFailureCodes):
    UserNameExists = 13500
    UserNameDoesNotExist = 13501
    FailedToCreateUser = 13502
    FailedToRemoveUser = 13503
    FailedToUpdateUser = 13504
    InvalidUserName = 13505
    InvalidPassword = 13506
    WeakPassword = 13507
    NewPasswordSameAsOld = 13508
    AdminUserCanNotBeDeleted = 13509
    FailedToAddUsersToView = 13510
    FailedToRemoveUsersFromView = 13511
    CantDeleteAdminFromView = 13512
    CantDeleteAdminUser = 13513
    FailedToAddUsersToGroup = 13514
    FailedToRemoveUsersFromGroup = 13515
    CantAddLocalGroupToGlobalUser = 13516
    CantAddGlobalGroupToLocalUser = 13517
    FailedToDeleteAllUsers = 13518



