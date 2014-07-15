from vFense.core.status_codes import (
    GenericCodes, GenericFailureCodes
)
class PackageCodes(GenericCodes):
    InvalidStatus = 5000
    InvalidPackageId = 5001
    InvalidFilter = 5002
    InvalidSeverity = 5003
    FileCompletedDownload = 5004
    FileIsDownloading = 5005
    FileNotRequired = 5006
    FilePendingDownload = 5007
    FileFailedDownload = 5008
    MissingUri = 5009
    InvalidUri = 5010
    HashNotVerified = 5011
    FileSizeMisMatch = 5012
    ThisIsNotAnUpdate = 5013
    ThisIsAnUpdate = 5014
    ToggleHiddenSuccessful = 5015
    AgentWillDownloadFromVendor = 5016
    PackageDeleted = 5017
    PackagesDeletionFailed = 5018


class PackageFailureCodes(GenericFailureCodes):
    ToggleHiddenFailed = 5300
    InvalidToggle = 5301
    ApplicationDoesNotExist = 5302
