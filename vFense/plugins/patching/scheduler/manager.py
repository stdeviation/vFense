from vFense.core.operations._constants import AgentOperations
from vFense.plugins.patching.operations import Install
from vFense.plugins.patching.scheduler.jobs import (
    agent_apps_operation, tag_apps_operation
)
from vFense.core.scheduler import Schedule
from vFense.core.scheduler._constants import ScheduleTriggers
from vFense.core.scheduler.manager import JobManager
from vFense.core.scheduler.status_codes import SchedulerFailureCodes
from vFense.core.results import ApiResults

class AgentAppsJobManager(JobManager):
    def _set_funcs(self):
        self.once_func = agent_apps_operation

    def once(self, install, run_date, job_name, time_zone=None,
             operation=AgentOperations.INSTALL_OS_APPS):
        """Install 1 or multiple applications to 1 or multiple agents.
        Args:
            install (Install): An instance of Install.
            run_date (float): The unix time, aka epoch time
            job_name (str): The name of this job.

        Kwargs:
            time_zone (str):  Example... UTC, Chile/EasterIsland
            operation (str): The name of the operation.
                example install_os_apps, uninstall
        """
        results = ApiResults()
        results.fill_in_defaults()
        self._set_funcs()
        if isinstance(install, Install):
            invalid_fields = install.get_invalid_fields()
            if not invalid_fields:
                install.fill_in_defaults()
                install.operation = operation
                job = (
                    Schedule(
                        job_name, self.once_func, install.to_dict(),
                        run_date=run_date, operation=operation,
                        time_zone=time_zone, trigger=ScheduleTriggers.DATE
                    )
                )
                results = self.add_date_job(job)

            else:
                msg = (
                    'Failed to create install job, invalid fields were passed'
                )
                results.generic_status_code = (
                    SchedulerFailureCodes.FailedToCreateObject
                )
                results.vfense_status_code = (
                    SchedulerFailureCodes.FailedToCreateSchedule
                )
                results.message = msg
                results.errors = invalid_fields
                results.data = install.to_dict()

        else:
            msg = (
                'Invalid {0} Instance, must pass an instance of Install.'
                .format(type(install))
            )
            results.generic_status_code = (
                SchedulerFailureCodes.FailedToCreateObject
            )
            results.vfense_status_code = (
                SchedulerFailureCodes.FailedToCreateSchedule
            )
            results.message = msg

        return results

class TagAppsJobManager(AgentAppsJobManager):
    def _set_funcs(self):
        self.once_func = tag_apps_operation
