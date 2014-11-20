from vFense.core.api.base import BaseHandler
from vFense.core.api._constants import ApiArguments
from vFense.core.decorators import (
    authenticated_request, results_message, api_catch_it
)
from vFense.core.permissions._constants import Permissions
from vFense.core.permissions.decorators import check_permissions
from vFense.core.stats.search.stats import RetrieveStats


class AgentStats(BaseHandler):
    @api_catch_it
    @authenticated_request
    def get(self, agent_id, stat):
        output = self.get_argument(ApiArguments.OUTPUT, 'json')
        search = RetrieveStats(agent_id=agent_id)
        results = self.get_stats(search, stat)
        self.set_status(results.http_status_code)
        self.modified_output(results, output, 'stats')

    @results_message
    @check_permissions(Permissions.READ)
    def get_stats(self, search, stat):
        results = search.by_stat(stat)
        results.count = len(results.data)
        return results
