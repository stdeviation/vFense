from vFense.core.agent._constants import AgentCommonKeys
from vFense.core.agent._db_model import AgentKeys
from vFense.core.agent.search._db import FetchAgents
from vFense.core.decorators import time_it
from vFense.search.base import RetrieveBase

class RetrieveAgents(RetrieveBase):
    def __init__(self, **kwargs):
        super(RetrieveAgents, self).__init__(**kwargs)

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

        self.fetch_agents = (
            FetchAgents(
                view_name=self.view_name, count=self.count,
                offset=self.offset, sort=self.sort, sort_key=self.sort_key
            )
        )

    @time_it
    def by_id(self, agent_id):
        """Query agents by computer and display name.
        Args:
            agent_id (str): The 36 character UUID fo the agent you
                are retrieving.

        Basic Usage:
            >>> from vFense.core.agent.search.search import RetrieveAgents
            >>> view_name = 'default'
            >>> search_agents = RetrieveAgents(view_name='default')
            >>> search_agents.by_id('74b70fcd-9ed5-4cfd-9779-a45d60478aa3')

        Returns:
            List of dictionairies.
            {
                "count": 1,
                "uri": null,
                "rv_status_code": 1001,
                "http_method": null,
                "http_status": 200,
                "message": null,
                "data": [
                    {
                        "display_name": null,
                        "environment": "Production",
                        "tags": [
                            {
                                "tag_name": "Foo Bar",
                                "tag_id": "6ef12d9d-a5a0-49c8-9890-206a7b362ce4"
                            }
                        ],
                        "available_vulnerabilities": 8,
                        "os_code": "linux",
                        "available_updates": 17,
                        "agent_status": "up",
                        "agent_id": "d4119b36-fe3c-4973-84c7-e8e3d72a3e02",
                        "computer_name": "ubuntu",
                        "os_string": "Ubuntu 12.04",
                        "needs_reboot": "no",
                        "host_name": ""
                    }
                ]
            }
        """
        count, data = self.fetch_agents.by_id(agent_id)
        return self._base(count, data)

    @time_it
    def by_name(self, query):
        """Query agents by computer and display name.
        Args:
            name (str): The regex you are searching by

        Basic Usage:
            >>> from vFense.core.agent.search.search import RetrieveAgents
            >>> view_name = 'default'
            >>> search_agents = RetrieveAgents(view_name='default')
            >>> search_agents.by_name('ubu')

        Returns:
            List of dictionairies.
            {
                "count": 1,
                "uri": null,
                "rv_status_code": 1001,
                "http_method": null,
                "http_status": 200,
                "message": null,
                "data": [
                    {
                        "display_name": null,
                        "environment": "Production",
                        "tags": [
                            {
                                "tag_name": "Foo Bar",
                                "tag_id": "6ef12d9d-a5a0-49c8-9890-206a7b362ce4"
                            }
                        ],
                        "available_vulnerabilities": 8,
                        "os_code": "linux",
                        "available_updates": 17,
                        "agent_status": "up",
                        "agent_id": "d4119b36-fe3c-4973-84c7-e8e3d72a3e02",
                        "computer_name": "ubuntu",
                        "os_string": "Ubuntu 12.04",
                        "needs_reboot": "no",
                        "host_name": ""
                    }
                ]
            }
        """
        count, data = self.fetch_agents.by_name(query)
        return self._base(count, data)

    @time_it
    def all(self):
        """Retrieve all agents.
        Basic Usage:
            >>> from vFense.core.agent.search.search import RetrieveAgents
            >>> view_name = 'default'
            >>> search_agents = RetrieveAgents(view_name='default')
            >>> search_agents.all()

        Returns:
            List of dictionairies.
            [
                {
                    "display_name": null,
                    "environment": "Production",
                    "tags": [
                        {
                            "tag_name": "Foo Bar",
                            "tag_id": "6ef12d9d-a5a0-49c8-9890-206a7b362ce4"
                        }
                    ],
                    "available_vulnerabilities": 8,
                    "os_code": "linux",
                    "available_updates": 17,
                    "agent_status": "up",
                    "agent_id": "d4119b36-fe3c-4973-84c7-e8e3d72a3e02",
                    "computer_name": "ubuntu",
                    "os_string": "Ubuntu 12.04",
                    "needs_reboot": "no",
                    "host_name": ""
                }
            ]
        """
        count, data = self.fetch_agents.all()
        return self._base(count, data)

    @time_it
    def by_key_and_val(self, fkey, fval):
        """Filter agents by a key and value.
        Args:
        fkey (str): The key you are filtering on.
            fval (str): The value for the key you are filtering on.

        Basic Usage:
            >>> from vFense.core.agent.search.search import RetrieveAgents
            >>> view_name = 'default'
            >>> fkey = 'os_code'
            >>> fval = 'linux'
            >>> search_agents = RetrieveAgents(view_name='default')
            >>> search_agents.by_key_and_val(fkey, fval)

        Returns:
            List of dictionairies.
            [
                {
                    "display_name": null,
                    "environment": "Production",
                    "tags": [
                        {
                            "tag_name": "Foo Bar",
                            "tag_id": "6ef12d9d-a5a0-49c8-9890-206a7b362ce4"
                        }
                    ],
                    "available_vulnerabilities": 8,
                    "os_code": "linux",
                    "available_updates": 17,
                    "agent_status": "up",
                    "agent_id": "d4119b36-fe3c-4973-84c7-e8e3d72a3e02",
                    "computer_name": "ubuntu",
                    "os_string": "Ubuntu 12.04",
                    "needs_reboot": "no",
                    "host_name": ""
                }
            ]
        """
        count = 0
        data = []

        if fkey in self.valid_keys_to_filter_by:
            count, data = self.fetch_agents.by_key_and_val(fkey, fval)
            return self._base(count, data)

        else:
            return self._set_results_invalid_filter_key(fkey)

    @time_it
    def by_key_and_val_and_query(self, fkey, fval, query):
        """Filter agents based on a key and value, while
            searching by computer and display name.
        Args:
            fkey (str): The key you are filtering on.
            fval (str): The value for the key you are filtering on.

        Basic Usage:
            >>> from vFense.core.agent.search.search import RetrieveAgents
            >>> view_name = 'default'
            >>> fkey = 'os_code'
            >>> fval = 'linux'
            >>> query = 'ubu'
            >>> search_agents = RetrieveAgents(view_name='default')
            >>> search_agents.by_key_and_value_and_query(fkey, fval, query)

        Returns:
            List of dictionairies.
            [
                {
                    "display_name": null,
                    "environment": "Production",
                    "tags": [
                        {
                            "tag_name": "Foo Bar",
                            "tag_id": "6ef12d9d-a5a0-49c8-9890-206a7b362ce4"
                        }
                    ],
                    "available_vulnerabilities": 8,
                    "os_code": "linux",
                    "available_updates": 17,
                    "agent_status": "up",
                    "agent_id": "d4119b36-fe3c-4973-84c7-e8e3d72a3e02",
                    "computer_name": "ubuntu",
                    "os_string": "Ubuntu 12.04",
                    "needs_reboot": "no",
                    "host_name": ""
                }
            ]
        """
        count = 0
        data = []

        if fkey in self.valid_keys_to_filter_by:
            count, data = (
                self.fetch_agents.by_key_and_val_and_query(fkey, fval, query)
            )
            return self._base(count, data)

        else:
            return self._set_results_invalid_filter_key(fkey)

    @time_it
    def by_ip(self, ip):
        """Search agents based on an ip address.
        Args:
            ip (str): The ip address you are searching for.

        Basic Usage:
            >>> from vFense.core.agent.search.search import RetrieveAgents
            >>> view_name = 'default'
            >>> ip = '192.168.0.101'
            >>> search_agents = RetrieveAgents(view_name='default')
            >>> search_agents.by_ip(ip)

        Returns:
            List of dictionairies.
            [
                {
                    "display_name": null,
                    "environment": "Production",
                    "tags": [
                        {
                            "tag_name": "Foo Bar",
                            "tag_id": "6ef12d9d-a5a0-49c8-9890-206a7b362ce4"
                        }
                    ],
                    "available_vulnerabilities": 8,
                    "os_code": "linux",
                    "available_updates": 17,
                    "agent_status": "up",
                    "agent_id": "d4119b36-fe3c-4973-84c7-e8e3d72a3e02",
                    "computer_name": "ubuntu",
                    "os_string": "Ubuntu 12.04",
                    "needs_reboot": "no",
                    "host_name": ""
                }
            ]
        """
        count, data = self.fetch_agents.by_ip(ip)
        return self._base(count, data)

    @time_it
    def by_ip_and_filter(self, ip, fkey, fval):
        """Search agents by ip address while filtering
            based on a key and value.
        Args:
            ip (str): The ip address you are searching for.
            fkey (str): The key you are filtering on.
            fval (str): The value for the key you are filtering on.

        Basic Usage:
            >>> from vFense.core.agent.search.search import RetrieveAgents
            >>> view_name = 'default'
            >>> ip = '192.168'
            >>> fkey = 'os_code'
            >>> fval = 'linux'
            >>> search_agents = RetrieveAgents(view_name='default')
            >>> search_agents.by_ip_and_filter(ip, fkey, fval)

        Returns:
            List of dictionairies.
            [
                {
                    "display_name": null,
                    "environment": "Production",
                    "tags": [
                        {
                            "tag_name": "Foo Bar",
                            "tag_id": "6ef12d9d-a5a0-49c8-9890-206a7b362ce4"
                        }
                    ],
                    "available_vulnerabilities": 8,
                    "os_code": "linux",
                    "available_updates": 17,
                    "agent_status": "up",
                    "agent_id": "d4119b36-fe3c-4973-84c7-e8e3d72a3e02",
                    "computer_name": "ubuntu",
                    "os_string": "Ubuntu 12.04",
                    "needs_reboot": "no",
                    "host_name": ""
                }
            ]
        """
        count = 0
        data = []
        if fkey in self.valid_keys_to_filter_by:
            count, data = self.fetch_agents.by_ip_and_filter(ip, fkey, fval)
            return self._base(count, data)

        else:
            return self._set_results_invalid_filter_key(fkey)

    @time_it
    def by_mac(self, mac):
        """Search agents based on an mac address.
        Args:
            mac (str): The mac address you are searching for.

        Basic Usage:
            >>> from vFense.core.agent.search.search import RetrieveAgents
            >>> view_name = 'default'
            >>> mac = '000c292672d6'
            >>> search_agents = RetrieveAgents(view_name='default')
            >>> search_agents.by_mac(mac)

        Returns:
            List of dictionairies.
            [
                {
                    "display_name": null,
                    "environment": "Production",
                    "tags": [
                        {
                            "tag_name": "Foo Bar",
                            "tag_id": "6ef12d9d-a5a0-49c8-9890-206a7b362ce4"
                        }
                    ],
                    "available_vulnerabilities": 8,
                    "os_code": "linux",
                    "available_updates": 17,
                    "agent_status": "up",
                    "agent_id": "d4119b36-fe3c-4973-84c7-e8e3d72a3e02",
                    "computer_name": "ubuntu",
                    "os_string": "Ubuntu 12.04",
                    "needs_reboot": "no",
                    "host_name": ""
                }
            ]
        """
        count, data = self.fetch_agents.by_mac(mac)
        return self._base(count, data)

    @time_it
    def by_mac_and_filter(self, mac, fkey, fval):
        """Search agents by mac address while filtering
            based on a key and value.
        Args:
            mac (str): The mac address you are searching for.
            fkey (str): The key you are filtering on.
            fval (str): The value for the key you are filtering on.

        Basic Usage:
            >>> from vFense.core.agent.search.search import RetrieveAgents
            >>> view_name = 'default'
            >>> mac = '000c292672d6'
            >>> fkey = 'os_code'
            >>> fval = 'linux'
            >>> search_agents = RetrieveAgents(view_name='default')
            >>> search_agents.by_mac_and_filter(mac, fkey, fval)

        Returns:
            List of dictionairies.
            [
                {
                    "display_name": null,
                    "environment": "Production",
                    "tags": [
                        {
                            "tag_name": "Foo Bar",
                            "tag_id": "6ef12d9d-a5a0-49c8-9890-206a7b362ce4"
                        }
                    ],
                    "available_vulnerabilities": 8,
                    "os_code": "linux",
                    "available_updates": 17,
                    "agent_status": "up",
                    "agent_id": "d4119b36-fe3c-4973-84c7-e8e3d72a3e02",
                    "computer_name": "ubuntu",
                    "os_string": "Ubuntu 12.04",
                    "needs_reboot": "no",
                    "host_name": ""
                }
            ]
        """
        count = 0
        data = []
        if fkey in self.valid_keys_to_filter_by:
            count, data = self.fetch_agents.by_mac_and_filter(mac, fkey, fval)
            return self._base(count, data)

        else:
            return self._set_results_invalid_filter_key(fkey)
