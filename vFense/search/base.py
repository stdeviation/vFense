from vFense.core._constants import SortValues, DefaultQueryValues
from vFense.core.agent._db_model import AgentKeys
from vFense.core.results import ApiResults
from vFense.core.status_codes import GenericCodes, GenericFailureCodes
from vFense.core.view._constants import DefaultViews

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

        if self.view_name == DefaultViews.GLOBAL:
            self.view_name = None

    def _base(self, count, data):
        """Default values get set here
        Basic Usage:
            >>> count = 1
            >>> data = {"computer_name": "foo"}
            >>> results = self._base(count, data)

        Returns:
            An instance of ApiResults
        """
        generic_status_code = GenericCodes.InformationRetrieved

        if count == 0:
            vfense_status_code = GenericFailureCodes.DataIsEmpty
            msg = 'dataset is empty'

        else:
            vfense_status_code = GenericCodes.InformationRetrieved
            msg = 'dataset retrieved'

        results = (
            self._set_results(
                generic_status_code, vfense_status_code,
                msg, count, data
            )
        )
        return results

    def _set_results_invalid_sort_key(self, key):
        vfense_status_code = GenericFailureCodes.InvalidSortKey
        generic_status_code = GenericCodes.InformationRetrieved
        msg = 'Invalid sort key {0}'.format(key)
        results = (
            self._set_results(
                generic_status_code, vfense_status_code, msg, 0, []
            )
        )
        return results

    def _set_results_invalid_filter_key(self, key):
        vfense_status_code = GenericFailureCodes.InvalidFilterKey
        generic_status_code = GenericCodes.InformationRetrieved
        msg = 'Invalid filter key {0}'.format(key)
        results = (
            self._set_results(
                generic_status_code, vfense_status_code, msg, 0, []
            )
        )
        return results

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
