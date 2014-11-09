from json import dumps

from vFense.core.api._constants import ApiArguments
from vFense.core.api.base import BaseHandler
from vFense.core.receiver.decorators import authenticate_agent
from vFense.core.results import Results
from vFense.core.decorators import (
    convert_json_to_arguments, api_catch_it, results_message
)
from vFense.core.receiver.decorators import (
    agent_results_message, agent_authenticated_request, receiver_catch_it,
    authenticate_agent
)
from vFense.core.stats import (
    FileSystemStatManager, MemoryStatManager, CPUStatManager
)
from vFense.core.stats.manager import (
    CPUStats, MemoryStats, FileSystemStats
)

class UpdateMonitoringStatsV1(BaseHandler):
    @agent_authenticated_request
    @convert_json_to_arguments
    def post(self, agent_id):
        data = self.arguments.get(ApiArguments.DATA)
        if data.has_key('cpu'):
            results = CPUStats(**(data.get('cpu')))
        self.set_status(results.http_status_code)
        self.set_header('Content-Type', 'application/json')
        self.write(dumps(results.to_dict_non_null()))

    @receiver_catch_it
    @agent_results_message
    def update_cpu(self, stat):
        manager = CPUStatManager()

