from vFense.core.agent.status_codes import AgentCodes, AgentFailureCodes

class AgentResultCodes(AgentCodes):
    NewAgentSucceeded = 3200
    CheckInSucceeded = 3201
    StartUpSucceeded = 3202
    ResultsUpdated = 3203
    TokenValidated = 3204
    AgentAuthenticated = 3205
    AgentUpdated = 3206
    DataReceivedSuccessfully = 3207


class AgentFailureResultCodes(AgentFailureCodes):
    NewAgentFailed = 3300
    CheckInFailed = 3301
    StartupFailed = 3302
    InvalidOperationId = 3303
    InvalidOperationIdWithAgentId = 3304
    ResultsFailedToUpdate = 3305
    InvalidSuccessValue = 3306
    OperationFailed = 3307
    InvalidToken = 3308
    DataReceivedFailure = 3309
