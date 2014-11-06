import unittest
from json import dumps
from vFense.core.agent._db_model import AgentKeys
from vFense.core.tag import Tag
from vFense.core.tag._db_model import TagKeys
from vFense.core.tag._db import fetch_tag_by_name_and_view
from vFense.core.agent._db import fetch_agent_ids
from vFense.core.tag.manager import TagManager
from vFense.core.agent import Agent
from vFense.core.agent.manager import AgentManager
from vFense.core.agent.status_codes import AgentCodes
from vFense.core.agent.operations.store_agent_operations import (
    StoreAgentOperations
)
from vFense.core.agent.operations.agent_results import (
    AgentOperationResults
)
from vFense.core.operations import AgentOperation
from vFense.core.operations.agent_operations import AgentOperationManager
from vFense.core.operations.status_codes import AgentOperationCodes
from vFense.core.queue import AgentQueue
from vFense.core.queue.manager import AgentQueueManager
from vFense.core.receiver.status_codes import AgentResultCodes
from vFense.core.tag.status_codes import TagCodes
from vFense.core.view.status_codes import ViewCodes
from vFense.core.tests.agent_and_tag_data import AGENT_DATA
from vFense.core.view import View
from vFense.core.view.manager import ViewManager


class OperationsQueueAndJobTests(unittest.TestCase):
    def test_a_create_view(self):
        view = View(
            'Test View 1', package_download_url_base='http://localhost/packages'
        )
        manager = ViewManager(view.view_name)
        results = manager.create(view)
        print dumps(results.to_dict(), indent=4)
        status_code = results.vfense_status_code
        self.failUnless(status_code == ViewCodes.ViewCreated)

    def test_b_create_tag(self):
        tag = (
            Tag(
                tag_name='Global Test Tag 1', view_name='Test View 1',
                is_global=True
            )
        )
        manager = TagManager()
        results = manager.create(tag)
        print dumps(results.to_dict(), indent=4)
        status_code = results.vfense_status_code
        self.failUnless(status_code == TagCodes.TagCreated)

    def test_c_create_agent(self):
        system_info = AGENT_DATA["system_info"]
        system_info[AgentKeys.Views] = AGENT_DATA[AgentKeys.Views]
        system_info[AgentKeys.Hardware] = AGENT_DATA[AgentKeys.Hardware]
        agent = Agent(**system_info)
        tag = (
            fetch_tag_by_name_and_view(
                'Global Test Tag 1', 'Test View 1'
            )
        )
        manager = AgentManager()
        results = manager.create(agent, tags=[tag[TagKeys.TagId]])
        print dumps(results.to_dict(), indent=4)
        status_code = results.vfense_status_code
        self.failUnless(status_code == AgentResultCodes.NewAgentSucceeded)

    def test_d_create_operation_reboot(self):
        agent_ids = fetch_agent_ids('Test View 1')
        username = 'global_admin'
        viewname = 'Test View 1'
        operation = AgentOperation()
        operation.agent_ids = agent_ids
        manager = StoreAgentOperations(username, viewname)
        results = manager.reboot(operation)
        print dumps(results.to_dict(), indent=4)
        status_code = results.vfense_status_code
        self.failUnless(status_code == AgentOperationCodes.Created)

    def test_d_get_agent_queue1_and_update_results(self):
        agent_id = fetch_agent_ids('Test View 1')[0]
        manager = AgentQueueManager(agent_id)
        job = AgentQueue(**manager.get_agent_queue()[0])
        oper_manager = AgentOperationManager()
        oper_manager.update_operation_pickup_time(
            job.operation_id, agent_id
        )
        results = (
            AgentOperationResults(
                agent_id, job.operation_id, success='true'
            )
        )
        updated = results.reboot()
        print dumps(updated.to_dict_non_null(), indent=4)
        self.failUnless(
            updated.vfense_status_code == AgentResultCodes.ResultsUpdated
        )

    def test_d_get_agent_queue2_and_delete(self):
        agent_id = fetch_agent_ids('Test View 1')[0]
        manager = AgentQueueManager(agent_id)
        operation_manager = AgentOperationManager()
        jobs = manager.get_agent_queue()
        deleted_ids = []
        for job in jobs:
            job = AgentQueue(**job)
            status = manager.remove_job(job.id)
            if status:
                deleted_ids.append(job.id)
                operation_manager.remove_operation(job.operation_id)
        print dumps(deleted_ids, indent=4)
        self.failUnless(len(jobs) == len(deleted_ids))

    def test_e_create_operation_shutdown(self):
        agent_ids = fetch_agent_ids('Test View 1')
        username = 'global_admin'
        viewname = 'Test View 1'
        operation = AgentOperation()
        operation.agent_ids = agent_ids
        manager = StoreAgentOperations(username, viewname)
        results = manager.shutdown(operation)
        print dumps(results.to_dict(), indent=4)
        status_code = results.vfense_status_code
        self.failUnless(status_code == AgentOperationCodes.Created)

    def test_e_pop_agent_queue(self):
        agent_id = fetch_agent_ids('Test View 1')[0]
        jobs = AgentQueueManager(agent_id).pop_agent_queue()
        operation_manager = AgentOperationManager()
        for job in jobs:
            job = AgentQueue(**job)
            count, errors = operation_manager.remove_operation(job.operation_id)
        print count, errors
        self.failUnless(count == 2)

    def test_x_view_delete_agents(self):
        manager = ViewManager('Test View 1')
        results = manager.delete_agents()
        print dumps(results.to_dict(), indent=4)
        status_code = results.vfense_status_code
        self.failUnless(status_code == AgentCodes.AgentsDeleted)

    def test_y_tag_remove(self):
        tag = (
            fetch_tag_by_name_and_view(
                'Global Test Tag 1', 'Test View 1'
            )
        )
        manager = TagManager(tag[TagKeys.TagId])
        results = manager.remove()
        print dumps(results.to_dict_non_null(), indent=4)
        status_code = results.vfense_status_code
        self.failUnless(status_code == TagCodes.TagRemoved)

    def test_z_view_remove(self):
        manager = ViewManager('Test View 1')
        results = manager.remove(force=True)
        print dumps(results.to_dict(), indent=4)
        status_code = results.vfense_status_code
        self.failUnless(status_code == ViewCodes.ViewDeleted)


def main():
    unittest.main()

if __name__ == '__main__':
    main()
