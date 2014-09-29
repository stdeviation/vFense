from vFense.core.api._constants import ApiArguments
from vFense.core.operations._constants import AgentOperations

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
    NAME = 'name'

class AppFilterValues():
    SEVERITY = 'severity'

class vFenseAppTypes():
    OS = 'os'
    AGENTUPDATES = 'agentupdates'
    CUSTOM = 'custom'
    SUPPORTED = 'supported'

    @staticmethod
    def return_app_operation(oper):
        if oper == vFenseAppTypes.OS:
            return AgentOperations.INSTALL_OS_APPS

        elif oper == vFenseAppTypes.CUSTOM:
            return AgentOperations.INSTALL_CUSTOM_APPS

        elif oper == vFenseAppTypes.SUPPORTED:
            return AgentOperations.INSTALL_SUPPORTED_APPS

        elif oper == vFenseAppTypes.AGENTUPDATES:
            return AgentOperations.INSTALL_AGENT_UPDATE
