from time import time
from vFense.core.agent._db_model import AgentKeys
from vFense.core.agent._constants import (
    AgentDefaults
)
from vFense.core._constants import (
    CommonKeys
)
from vFense.core.results import ApiResultKeys
from vFense.core.status_codes import GenericCodes


class Stats(object):
    """Used to represent an instance of an agent."""

    def __init__(self, agent_id=None, stat_type=None):
        """
        Kwargs:
            agent_id (str): The id of the agent.
            stat_type (str): The type of the stat.
        """
        self.agent_id = agent_id
        self.stat_type = stat_type


    def fill_in_defaults(self):
        """Replace all the fields that have None as their value with
        the hardcoded default values.

        Use case(s):
            Useful when adding a new agent instance and only want to fill
            in a few fields, then allow the add agent functions to call this
            method to fill in the rest.
        """

        pass

    def get_invalid_fields(self):
        """Check the agent for any invalid fields.

        """
        return []

    def to_dict(self):
        """ Turn the fields into a dictionary."""

        return {}

    def to_dict_non_null(self):
        """ Use to get non None fields. Useful when
        filling out just a few fields to update the db.

        Returns:
            (dict): a dictionary with the non None fields of this view.
        """
        agent_dict = self.to_dict()

        return {k:agent_dict[k] for k in agent_dict
                if agent_dict[k] != None}

class CPUStats(Stats):

    def __init__(self, **kwargs):
        super(CPUStats, self).__init__(
            idle=None, system=None, user=None, iowait=None, **kwargs
        )
        """
        Kwargs:
            idle (float): Percent of cpu that is idle.
            user (float): Percent of cpu being used by the user.
            system (float): Percent of cpu being used by the system.
            iowait (float): Percent of cpu waiting.
            agent_id (str): The id of the agent.
            stat_type (str): The type of the stat.
        """
        self.agent_id = kwargs.get('agent_id')
        self.stat_type = kwargs.get('stat_type')
        self.idle = kwargs.get('idle')
        self.user = kwargs.get('user')
        self.system = kwargs.get('system')
        self.iowait = kwargs.get('iowait')
