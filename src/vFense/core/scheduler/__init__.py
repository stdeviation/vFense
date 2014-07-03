from time import time
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.date import DateTrigger
from apscheduler.triggers.interval import IntervalTrigger
from vFense.core.scheduler._db_model import JobKeys
from vFense.core.scheduler._constants import (
    ScheduleDefaults, ScheduleTriggers, ScheduleVariables,
    CronKeys, IntervalKeys
)
from vFense.core._constants import (
    CommonKeys
)
from vFense.result._constants import ApiResultKeys
from vFense.result.status_codes import GenericCodes
from pytz import all_timezones


class Schedule(object):
    """Used to represent an instance of an agent."""

    def __init__(self, name=None, fn=None, job_kwargs=None,
                 start_date=None, end_date=None, operation=None,
                 time_zone=None, trigger=None, year=None, month=None,
                 day=None, day_of_week=None, hour=None, minute=None,
                 second=None, years=None, months=None, days=None,
                 hours=None, minutes=None, seconds=None
                 ):
        """
        Kwargs:
            name (str): The name of the job you are scheduling.
            fn (func): The function, this schedule will call.
            job_kwargs (dict): The keyword arguments this function will take.
            start_date (float): The start time in seconds.
                (unix time aka epoch time )
            end_date (float): The end time in seconds.
                (unix time aka epoch time )
            operation (str): The operation type
                example install, reboot, shutdown
            time_zone (str): The timezone this schedule is set for.
            trigger (boolean): The type of scheduler this is.
                example cron, interval, data
            year (str|int): The year or range of years.
            month (str|int): The month or range of months.
            day (str|int): The day or range of days.
            day_of_week (str|int): The day of week or range of days of week.
            hour (str|int): The hour or range of hours.
            minute (str|int): The minute or range of minutes.
            second (str|int): The second or range of seconds.
            years int: The year or range of years.
            months int: The month or range of months.
            days int: The days.
            hours int: The hours.
            minutes int: The minutes.
            seconds int: The seconds.
        """
        self.name = name
        self.fn = fn
        self.job_kwargs = job_kwargs
        self.start_date = start_date
        self.end_date = end_date
        self.operation = operation
        self.time_zone = time_zone
        self.trigger = trigger
        self.year = year
        self.month = month
        self.day = day
        self.day_of_week = day_of_week
        self.hour = hour
        self.minute = minute
        self.second = second
        self.years = years
        self.months = months
        self.days = days
        self.hours = hours
        self.minutes = minutes
        self.seconds = seconds


    def fill_in_defaults(self):
        """Replace all the fields that have None as their value with
        the hardcoded default values.

        Use case(s):
            Useful when adding a new schedule instance and only want to fill
            in a few fields, then allow the add schedule functions to call this
            method to fill in the rest.
        """

        if not self.time_zone:
            self.time_zone = ScheduleDefaults.TIME_ZONE

    def get_invalid_fields(self):
        """Check the agent for any invalid fields.

        Returns:
            (list): List of key/value pair dictionaries corresponding
                to the invalid fields.

                Ex:
                    [
                        {'view_name': 'the invalid name in question'},
                        {'net_throttle': -10}
                    ]
        """
        invalid_fields = []

        if self.trigger:
            if not isinstance(self.trigger, basestring):
                invalid_fields.append(
                    {
                        JobKeys.Trigger: self.trigger,
                        CommonKeys.REASON: 'Must be a string value',
                        ApiResultKeys.VFENSE_STATUS_CODE: (
                            GenericCodes.InvalidValue
                        )
                    }
                )

            if self.trigger not in ScheduleTriggers.get_valid_triggers():
                invalid_fields.append(
                    {
                        JobKeys.Trigger: self.trigger,
                        CommonKeys.REASON: (
                            'Trigger must be one of these {0}'
                            .format(
                                ', '.join(
                                    ScheduleTriggers.get_valid_triggers()
                                )
                            )
                        ),
                        ApiResultKeys.VFENSE_STATUS_CODE: (
                            GenericCodes.InvalidValue
                        )
                    }
                )

        if self.time_zone:
            if not isinstance(self.time_zone, basestring):
                invalid_fields.append(
                    {
                        JobKeys.TimeZone: self.time_zone,
                        CommonKeys.REASON: 'Must be a string value',
                        ApiResultKeys.VFENSE_STATUS_CODE: (
                            GenericCodes.InvalidValue
                        )
                    }
                )

            if self.time_zone not in all_timezones():
                invalid_fields.append(
                    {
                        JobKeys.TimeZone: self.time_zone,
                        CommonKeys.REASON: (
                            'Time zone must be one of these {0}'
                            .format(', '.join(all_timezones))
                        ),
                        ApiResultKeys.VFENSE_STATUS_CODE: (
                            GenericCodes.InvalidValue
                        )
                    }
                )

        if self.start_date:
            if not isinstance(self.start_date, float):
                invalid_fields.append(
                    {
                        JobKeys.StartDate: self.start_date,
                        CommonKeys.REASON: (
                            'Must be a float value'
                        ),
                        ApiResultKeys.VFENSE_STATUS_CODE: (
                            GenericCodes.InvalidValue
                        )
                    }
                )

        if self.end_date:
            if not isinstance(self.end_date, float):
                invalid_fields.append(
                    {
                        JobKeys.EndDate: self.end_date,
                        CommonKeys.REASON: (
                            'Must be a float value'
                        ),
                        ApiResultKeys.VFENSE_STATUS_CODE: (
                            GenericCodes.InvalidValue
                        )
                    }
                )

        if self.fn:
            if not hasattr(self.fn, '__call__'):
                invalid_fields.append(
                    {
                        ScheduleVariables.Function: self.fn,
                        CommonKeys.REASON: (
                            'Must be a a valid function'
                        ),
                        ApiResultKeys.VFENSE_STATUS_CODE: (
                            GenericCodes.InvalidValue
                        )
                    }
                )

        if self.job_kwargs:
            if not isinstance(self.job_kwargs, dict):
                invalid_fields.append(
                    {
                        JobKeys.Kwargs: self.job_kwargs,
                        CommonKeys.REASON: (
                            'Must be a dictionary'
                        ),
                        ApiResultKeys.VFENSE_STATUS_CODE: (
                            GenericCodes.InvalidValue
                        )
                    }
                )

        if self.trigger:
            if self.trigger == 'cron':
                try:
                    CronTrigger(self.fn, **self.to_cron_dict())
                except ValueError as e:
                    invalid_fields.append(
                        {
                            JobKeys.Trigger: self.trigger,
                            CommonKeys.REASON: e,
                            ApiResultKeys.VFENSE_STATUS_CODE: (
                                GenericCodes.InvalidValue
                            )
                        }
                    )

            elif self.trigger == 'date':
                try:
                    DateTrigger(self.fn, **self.to_date_dict())
                except ValueError as e:
                    invalid_fields.append(
                        {
                            JobKeys.Trigger: self.trigger,
                            CommonKeys.REASON: e,
                            ApiResultKeys.VFENSE_STATUS_CODE: (
                                GenericCodes.InvalidValue
                            )
                        }
                    )

            elif self.trigger == 'interval':
                try:
                    IntervalTrigger(self.fn, **self.to_interval_dict())
                except ValueError as e:
                    invalid_fields.append(
                        {
                            JobKeys.Trigger: self.trigger,
                            CommonKeys.REASON: e,
                            ApiResultKeys.VFENSE_STATUS_CODE: (
                                GenericCodes.InvalidValue
                            )
                        }
                    )

        return invalid_fields

    def to_cron_dict(self):
        return {
            CronKeys.Year: self.year,
            CronKeys.Month: self.month,
            CronKeys.Day: self.day,
            CronKeys.DayOfWeek: self.day_of_week,
            CronKeys.Minute: self.minute,
            CronKeys.Second: self.second,
            JobKeys.StartDate: self.start_date,
            JobKeys.EndDate: self.end_date,
            JobKeys.TimeZone: self.time_zone,
        }

    def to_interval_dict(self):
        return {
            IntervalKeys.Years: self.years,
            IntervalKeys.Months: self.months,
            IntervalKeys.Days: self.days,
            IntervalKeys.Minutes: self.minutes,
            IntervalKeys.Seconds: self.seconds,
            JobKeys.StartDate: self.start_date,
            JobKeys.EndDate: self.end_date,
            JobKeys.TimeZone: self.time_zone,
        }

    def to_date_dict(self):
        return {
            JobKeys.StartDate: self.start_date,
            JobKeys.TimeZone: self.time_zone,
        }

    def to_dict(self):
        """ Turn the view fields into a dictionary.

        Returns:
            (dict): A dictionary with the fields corresponding to the job.

                Ex:
        """

        return {
            JobKeys.Name: self.name,
            JobKeys.Kwargs: self.kwargs,
            JobKeys.Operation: self.operation,
            JobKeys.StartDate: self.start_date,
            JobKeys.EndDate: self.end_date,
            JobKeys.Trigger: self.trigger,
            JobKeys.TimeZone: self.time_zone,
            CronKeys.Year: self.year,
            CronKeys.Month: self.month,
            CronKeys.Day: self.day,
            CronKeys.DayOfWeek: self.day_of_week,
            CronKeys.Minute: self.minute,
            CronKeys.Second: self.second,
        }


    def to_dict_non_null(self):
        """ Use to get non None fields of a job. Useful when
        filling out just a few fields to update the job in the db.

        Returns:
            (dict): a dictionary with the non None fields of this view.
        """
        job_dict = self.to_dict()

        return {k:job_dict[k] for k in job_dict
                if job_dict[k] != None}
