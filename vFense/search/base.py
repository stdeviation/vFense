from vFense.core._constants import SortValues, DefaultQueryValues
from vFense.core.results import ApiResults
from vFense.core.agent._db_model import AgentKeys

class RetrieveBase(object):
    def __init__(
        self, view_name=None,
        count=DefaultQueryValues.COUNT,
        offset=DefaultQueryValues.OFFSET,
        sort=SortValues.ASC,
        sort_key=AgentKeys.ComputerName
        ):

        self.view_name = view_name
        self.count = count
        self.offset = offset
        self.sort = sort
        self.sort_key = sort_key

    def _set_results(self, generic_status_code, vfense_status_code,
                     msg, count, data):
        results = ApiResults()
        results.fill_in_defaults()
        results.generic_status_code = generic_status_code
        results.vfense_status_code = vfense_status_code
        results.message = msg
        results.count = count
        results.data = data
        return results
