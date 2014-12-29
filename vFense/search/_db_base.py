from vFense.core._constants import SortValues, DefaultQueryValues
from vFense.core.agent._db_model import AgentKeys
from vFense.db.client import r


class FetchBase(object):
    def __init__(
        self, view_name=None,
        count=DefaultQueryValues.COUNT,
        offset=DefaultQueryValues.OFFSET,
        sort=SortValues.ASC,
        sort_key=AgentKeys.ComputerName,
        **kwargs
        ):
        """
        Kwargs:
            view_name (str): Fetch all agents in this view.
            count (int): The number of results to return.
            offset (int): The next set of results beginning at offset.
            sort (str): asc or desc.
            sort_key (str): The key you are going to sort the results by.
        """
        self.view_name = view_name
        self.count = count
        self.offset = offset
        self.sort_key = sort_key

        if sort == SortValues.ASC:
            self.sort = r.asc
        else:
            self.sort = r.desc
