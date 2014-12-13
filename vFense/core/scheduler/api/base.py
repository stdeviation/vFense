
from vFense.core.api._constants import ApiArguments
from vFense.core.api.base import BaseHandler
from vFense.core.decorators import results_message
from vFense.core.scheduler._db_model import JobKeys
from vFense.core.user.manager import UserManager

class BaseJob(BaseHandler):
    def get_search_arguments(self):
        self.active_user = self.get_current_user()
        self.user = UserManager(self.active_user)
        self.active_view = self.user.properties.current_view
        self.count = int(self.get_argument(ApiArguments.COUNT, 30))
        self.offset = int(self.get_argument(ApiArguments.OFFSET, 0))
        self.query = self.get_argument(ApiArguments.QUERY, None)
        self.operation = self.get_argument(ApiArguments.OPERATION, None)
        self.trigger = self.get_argument('trigger', None)
        self.timezone = self.get_argument('timezone', None)
        self.sort = self.get_argument(ApiArguments.SORT, 'desc')
        self.sort_by = self.get_argument(ApiArguments.SORT_BY, JobKeys.NextRunTime)
        self.output = self.get_argument(ApiArguments.OUTPUT, 'json')

    def apply_search(self, search):
        if not self.operation and not self.trigger and not self.query and not self.timezone:
            results = self.get_all_jobs(search)

        elif self.query and not self.operation and not self.trigger and not self.imezone:
            results = self.get_all_jobs_by_name(search, self.query)

        elif self.operation and not self.trigger and not self.query and not self.timezone:
            results = self.get_all_jobs_by_operation(search, self.operation)

        elif self.trigger and not self.operation and not self.query and not self.timezone:
            results = self.get_all_jobs_by_trigger(search, self.trigger)

        elif self.timezone and not self.operation and not self.query and not self.trigger:
            results = self.get_all_jobs_by_timezone(search, self.timezone)

        elif self.query and self.trigger and not self.operation and not self.timezone:
            results = self.get_all_jobs_by_name_and_trigger(
                search, self.query, self.trigger
            )

        elif self.operation and self.trigger and not self.query and not self.timezone:
            results = self.get_all_jobs_by_operation_and_trigger(
                search, self.operation, self.trigger
            )

        elif self.query and self.operation and self.trigger:
            results = (
                self.get_all_jobs_by_name_and_trigger_and_operation(
                    search, self.query, self.trigger, self.operation
                )
            )

        return results


    @results_message
    def get_all_jobs(self, search):
        results = search.all()
        return results

    @results_message
    def get_all_jobs_by_name(self, search, name):
        results = search.by_name(name)
        return results

    @results_message
    def get_all_jobs_by_trigger(self, search, trigger):
        results = search.by_trigger(trigger)
        return results

    @results_message
    def get_all_jobs_by_operation(self, search, operation):
        results = search.by_operation(operation)
        return results

    @results_message
    def get_all_jobs_by_timezone(self, search, timezone):
        results = search.by_timezone(timezone)
        return results

    @results_message
    def get_all_jobs_by_name_and_trigger(self, search, name, trigger):
        results = search.by_name_and_trigger(name, trigger)
        return results

    @results_message
    def get_all_jobs_by_operation_and_trigger(self, search, operation,
                                              trigger):
        results = search.by_operation_and_trigger(operation, trigger)
        return results

    @results_message
    def get_all_jobs_by_name_and_trigger_and_operation(self, search, name,
                                                       trigger, operation):
        results = (
            search.by_name_and_trigger_and_operation(
                name, trigger, operation
            )
        )
        return results
