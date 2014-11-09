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
    def get(self):
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
        hwtype = self.get_argument(HardwarePerAgentKeys.Type, 'nic')
        fkey = self.get_argument(ApiArguments.FILTER_KEY, None)
        search = (
            RetrieveHardware(
                view_name=active_view, count=count, offset=offset,
                sort=sort, sort_key=sort_by
            )
        )

        if not os_code and not os_string and not bit_type and not query:
            results = self.by_hw_typw(search, hwtype)

        elif os_code and not os_string and not bit_type and not query:
            results = self.by_cpu_and_os_code(search, hwtype, os_code)

        elif os_code and query and not os_string and not bit_type:
            results = (
                self.by_cpu_and_os_code_and_query(
                    search, hwtype, os_code, fkey, query
                )
            )

        self.set_status(results.http_status_code)
        self.set_header('Content-Type', 'application/json')
        self.write(json.dumps(results.to_dict_non_null(), indent=4))

    @results_message
    def by_hw_type(self, search, hwtype):
        if hwtype == 'cpu':
            results = search.cpu()

        elif hwtype == 'memory':
            results = search.memory()

        elif hwtype == 'nic':
            results = search.nic()

        elif hwtype == 'storage':
            results = search.storage()

        elif hwtype == 'display':
            results = search.display()

        return results

    @results_message
    def by_os_code(self, search, hwtype, os_code):
        if hwtype == 'cpu':
            results = search.cpu_by_regex('os_code', os_code)

        elif hwtype == 'memory':
            results = search.memory_by_regex('os_code', os_code)

        elif hwtype == 'nic':
            results = search.nic_by_regex('os_code', os_code)

        elif hwtype == 'storage':
            results = search.storage_by_regex('os_code', os_code)

        elif hwtype == 'display':
            results = search.display_by_regex('os_code', os_code)

        return results

    @results_message
    def by_os_code_and_query(self, search, hwtype, os_code, fkey, query):
        if hwtype == 'cpu':
            results = (
                search.cpu_by_os_code_and_by_regex(os_code, fkey, query)
            )
        if hwtype == 'memory':
            results = (
                search.memory_by_os_code_and_by_regex(os_code, fkey, query)
            )
        elif hwtype == 'nic':
            results = (
                search.nic_by_os_code_and_by_regex(os_code, fkey, query)
            )
        elif hwtype == 'storage':
            results = (
                search.storage_by_os_code_and_by_regex(os_code, fkey, query)
            )
        elif hwtype == 'display':
            results = (
                search.display_by_os_code_and_by_regex(os_code, fkey, query)
            )
        return results
