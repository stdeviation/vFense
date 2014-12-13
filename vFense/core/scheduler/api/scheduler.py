from vFense.core.api._constants import ApiArguments
from vFense.core.api.base import BaseHandler
from vFense.core.decorators import (
    authenticated_request, results_message, api_catch_it
)
from vFense.core.results import ApiResults
from vFense.core.status_codes import GenericCodes
from vFense.core.permissions._constants import Permissions
from vFense.core.permissions.decorators import check_permissions
from vFense.core.scheduler.api.base import BaseJob
from vFense.core.scheduler.search.search import RetrieveJobs
from vFense.core.user.manager import UserManager

from pytz import all_timezones

class TimeZonesHandler(BaseHandler):
    @authenticated_request
    @check_permissions(Permissions.READ)
    def get(self):
        output = self.get_argument(ApiArguments.OUTPUT, 'json')
        results = self.get_timezones()
        self.set_header('Content-Type', 'application/json')
        self.modified_output(results, output, 'timezones')

    @api_catch_it
    @results_message
    def get_timezones(self):
        results = ApiResults()
        data = all_timezones
        results.data = data
        results.count = len(data)
        results.generic_status_code = GenericCodes.InformationRetrieved
        results.vfense_status_code = GenericCodes.InformationRetrieved
        return results


class JobHandler(BaseHandler):
    @authenticated_request
    @check_permissions(Permissions.READ)
    def get(self, job_id):
        active_user = self.get_current_user()
        active_view = UserManager(active_user).properties.current_view
        output = self.get_argument(ApiArguments.OUTPUT, 'json')
        search = RetrieveJobs(active_view)
        results = self.get_job_by_id(search, job_id)
        print results.to_dict_non_null()
        self.set_status(results.http_status_code)
        self.modified_output(results, output, 'job')

    @api_catch_it
    @results_message
    def get_job_by_id(self, search, job_id):
        results = search.by_id(job_id)
        return results


class JobsHandler(BaseJob):
    @authenticated_request
    @check_permissions(Permissions.READ)
    def get(self):
        self.get_search_arguments()
        search = (
            RetrieveJobs(
                view_name=self.active_view, count=self.count,
                offset=self.offset, sort=self.sort, sort_key=self.sort_by
            )
        )
        results = self.apply_search(search)

        self.set_status(results.http_status_code)
        self.modified_output(results, self.output, 'jobs')
