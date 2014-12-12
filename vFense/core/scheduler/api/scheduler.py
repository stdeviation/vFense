from vFense.core.permissions._constants import Permissions
from vFense.core.permissions.decorators import check_permissions
from vFense.core.scheduler.api.abase import BaseJob
from vFense.core.scheduler.search.search import RetrieveJobs

class JobsHandler(BaseJob):
    @authenticated_request
    @check_permissions(Permissions.READ)
    def get(self):
        self.get_search_arguments()
        self.search = (
            RetrieveJobs(
                view_name=self.active_view, count=self.count,
                offset=self.offset, sort=self.sort, sort_key=self.sort_by
            )
        )

        self.set_status(results.http_status_code)
        self.modified_output(results, output, 'jobs')


