import unittest
from json import dumps

from vFense.core.agent._db_model import (
    AgentKeys
)
from vFense.core.tag import Tag
from vFense.core.tag.manager import TagManager
from vFense.core.agent import Agent
from vFense.core.agent.manager import AgentManager
from vFense.errorz.status_codes import (
    AgentCodes, AgentResultCodes
)
from vFense.errorz._constants import ApiResultKeys
from vFense.core.agent._constants import AgentDefaults
from vFense.core.tests.agent_and_tag_data import AGENT_DATA

class AgentsAndTagsTests(unittest.TestCase):

    def test_a_create_agent1(self):
        system_info = AGENT_DATA["system_info"]
        system_info[AgentKeys.Views] = AGENT_DATA[AgentKeys.Views]
        system_info[AgentKeys.Hardware] = AGENT_DATA[AgentKeys.Hardware]
        agent = Agent(**system_info)
        manager = AgentManager()
        results = manager.create(agent)
        print dumps(results, indent=4)
        status_code = results.get(ApiResultKeys.VFENSE_STATUS_CODE)
        self.failUnless(status_code == AgentResultCodes.NewAgentSucceeded)


def main():
    unittest.main()

if __name__ == '__main__':
    main()
