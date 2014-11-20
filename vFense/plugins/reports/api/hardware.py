import simplejson as json

from vFense.core.api.base import BaseHandler
from vFense.core._constants import DefaultQueryValues, SortValues
from vFense.core.api._constants import (
    ApiArguments, AgentApiArguments
)
from vFense.core.results import ApiResults, ExternalApiResults
from vFense.core.decorators import (
    authenticated_request, results_message, api_catch_it
)
from vFense.core.permissions._constants import Permissions
from vFense.core.permissions.decorators import check_permissions
from vFense.core.agent._db_model import AgentKeys, HardwarePerAgentKeys
from vFense.core.user.manager import UserManager
from vFense.plugins.reports.search.hardware import RetrieveHardware

class HardwareReportsHandler(BaseHandler):
    @api_catch_it
    @authenticated_request
    def get(self, report_type):
        active_user = self.get_current_user()
        active_view = UserManager(active_user).properties.current_view
        query = self.get_argument(ApiArguments.QUERY, None)
        count = (
            int(
                self.get_argument(ApiArguments.COUNT, DefaultQueryValues.COUNT)
            )
        )
        offset = (
            int(
                self.get_argument(
                    ApiArguments.OFFSET, DefaultQueryValues.OFFSET
                )
            )
        )
        sort = self.get_argument(ApiArguments.SORT, SortValues.ASC)
        sort_by = (
            self.get_argument(ApiArguments.SORT_BY, AgentKeys.ComputerName)
        )

        os_code = self.get_argument(AgentApiArguments.OS_CODE, None)
        os_string = self.get_argument(AgentApiArguments.OS_STRING, None)
        bit_type = self.get_argument(AgentApiArguments.BIT_TYPE, None)
        fkey = self.get_argument(ApiArguments.FILTER_KEY, None)
        search = (
            RetrieveHardware(
                view_name=active_view, count=count, offset=offset,
                sort=sort, sort_key=sort_by
            )
        )
        print os_code, os_string, bit_type, query
        if not os_code and not os_string and not bit_type and not query:
            print 'IN HERE'
            print search, report_type
            results = self.by_hw_type(search, report_type)
            print results

        elif os_code and not os_string and not bit_type and not query:
            results = self.by_cpu_and_os_code(search, report_type, os_code)

        elif os_code and query and not os_string and not bit_type:
            results = (
                self.by_cpu_and_os_code_and_query(
                    search, report_type, os_code, fkey, query
                )
            )

        self.set_status(results.http_status_code)
        self.set_header('Content-Type', 'application/json')
        self.write(json.dumps(results.to_dict_non_null(), indent=4))

    @results_message
    def by_hw_type(self, search, report_type):
        print 'in main func'
        print search, report_type
        if report_type == 'cpu':
            results = search.cpu()

        elif report_type == 'memory':
            results = search.memory()

        elif report_type == 'network':
            results = search.nic()

        elif report_type == 'disk':
            results = search.storage()

        elif report_type == 'hardware':
            results = search.display()

        elif report_type == 'os':
            results = search.display()

        return results

    @results_message
    def by_os_code(self, search, report_type, os_code):
        if report_type == 'cpu':
            results = search.cpu_by_regex('os_code', os_code)

        elif report_type == 'memory':
            results = search.memory_by_regex('os_code', os_code)

        elif report_type == 'nic':
            results = search.nic_by_regex('os_code', os_code)

        elif report_type == 'storage':
            results = search.storage_by_regex('os_code', os_code)

        elif report_type == 'display':
            results = search.display_by_regex('os_code', os_code)

        return results

    @results_message
    def by_os_code_and_query(self, search, report_type, os_code, fkey, query):
        if report_type == 'cpu':
            results = (
                search.cpu_by_os_code_and_by_regex(os_code, fkey, query)
            )
        if report_type == 'memory':
            results = (
                search.memory_by_os_code_and_by_regex(os_code, fkey, query)
            )
        elif report_type == 'nic':
            results = (
                search.nic_by_os_code_and_by_regex(os_code, fkey, query)
            )
        elif report_type == 'storage':
            results = (
                search.storage_by_os_code_and_by_regex(os_code, fkey, query)
            )
        elif report_type == 'display':
            results = (
                search.display_by_os_code_and_by_regex(os_code, fkey, query)
            )
        return results
