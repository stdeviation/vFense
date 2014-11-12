class GenericCodes(object):
    InformationRetrieved = 1001
    CouldNotRetrieveInformation = 1002
    IncorrectArguments = 1003
    DoesNotExist = 1004
    CouldNotBeDeleted = 1005
    InvalidId = 1006
    InvalidFilter = 1007
    ObjectUpdated = 1008
    UpdateFailed = 1009
    ObjectCreated = 1010
    ObjectExists = 1011
    ObjectDeleted = 1012
    SomethingBroke = 1013
    FileUploaded = 1014
    FileFailedToUpload = 1015
    FileDoesNotExist = 1016
    ObjectUnchanged = 1017
    PermissionGranted = 1018
    PermissionDenied = 1019
    InvalidPermission = 1020
    AuthorizationGranted = 1021
    AuthorizationDenied = 1022
    MissingUsername = 1023
    MissingPassword = 1024
    InvalidValue = 1025
    InvalidFields = 1026
    ObjectsDeleted = 1027
    ObjectsUnchanged = 1028
    ObjectsUpdated = 1029


class GenericFailureCodes(object):
    FailedToCreateObject = 1500
    FailedToUpdateObject = 1501
    FailedToDeleteObject = 1502
    FailedToRetrieveObject = 1503
    DataIsEmpty = 1504
    InvalidSortKey = 1505
    InvalidFilterKey = 1506
    InvalidId = 1507
    InvalidPlugin = 1508
    InvalidInstanceType = 1509
    InvalidFields = 1510
    FailedToDeleteAllObjects = 1511
    FailedToUpdateAllObjects = 1512
    InvalidHeaders = 1513


class DbCodes(object):
    Down = 2000
    Updated = 2001
    Inserted = 2002
    Unchanged = 2003
    Replaced = 2004
    Errors = 2005
    Deleted = 2006
    Nothing = 2007
    Skipped = 2008
    DoesNotExist = 2009


class UpdatesApplications(object):
    UpdatesApplications = 7000
    UpdatesApplicationsFailed = 7001

