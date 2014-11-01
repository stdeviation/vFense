from vFense.core.status_codes import GenericCodes, GenericFailureCodes

class EmailCodes(GenericCodes):
    EmailSettingsCreated = 11000
    EmailSettingsUpdated = 11001
    EmailSettingsDeleted = 11002


class EmailFailureCodes(GenericFailureCodes):
    FailedToCreateEmailSettings = 8100
    FailedToUpdateEmailSettings = 8101
    FailedToDeleteEmailSettings = 8102
