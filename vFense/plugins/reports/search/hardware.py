from vFense.core.agent._db_model import AgentKeys
from vFense.core.results import ApiResults
from vFense.core.status_codes import GenericCodes, GenericFailureCodes
from vFense.core.view._constants import DefaultViews
from vFense.core.agent._constants import AgentCommonKeys
from vFense.plugins.reports.search._db_hardware import FetchHardware
from vFense.search.base import RetrieveBase

class RetrieveHardware(RetrieveBase):
    def __init__(self, **kwargs):
        super(RetrieveHardware, self).__init__(**kwargs)

        self.list_of_valid_keys = [
            AgentKeys.ComputerName, AgentKeys.HostName,
            AgentKeys.DisplayName, AgentKeys.OsCode,
            AgentKeys.OsString, AgentKeys.AgentId, AgentKeys.AgentStatus,
            AgentKeys.NeedsReboot, AgentKeys.BasicStats,
            AgentKeys.Environment, AgentKeys.LastAgentUpdate
        ]

        self.valid_keys_to_filter_by = (
            [
                AgentKeys.OsCode,
                AgentKeys.OsString,
                AgentKeys.AgentStatus,
                AgentKeys.Environment
            ]
        )

        valid_keys_to_sort_by = (
            [
                AgentKeys.ComputerName,
                AgentKeys.HostName,
                AgentKeys.DisplayName,
                AgentKeys.OsCode,
                AgentKeys.OsString,
                AgentKeys.AgentStatus,
                AgentKeys.Environment,
                AgentCommonKeys.AVAIL_VULN,
                AgentCommonKeys.AVAIL_UPDATES,
                AgentKeys.LastAgentUpdate,
            ]
        )

        if self.sort_key not in valid_keys_to_sort_by:
            self.sort_key = AgentKeys.ComputerName

        if self.view_name == DefaultViews.GLOBAL:
            self.view_name = None

        self.fetch = (
            FetchHardware(
                self.view_name, self.count, self.offset,
                self.sort, self.sort_key
            )
        )

    def all(self):
        """Return all hardware
        Basic Usage:
            >>> from vFense.plugins.reports.search.hardware import RetrieveHardware
            >>> view_name = 'global'
            >>> search = RetrieveHardware(view_name='default')
            >>> search.all()

        Returns:
            An instance of ApiResults
        """
        count, data = self.fetch.all()
        return self._base(count, data)

    def memory(self):
        """Return all memory
        Basic Usage:
            >>> from vFense.plugins.reports.search.hardware import RetrieveHardware
            >>> view_name = 'global'
            >>> search = RetrieveHardware(view_name='default')
            >>> search.memory()

        Returns:
            An instance of ApiResults
        """
        count, data = self.fetch.memory()
        return self._base(count, data)

    def cpu(self):
        """Return all cpus
        Basic Usage:
            >>> from vFense.plugins.reports.search.hardware import RetrieveHardware
            >>> view_name = 'global'
            >>> search = RetrieveHardware(view_name='default')
            >>> search.cpu()

        Returns:
            An instance of ApiResults
        """
        count, data = self.fetch.cpu()
        return self._base(count, data)

    def display(self):
        """Return all displays
        Basic Usage:
            >>> from vFense.plugins.reports.search.hardware import RetrieveHardware
            >>> view_name = 'global'
            >>> search = RetrieveHardware(view_name='default')
            >>> search.display()

        Returns:
            An instance of ApiResults
        """
        count, data = self.fetch.display()
        return self._base(count, data)

    def storage(self):
        """Return all file systems
        Basic Usage:
            >>> from vFense.plugins.reports.search.hardware import RetrieveHardware
            >>> view_name = 'global'
            >>> search = RetrieveHardware(view_name='default')
            >>> search.storage()

        Returns:
            An instance of ApiResults
        """
        count, data = self.fetch.storage()
        return self._base(count, data)

    def nic(self):
        """Return all nics
        Basic Usage:
            >>> from vFense.plugins.reports.search.hardware import RetrieveHardware
            >>> view_name = 'global'
            >>> search = RetrieveHardware(view_name='default')
            >>> search.nic()

        Returns:
            An instance of ApiResults
        """
        count, data = self.fetch.nic()
        return self._base(count, data)


    def _base(self, count, data):
        """Return all hardware
        Basic Usage:
            >>> from vFense.plugins.reports.search.hardware import RetrieveHardware
            >>> view_name = 'global'
            >>> search = RetrieveHardware(view_name='default')
            >>> search.all()

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
