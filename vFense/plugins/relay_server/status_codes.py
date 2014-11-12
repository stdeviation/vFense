from vFense.core.status_codes import (
    GenericCodes, GenericFailureCodes,
)

class RelayServerCodes(GenericCodes):
    RelayServerCreated = 10000
    RelayServerUpdated = 10001
    RelayServerRemoved = 10002
    RelayServerExist = 10003
    RelayServerUnchanged = 10004


class RelayServerFailureCodes(GenericFailureCodes):
    FailedToAddRelayServer = 10100
    FailedToUpdateRelayServer = 10101
    FailedToRemoveRelayServer = 10102
    RelayServerDoesNotExist = 10103
