from vFense.core.scheduler._constants import job_id
from vFense.core.api.scheduler import (
    JobHandler, JobsHandler, TimeZonesHandler
)

def api_handlers():
    handlers = [
        ##### Timezones
        (r"/api/v1/supported/timezones?", TimeZonesHandler),
        ##### Scheduler API Handlers
        (r"/api/v1/schedules?", JobsHandler),
        (r"/api/v1/schedule/({0})?".format(job_id()), JobHandler),
        #(r"/api/v1/schedules/recurrent/none?", SchedulerDateBasedJobHandler),
        #(r"/api/v1/schedules/recurrent/daily?", SchedulerDailyRecurrentJobHandler),
        #(r"/api/v1/schedules/recurrent/monthly?", SchedulerMonthlyRecurrentJobHandler),
        #(r"/api/v1/schedules/recurrent/yearly?", SchedulerYearlyRecurrentJobHandler),
        #(r"/api/v1/schedules/recurrent/weekly?", SchedulerWeeklyRecurrentJobHandler),
        #(r"/api/v1/schedules/recurrent/custom?", SchedulerCustomRecurrentJobHandler),
    ]
    return handlers
