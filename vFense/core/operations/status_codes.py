from vFense.core.status_codes import GenericCodes, GenericFailureCodes


class AgentOperationCodes(GenericCodes):
    Created = 6000
    Updated = 6001
    #Apps Results Codes For Operations
    ResultsReceived = 6002
    ResultsReceivedWithErrors = 6003
    ResultsPending = 6004
    InvalidOperationType = 6005
    #Results Codes For Operations
    ResultsCompleted = 6006
    ResultsCompletedWithErrors = 6007
    ResultsCompletedFailed = 6008
    ResultsIncomplete = 6009
    ResultsExpired = 6010
    OperationExpired = 6011


class AgentOperationFailureCodes(GenericFailureCodes):
    FailedToCreateOperation = 6200
    FailedToUpdateOperation = 6203


class OperationPerAgentCodes(GenericCodes):
    Checkin = 6500
    PendingPickUp = 6501
    PickedUp = 6502
    OperationExpired = 6503
    OperationFailed = 6504
    OperationCompleted = 6505
    OperationCompletedWithErrors = 6506
