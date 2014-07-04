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
    Tags = 'tags'
    UserName = 'user_name'
    ViewName = 'view_name'


class CronKeys(object):
    Year = 'year'
    Month = 'month'
    Day = 'day'
    DayOfWeek = 'day_of_week'
    Minute = 'minute'
    Second = 'second'
    TimeZone = 'timezone'


class IntervalKeys(object):
    Years = 'years'
    Months = 'months'
    Days = 'days'
    Minutes = 'minutes'
    Seconds = 'seconds'
    TimeZone = 'timezone'


class DateKeys(object):
    TimeZone = 'timezone'
    RunDate = 'run_date'
