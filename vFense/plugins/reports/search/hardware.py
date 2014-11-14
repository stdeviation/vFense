from vFense.core.agent._db_model import AgentKeys
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
                AgentKeys.Environment,
                AgentKeys.LastAgentUpdate,
            ]
        )

        if self.sort_key not in valid_keys_to_sort_by:
            self.sort_key = AgentKeys.ComputerName

        self.fetch = (
            FetchHardware(
                view_name=self.view_name, count=self.count,
                offset=self.offset, sort=self.sort, sort_key=self.sort_key
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

    def memory_by_regex(self, key, regex):
        """Return all memory by searching on a key and regex that maches
            the value.
        Args:
            key (str): The key you want to perform the search on.
                examples... computer_name, os_string, os_code
            regex (str): A valid PCRE aka regular expression

        Basic Usage:
            >>> from vFense.plugins.reports.search.hardware import RetrieveHardware
            >>> view_name = 'global'
            >>> search = RetrieveHardware(view_name='default')
            >>> search.memory_by_regex('os_code', 'linux')
            >>> search.memory_by_regex('os_string', 'Red*')

        Returns:
            An instance of ApiResults
        """
        valid_keys = self.fetch.get_valid_keys_for_type('memory')
        if key in valid_keys and self.sort_key in valid_keys:
            count, data = self.fetch.memory_by_regex(key, regex)
            return self._base(count, data)

        elif key not in valid_keys:
            return self._set_results_invalid_filter_key(key)

        else:
            return self._set_results_invalid_sort_key(key)

    def cpu_by_regex(self, key, regex):
        """Return all cpus by searching on a key and regex that maches
            the value.
        Args:
            key (str): The key you want to perform the search on.
                examples... computer_name, os_string, os_code
            regex (str): A valid PCRE aka regular expression

        Basic Usage:
            >>> from vFense.plugins.reports.search.hardware import RetrieveHardware
            >>> view_name = 'global'
            >>> search = RetrieveHardware(view_name='default')
            >>> search.cpu_by_regex('os_code', 'linux')
            >>> search.cpu_by_regex('os_string', 'Red*')

        Returns:
            An instance of ApiResults
        """
        valid_keys = self.fetch.get_valid_keys_for_type('cpu')
        if key in valid_keys and self.sort_key in valid_keys:
            count, data = self.fetch.memory_by_regex(key, regex)
            return self._base(count, data)

        elif key not in valid_keys:
            return self._set_results_invalid_filter_key(key)

        else:
            return self._set_results_invalid_sort_key(key)

    def nic_by_regex(self, key, regex):
        """Return all nics by searching on a key and regex that maches
            the value.
        Args:
            key (str): The key you want to perform the search on.
                examples... computer_name, os_string, os_code
            regex (str): A valid PCRE aka regular expression

        Basic Usage:
            >>> from vFense.plugins.reports.search.hardware import RetrieveHardware
            >>> view_name = 'global'
            >>> search = RetrieveHardware(view_name='default')
            >>> search.nic_by_regex('os_code', 'linux')
            >>> search.nic_by_regex('os_string', 'Red*')

        Returns:
            An instance of ApiResults
        """
        valid_keys = self.fetch.get_valid_keys_for_type('nic')
        if key in valid_keys and self.sort_key in valid_keys:
            count, data = self.fetch.nic_by_regex(key, regex)
            return self._base(count, data)

        elif key not in valid_keys:
            return self._set_results_invalid_filter_key(key)

        else:
            return self._set_results_invalid_sort_key(key)

    def storage_by_regex(self, key, regex):
        """Return all filesystems by searching on a key and regex that maches
            the value.
        Args:
            key (str): The key you want to perform the search on.
                examples... computer_name, os_string, os_code
            regex (str): A valid PCRE aka regular expression

        Basic Usage:
            >>> from vFense.plugins.reports.search.hardware import RetrieveHardware
            >>> view_name = 'global'
            >>> search = RetrieveHardware(view_name='default')
            >>> search.storage_by_regex('os_code', 'linux')
            >>> search.storage_by_regex('os_string', 'Red*')

        Returns:
            An instance of ApiResults
        """
        valid_keys = self.fetch.get_valid_keys_for_type('storage')
        if key in valid_keys and self.sort_key in valid_keys:
            count, data = self.fetch.nic_by_regex(key, regex)
            return self._base(count, data)

        elif key not in valid_keys:
            return self._set_results_invalid_filter_key(key)

        else:
            return self._set_results_invalid_sort_key(key)

    def display_by_regex(self, key, regex):
        """Return all displays by searching on a key and regex that maches
            the value.
        Args:
            key (str): The key you want to perform the search on.
                examples... computer_name, os_string, os_code
            regex (str): A valid PCRE aka regular expression

        Basic Usage:
            >>> from vFense.plugins.reports.search.hardware import RetrieveHardware
            >>> view_name = 'global'
            >>> search = RetrieveHardware(view_name='default')
            >>> search.display_by_regex('os_code', 'linux')
            >>> search.display_by_regex('os_string', 'Red*')

        Returns:
            An instance of ApiResults
        """
        valid_keys = self.fetch.get_valid_keys_for_type('display')
        if key in valid_keys and self.sort_key in valid_keys:
            count, data = self.fetch.nic_by_regex(key, regex)
            return self._base(count, data)

        elif key not in valid_keys:
            return self._set_results_invalid_filter_key(key)

        else:
            return self._set_results_invalid_sort_key(key)

    def cpu_by_os_code_and_by_regex(self, os_code, key, regex):
        """Return all cpus by filtering on the os_code and by searching
            on a key and regex that maches the value.
        Args:
            os_code (str): The operating system you want to filter on.
                examples... windows, darwin, linux
            key (str): The key you want to perform the search on.
                examples... computer_name, os_string, os_code
            regex (str): A valid PCRE aka regular expression

        Basic Usage:
            >>> from vFense.plugins.reports.search.hardware import RetrieveHardware
            >>> view_name = 'global'
            >>> search = RetrieveHardware(view_name='default')
            >>> search.cpu_by_os_code_and_by_regex(
                'linux', 'os_string', 'ubu'
            )
            >>> search.cpu_by_os_code_and_by_regex(
                'linux', 'computer_name', '^ns*'
            )

        Returns:
            An instance of ApiResults
        """
        valid_keys = self.fetch.get_valid_keys_for_type('cpu')
        if key in valid_keys and self.sort_key in valid_keys:
            count, data = self.fetch.cpu_by_os_code_and_by_regex(
                os_code, key, regex
            )
            return self._base(count, data)

        elif key not in valid_keys:
            return self._set_results_invalid_filter_key(key)

        else:
            return self._set_results_invalid_sort_key(key)

    def memory_by_os_code_and_by_regex(self, os_code, key, regex):
        """Return all memory by filtering on the os_code and by searching
            on a key and regex that maches the value.
        Args:
            os_code (str): The operating system you want to filter on.
                examples... windows, darwin, linux
            key (str): The key you want to perform the search on.
                examples... computer_name, os_string, os_code
            regex (str): A valid PCRE aka regular expression

        Basic Usage:
            >>> from vFense.plugins.reports.search.hardware import RetrieveHardware
            >>> view_name = 'global'
            >>> search = RetrieveHardware(view_name='default')
            >>> search.memory_by_os_code_and_by_regex(
                'linux', 'os_string', 'ubu'
            )
            >>> search.memory_by_os_code_and_by_regex(
                'linux', 'computer_name', '^ns*'
            )

        Returns:
            An instance of ApiResults
        """
        valid_keys = self.fetch.get_valid_keys_for_type('memory')
        if key in valid_keys and self.sort_key in valid_keys:
            count, data = self.fetch.memory_by_os_code_and_by_regex(
                os_code, key, regex
            )
            return self._base(count, data)

        elif key not in valid_keys:
            return self._set_results_invalid_filter_key(key)

        else:
            return self._set_results_invalid_sort_key(key)

    def display_by_os_code_and_by_regex(self, os_code, key, regex):
        """Return all displays by filtering on the os_code and by searching
            on a key and regex that maches the value.
        Args:
            os_code (str): The operating system you want to filter on.
                examples... windows, darwin, linux
            key (str): The key you want to perform the search on.
                examples... computer_name, os_string, os_code
            regex (str): A valid PCRE aka regular expression

        Basic Usage:
            >>> from vFense.plugins.reports.search.hardware import RetrieveHardware
            >>> view_name = 'global'
            >>> search = RetrieveHardware(view_name='default')
            >>> search.display_by_os_code_and_by_regex(
                'linux', 'os_string', 'ubu'
            )
            >>> search.display_by_os_code_and_by_regex(
                'linux', 'computer_name', '^ns*'
            )

        Returns:
            An instance of ApiResults
        """
        valid_keys = self.fetch.get_valid_keys_for_type('display')
        if key in valid_keys and self.sort_key in valid_keys:
            count, data = self.fetch.display_by_os_code_and_by_regex(
                os_code, key, regex
            )
            return self._base(count, data)

        elif key not in valid_keys:
            return self._set_results_invalid_filter_key(key)

        else:
            return self._set_results_invalid_sort_key(key)

    def storage_by_os_code_and_by_regex(self, os_code, key, regex):
        """Return all filesystems by filtering on the os_code and by searching
            on a key and regex that maches the value.
        Args:
            os_code (str): The operating system you want to filter on.
                examples... windows, darwin, linux
            key (str): The key you want to perform the search on.
                examples... computer_name, os_string, os_code
            regex (str): A valid PCRE aka regular expression

        Basic Usage:
            >>> from vFense.plugins.reports.search.hardware import RetrieveHardware
            >>> view_name = 'global'
            >>> search = RetrieveHardware(view_name='default')
            >>> search.storage_by_os_code_and_by_regex(
                'linux', 'os_string', 'ubu'
            )
            >>> search.storage_by_os_code_and_by_regex(
                'linux', 'computer_name', '^ns*'
            )

        Returns:
            An instance of ApiResults
        """
        valid_keys = self.fetch.get_valid_keys_for_type('storage')
        if key in valid_keys and self.sort_key in valid_keys:
            count, data = self.fetch.storage_by_os_code_and_by_regex(
                os_code, key, regex
            )
            return self._base(count, data)

        elif key not in valid_keys:
            return self._set_results_invalid_filter_key(key)

        else:
            return self._set_results_invalid_sort_key(key)

    def nic_by_os_code_and_by_regex(self, os_code, key, regex):
        """Return all nics by filtering on the os_code and by searching
            on a key and regex that maches the value.
        Args:
            os_code (str): The operating system you want to filter on.
                examples... windows, darwin, linux
            key (str): The key you want to perform the search on.
                examples... computer_name, os_string, os_code
            regex (str): A valid PCRE aka regular expression

        Basic Usage:
            >>> from vFense.plugins.reports.search.hardware import RetrieveHardware
            >>> view_name = 'global'
            >>> search = RetrieveHardware(view_name='default')
            >>> search.nic_by_os_code_and_by_regex(
                'linux', 'os_string', 'ubu'
            )
            >>> search.nic_by_os_code_and_by_regex(
                'linux', 'computer_name', '^ns*'
            )

        Returns:
            An instance of ApiResults
        """
        valid_keys = self.fetch.get_valid_keys_for_type('nic')
        if key in valid_keys and self.sort_key in valid_keys:
            count, data = self.fetch.nic_by_os_code_and_by_regex(
                os_code, key, regex
            )
            return self._base(count, data)

        elif key not in valid_keys:
            return self._set_results_invalid_filter_key(key)

        else:
            return self._set_results_invalid_sort_key(key)

    def cpu_by_os_string_and_by_regex(self, os_string, key, regex):
        """Return all cpus by filtering on the os_code and by searching
            on a key and regex that maches the value.
        Args:
            os_string (str): The operating system you want to filter on.
                examples... Windows 7 Professional N, Ubuntu 13.0.4
            key (str): The key you want to perform the search on.
                examples... computer_name, cores, cache_kb
            regex (str): A valid PCRE aka regular expression

        Basic Usage:
            >>> from vFense.plugins.reports.search.hardware import RetrieveHardware
            >>> view_name = 'global'
            >>> search = RetrieveHardware(view_name='default')
            >>> search.cpu_by_os_code_and_by_regex(
                'linux', 'os_string', 'ubu'
            )
            >>> search.cpu_by_os_code_and_by_regex(
                'linux', 'computer_name', '^ns*'
            )

        Returns:
            An instance of ApiResults
        """
        valid_keys = self.fetch.get_valid_keys_for_type('cpu')
        if key in valid_keys and self.sort_key in valid_keys:
            count, data = self.fetch.cpu_by_os_string_and_by_regex(
                os_string, key, regex
            )
            return self._base(count, data)

        elif key not in valid_keys:
            return self._set_results_invalid_filter_key(key)

        else:
            return self._set_results_invalid_sort_key(key)

    def memory_by_os_string_and_by_regex(self, os_string, key, regex):
        """Return memory by filtering on the os_string and by searching
            on a key and regex that maches the value.
        Args:
            os_string (str): The operating system you want to filter on.
                examples... Windows 7 Professional N, Ubuntu 13.0.4
            key (str): The key you want to perform the search on.
                examples... computer_name, name, total_memory
            regex (str): A valid PCRE aka regular expression

        Basic Usage:
            >>> from vFense.plugins.reports.search.hardware import RetrieveHardware
            >>> view_name = 'global'
            >>> search = RetrieveHardware(view_name='default')
            >>> search.cpu_by_os_string_and_by_regex(
                'linux', 'os_string', 'ubu'
            )
            >>> search.cpu_by_os_string_and_by_regex(
                'linux', 'computer_name', '^ns*'
            )

        Returns:
            An instance of ApiResults
        """
        valid_keys = self.fetch.get_valid_keys_for_type('memory')
        if key in valid_keys and self.sort_key in valid_keys:
            count, data = self.fetch.memory_by_os_string_and_by_regex(
                os_string, key, regex
            )
            return self._base(count, data)

        elif key not in valid_keys:
            return self._set_results_invalid_filter_key(key)

        else:
            return self._set_results_invalid_sort_key(key)

    def nic_by_os_string_and_by_regex(self, os_string, key, regex):
        """Return nics by filtering on the os_string and by searching
            on a key and regex that maches the value.
        Args:
            os_string (str): The operating system you want to filter on.
                examples... Windows 7 Professional N, Ubuntu 13.0.4
            key (str): The key you want to perform the search on.
                examples... computer_name, display_name, mac, ip_address
            regex (str): A valid PCRE aka regular expression

        Basic Usage:
            >>> from vFense.plugins.reports.search.hardware import RetrieveHardware
            >>> view_name = 'global'
            >>> search = RetrieveHardware(view_name='default')
            >>> search.cpu_by_os_string_and_by_regex(
                'linux', 'os_string', 'ubu'
            )
            >>> search.cpu_by_os_string_and_by_regex(
                'linux', 'computer_name', '^ns*'
            )

        Returns:
            An instance of ApiResults
        """
        valid_keys = self.fetch.get_valid_keys_for_type('nic')
        if key in valid_keys and self.sort_key in valid_keys:
            count, data = self.fetch.nic_by_os_string_and_by_regex(
                os_string, key, regex
            )
            return self._base(count, data)

        elif key not in valid_keys:
            return self._set_results_invalid_filter_key(key)

        else:
            return self._set_results_invalid_sort_key(key)

    def display_by_os_string_and_by_regex(self, os_string, key, regex):
        """Return displays by filtering on the os_string and by searching
            on a key and regex that maches the value.
        Args:
            os_string (str): The operating system you want to filter on.
                examples... Windows 7 Professional N, Ubuntu 13.0.4
            key (str): The key you want to perform the search on.
                examples... computer_name, display_name, mac, ip_address
            regex (str): A valid PCRE aka regular expression

        Basic Usage:
            >>> from vFense.plugins.reports.search.hardware import RetrieveHardware
            >>> view_name = 'global'
            >>> search = RetrieveHardware(view_name='default')
            >>> search.display_by_os_string_and_by_regex(
                'linux', 'os_string', 'ubu'
            )
            >>> search.display_by_os_string_and_by_regex(
                'linux', 'computer_name', '^ns*'
            )

        Returns:
            An instance of ApiResults
        """
        valid_keys = self.fetch.get_valid_keys_for_type('display')
        if key in valid_keys and self.sort_key in valid_keys:
            count, data = self.fetch.display_by_os_string_and_by_regex(
                os_string, key, regex
            )
            return self._base(count, data)

        elif key not in valid_keys:
            return self._set_results_invalid_filter_key(key)

        else:
            return self._set_results_invalid_sort_key(key)

    def storage_by_os_string_and_by_regex(self, os_string, key, regex):
        """Return filesystems by filtering on the os_string and by searching
            on a key and regex that maches the value.
        Args:
            os_string (str): The operating system you want to filter on.
                examples... Windows 7 Professional N, Ubuntu 13.0.4
            key (str): The key you want to perform the search on.
                examples... computer_name, display_name, mac, ip_address
            regex (str): A valid PCRE aka regular expression

        Basic Usage:
            >>> from vFense.plugins.reports.search.hardware import RetrieveHardware
            >>> view_name = 'global'
            >>> search = RetrieveHardware(view_name='default')
            >>> search.display_by_os_string_and_by_regex(
                'linux', 'os_string', 'ubu'
            )
            >>> search.display_by_os_string_and_by_regex(
                'linux', 'computer_name', '^ns*'
            )

        Returns:
            An instance of ApiResults
        """
        valid_keys = self.fetch.get_valid_keys_for_type('storage')
        if key in valid_keys and self.sort_key in valid_keys:
            count, data = self.fetch.storage_by_os_string_and_by_regex(
                os_string, key, regex
            )
            return self._base(count, data)

        elif key not in valid_keys:
            return self._set_results_invalid_filter_key(key)

        else:
            return self._set_results_invalid_sort_key(key)

    def cpu_by_arch_and_by_regex(self, arch, key, regex):
        """Return filesystems by filtering on the os_string and by searching
            on a key and regex that maches the value.
        Args:
            arch (str): The operating system you want to filter on.
                examples... 32, 64
            key (str): The key you want to perform the search on.
                examples... computer_name, display_name, mac, ip_address
            regex (str): A valid PCRE aka regular expression

        Basic Usage:
            >>> from vFense.plugins.reports.search.hardware import RetrieveHardware
            >>> view_name = 'global'
            >>> search = RetrieveHardware(view_name='default')
            >>> search.cpu_by_arch_and_by_regex(
                'linux', 'os_string', 'ubu'
            )
            >>> search.cpu_by_arch_and_by_regex(
                'linux', 'computer_name', '^ns*'
            )

        Returns:
            An instance of ApiResults
        """
        valid_keys = self.fetch.get_valid_keys_for_type('cpu')
        if key in valid_keys and self.sort_key in valid_keys:
            count, data = self.fetch.cpu_by_arch_and_by_regex(
                arch, key, regex
            )
            return self._base(count, data)

        elif key not in valid_keys:
            return self._set_results_invalid_filter_key(key)

        else:
            return self._set_results_invalid_sort_key(key)

    def memory_by_arch_and_by_regex(self, arch, key, regex):
        """Return memory by filtering on the os_string and by searching
            on a key and regex that maches the value.
        Args:
            arch (str): The operating system you want to filter on.
                examples... 32, 64
            key (str): The key you want to perform the search on.
                examples... computer_name, display_name, mac, ip_address
            regex (str): A valid PCRE aka regular expression

        Basic Usage:
            >>> from vFense.plugins.reports.search.hardware import RetrieveHardware
            >>> view_name = 'global'
            >>> search = RetrieveHardware(view_name='default')
            >>> search.memory_by_arch_and_by_regex(
                'linux', 'os_string', 'ubu'
            )
            >>> search.memory_by_arch_and_by_regex(
                'linux', 'computer_name', '^ns*'
            )

        Returns:
            An instance of ApiResults
        """
        valid_keys = self.fetch.get_valid_keys_for_type('memory')
        if key in valid_keys and self.sort_key in valid_keys:
            count, data = self.fetch.memory_by_arch_and_by_regex(
                arch, key, regex
            )
            return self._base(count, data)

        elif key not in valid_keys:
            return self._set_results_invalid_filter_key(key)

        else:
            return self._set_results_invalid_sort_key(key)

    def nic_by_arch_and_by_regex(self, arch, key, regex):
        """Return nic by filtering on the os_string and by searching
            on a key and regex that maches the value.
        Args:
            arch (str): The operating system you want to filter on.
                examples... 32, 64
            key (str): The key you want to perform the search on.
                examples... computer_name, display_name, mac, ip_address
            regex (str): A valid PCRE aka regular expression

        Basic Usage:
            >>> from vFense.plugins.reports.search.hardware import RetrieveHardware
            >>> view_name = 'global'
            >>> search = RetrieveHardware(view_name='default')
            >>> search.nic_by_arch_and_by_regex(
                'linux', 'os_string', 'ubu'
            )
            >>> search.nic_by_arch_and_by_regex(
                'linux', 'computer_name', '^ns*'
            )

        Returns:
            An instance of ApiResults
        """
        valid_keys = self.fetch.get_valid_keys_for_type('nic')
        if key in valid_keys and self.sort_key in valid_keys:
            count, data = self.fetch.nic_by_arch_and_by_regex(
                arch, key, regex
            )
            return self._base(count, data)

        elif key not in valid_keys:
            return self._set_results_invalid_filter_key(key)

        else:
            return self._set_results_invalid_sort_key(key)

    def display_by_arch_and_by_regex(self, arch, key, regex):
        """Return display by filtering on the os_string and by searching
            on a key and regex that maches the value.
        Args:
            arch (str): The operating system you want to filter on.
                examples... 32, 64
            key (str): The key you want to perform the search on.
                examples... computer_name, display_name, mac, ip_address
            regex (str): A valid PCRE aka regular expression

        Basic Usage:
            >>> from vFense.plugins.reports.search.hardware import RetrieveHardware
            >>> view_name = 'global'
            >>> search = RetrieveHardware(view_name='default')
            >>> search.display_by_arch_and_by_regex(
                'linux', 'os_string', 'ubu'
            )
            >>> search.display_by_arch_and_by_regex(
                'linux', 'computer_name', '^ns*'
            )

        Returns:
            An instance of ApiResults
        """
        valid_keys = self.fetch.get_valid_keys_for_type('display')
        if key in valid_keys and self.sort_key in valid_keys:
            count, data = self.fetch.display_by_arch_and_by_regex(
                arch, key, regex
            )
            return self._base(count, data)

        elif key not in valid_keys:
            return self._set_results_invalid_filter_key(key)

        else:
            return self._set_results_invalid_sort_key(key)

    def storage_by_arch_and_by_regex(self, arch, key, regex):
        """Return filesystems by filtering on the os_string and by searching
            on a key and regex that maches the value.
        Args:
            arch (str): The operating system you want to filter on.
                examples... 32, 64
            key (str): The key you want to perform the search on.
                examples... computer_name, display_name, mac, ip_address
            regex (str): A valid PCRE aka regular expression

        Basic Usage:
            >>> from vFense.plugins.reports.search.hardware import RetrieveHardware
            >>> view_name = 'global'
            >>> search = RetrieveHardware(view_name='default')
            >>> search.display_by_arch_and_by_regex(
                'linux', 'os_string', 'ubu'
            )
            >>> search.display_by_arch_and_by_regex(
                'linux', 'computer_name', '^ns*'
            )

        Returns:
            An instance of ApiResults
        """
        valid_keys = self.fetch.get_valid_keys_for_type('storage')
        if key in valid_keys and self.sort_key in valid_keys:
            count, data = self.fetch.storage_by_arch_and_by_regex(
                arch, key, regex
            )
            return self._base(count, data)

        elif key not in valid_keys:
            return self._set_results_invalid_filter_key(key)

        else:
            return self._set_results_invalid_sort_key(key)
