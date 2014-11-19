from json import dumps

from vFense.core.api._constants import ApiArguments
from vFense.core.api.base import BaseHandler
from vFense.core.decorators import (
    convert_json_to_arguments, results_message, api_catch_it
)
from vFense.core.receiver.api.base import AgentBaseHandler
from vFense.core.receiver.decorators import (
    agent_results_message, agent_authenticated_request, receiver_catch_it,
    authenticate_agent
)
from vFense.core.stats.manager import (
    FileSystemStatManager, MemoryStatManager, CPUStatManager
)
from vFense.core.stats import (
    CPUStats, MemoryStats, FileSystemStats
)

class UpdateMonitoringStatsV1(BaseHandler):
    @agent_authenticated_request
    @convert_json_to_arguments
    def post(self, agent_id):
        data = self.arguments.get(ApiArguments.DATA)
        if data.has_key('cpu'):
            stats = CPUStats(**(data.get('cpu')))
            results = self.update_cpu(stats, agent_id)

        if data.has_key('memory'):
            stats = MemoryStats(**(data.get('memory')))
            results = self.update_memory(stats, agent_id)

        if data.has_key('file_system'):
            stats = data.get('file_systems')
            results = self.update_memory(stats, agent_id)

        self.set_status(results.http_status_code)
        self.set_header('Content-Type', 'application/json')
        self.write(dumps(results.to_dict_non_null()))

    @api_catch_it
    @results_message
    def update_cpu(self, stat, agent_id):
        manager = CPUStatManager(agent_id=agent_id)
        results = manager.update(stat)
        return results

    @api_catch_it
    @results_message
    def update_memory(self, stat, agent_id):
        manager = MemoryStatManager(agent_id=agent_id)
        results = manager.update(stat)
        return results

    @receiver_catch_it
    @agent_results_message
    def update_filesystems(self, stats, agent_id):
        manager = FileSystemStatManager(agent_id=agent_id)
        stats = map(lambda x: FileSystemStats(**x), stats)
        results = manager.update(stats)
        return results


class UpdateMonitoringStatsV2(AgentBaseHandler):
    @authenticate_agent
    @convert_json_to_arguments
    def post(self, agent_id):
        data = self.arguments.get(ApiArguments.DATA)
        if data.has_key('cpu'):
            stats = CPUStats(**(data.get('cpu')))
            results = self.update_cpu(stats, agent_id)

        if data.has_key('memory'):
            stats = MemoryStats(**(data.get('memory')))
            results = self.update_memory(stats, agent_id)

        if data.has_key('file_system'):
            stats = data.get('file_systems')
            results = self.update_memory(stats, agent_id)

        self.set_status(results.http_status_code)
        self.set_header('Content-Type', 'application/json')
        self.write(dumps(results.to_dict_non_null()))

    @receiver_catch_it
    @agent_results_message
    def update_cpu(self, stat, agent_id):
        manager = CPUStatManager(agent_id=agent_id)
        results = manager.update(stat)
        return results

    @receiver_catch_it
    @agent_results_message
    def update_memory(self, stat, agent_id):
        manager = MemoryStatManager(agent_id=agent_id)
        results = manager.update(stat)
        return results

    @receiver_catch_it
    @agent_results_message
    def update_filesystems(self, stats, agent_id):
        manager = FileSystemStatManager(agent_id=agent_id)
        stats = map(lambda x: FileSystemStats(**x), stats)
        results = manager.update(stats)
        return results
