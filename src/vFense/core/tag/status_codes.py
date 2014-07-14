from vFense.core.status_codes import GenericCodes, GenericFailureCodes


class TagCodes(GenericCodes):
    TagCreated = 4000
    TagRemoved = 4001
    TagUpdated = 4002
    TagUnchanged = 4003
    TagCreatedAndAgentAdded = 4004
    RemovedAgentIdFromTag = 4005
    RemovedTagFromAgentId = 4006
    RemovedAllAgentsFromTag = 4007
    FailedToRemoveAllAgentsFromTag = 4008
    FailedToRemoveTag = 4009
    TagExistsAndAgentAdded = 4010
    AgentsAddedToTag = 4011
    AgentsRemovedFromTag = 4012
    TagsDeleted = 4013
    TagsUpdated = 4014
    TagsUnchanged = 4015


class TagFailureCodes(GenericFailureCodes):
    FailedToCreateTag = 4501
    FailedToRemoveTag = 4502
    FailedToAddAgentsToTag = 4503
    FailedToRemoveAgentsFromTag = 4504
    InvalidTagIds = 4505
    FailedToDeleteTags = 4506
    FailedToUpdateTags = 4507
    FailedToUpdateTag = 4508


