import simplejson as json

from vFense._constants import VFENSE_LOGGING_CONFIG
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
from vFense.core.user._db_model import AgentKeys, HardwarePerAgentKeys
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
        hw_type = self.get_argument(HardwarePerAgentKeys.Type, 'nic')
        fkey = self.get_argument(ApiArguments.FILTER_KEY, None)
        fval = self.get_argument(ApiArguments.FILTER_VAL, None)
        search = (
            RetrieveHardware(
                view_name=active_view, count=count, offset=offset,
                sort=sort, sort_key=sort_by
            )
        )
        if hw_type == 'memory':
            if not os_code and not os_string and not bit_type:
                results = self.by_memory(search)
        self.set_status(results.http_status_code)
        self.set_header('Content-Type', 'application/json')
        self.write(json.dumps(results.to_dict_non_null(), indent=4))

    @results_message
    def by_memory(self, search):
        results = search.memory()
        return results

    @results_message
    def by_cpu(self):
        search = RetrieveHardware()
        results = search.cpu()
        return results

    @results_message
    def by_nic(self):
        search = RetrieveHardware()
        results = search.nic()
        return results

    @results_message
    def by_display(self):
        search = RetrieveHardware()
        results = search.display()
        return results

    @results_message
    def by_storage(self):
        search = RetrieveHardware()
        results = search.storage()
        return results
