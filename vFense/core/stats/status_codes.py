from vFense.core.status_codes import GenericCodes, GenericFailureCodes

class StatCodes(GenericCodes):
    StatCreated = 10000
    StatUpdated = 10001
    StatDeleted = 10002


class StatFailureCodes(GenericFailureCodes):
    FailedToCreateStat = 10100
    FailedToUpdateStat = 10101
    FailedToDeleteStat = 10101
