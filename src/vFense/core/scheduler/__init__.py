from time import time
from vFense.core.scheduler._db_model import JobKeys
from vFense.core.scheduler._constants import (
    ScheduleDefaults, ScheduleTriggers, ScheduleVariables
)
from vFense.core._constants import (
    CommonKeys
)
from vFense.result._constants import ApiResultKeys
from vFense.result.status_codes import GenericCodes
from pytc import all_timezones


class Schedule(object):
    """Used to represent an instance of an agent."""

    def __init__(self, name=None, fn=None, job_kwargs=None,
                 start_date=None, end_date=None, operation=None,
                 time_zone=None, trigger=None,
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
        """
        self.name = name
        self.fn = fn
        self.job_kwargs = job_kwargs
        self.start_date = start_date
        self.end_date = end_date
        self.operation = operation
        self.time_zone = time_zone
        self.trigger = trigger


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


        return invalid_fields

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
