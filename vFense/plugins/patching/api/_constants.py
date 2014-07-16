from vFense.core.api._constants import ApiArguments

class AppApiArguments(ApiArguments):
    STATUS = 'status'
    SEVERITY = 'severity'
    VULN = 'vuln'
    HIDDEN = 'hidden'
    APP_IDS = 'app_ids'
    RUN_DATE = 'run_date'
    START_DATE = 'start_date'
    JOB_NAME = 'job_name'
    RESTART = 'restart'
    CPU_THROTTLE = 'cpu_throttle'
    NET_THROTTLE = 'net_throttle'

class AppFilterValues():
    SEVERITY = 'severity'
