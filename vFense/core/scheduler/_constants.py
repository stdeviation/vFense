class ScheduleDefaults(object):
    TIME_ZONE = 'UTC'


class ScheduleTriggers(object):
    CRON = 'cron'
    INTERVAL = 'interval'
    DATE = 'date'

    @staticmethod
    def get_valid_triggers():
        valid_triggers = (
            map(
                lambda x:
                getattr(ScheduleTriggers, x), dir(ScheduleTriggers)[:-3]
            )
        )
        return valid_triggers


class ScheduleKeys(object):
    Function = 'function'
    Agents = 'agents'
    AgentIds = 'agent_ids'
    Tags = 'tags'
    TagIds = 'tag_ids'
    UserName = 'user_name'
    ViewName = 'view_name'


class CronKeys(object):
    Year = 'year'
    Month = 'month'
    Day = 'day'
    DayOfWeek = 'day_of_week'
    Week = 'week'
    Minute = 'minute'
    Second = 'second'
    TimeZone = 'timezone'
    StartDate = 'start_date'
    EndDate = 'end_date'


class IntervalKeys(object):
    Weeks = 'weeks'
    Hours = 'hours'
    Days = 'days'
    Minutes = 'minutes'
    Seconds = 'seconds'
    TimeZone = 'timezone'
    StartDate = 'start_date'
    EndDate = 'end_date'


class DateKeys(object):
    TimeZone = 'timezone'
    RunDate = 'run_date'

def job_id():
    return '[a-f0-9]{32}'

def job_regex():
    return '({0})'.format(job_id())
