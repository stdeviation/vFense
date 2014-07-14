
class SchedulerCodes(object):
    ScheduleCreated = 9000
    ScheduleUpdated = 9001
    FailedToCreateSchedule = 9002
    InvalidTimeStamp = 9003
    InvalidScheduleType = 9004
    ScheduleRemoved = 9005
    ScheduleRemovedFailed = 9006
    InvalidScheduleName = 9007
    ScheduleExists = 9008


class SchedulerFailureCodes(object):
    FailedToCreateSchedule = 9100
    FailedToRemoveSchedule = 9101
    FailedToUpdateSchedule = 9102
    InvalidTimeStamp = 9103
    ScheduleExistsWithSameName = 9104
