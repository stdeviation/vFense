import re
from vFense.supported_platforms import REDHAT_DISTROS
from vFense.plugins.vuln import Vulnerability
from vFense.plugins.vuln.ubuntu import Ubuntu
from vFense.plugins.vuln.ubuntu.search._db import FetchUbuntuVulns
from vFense.plugins.vuln.redhat import Redhat
from vFense.plugins.vuln.redhat.search._db import FetchRedhatVulns
from vFense.plugins.vuln.windows import Windows
from vFense.plugins.vuln.windows.search._db import FetchWindowsVulns


class FetchVulns(object):
    """Search vulnerabilities by the os_string. This is mainly
        so you do not have to know the different collections to search by.

    Args:
        os_string (str): Example .. "Ubuntu 14.04 trusty"

    Kwargs:
        count (int): The number of results to return.
        offset (int): The next set of results to return,
            starting from the offset.
        sort (str): Sort ascending or descending.
            valid values asc or desc
            default=desc
        sort_key (str): Which key to sort by. default=date_posted

    Basic Usage:
        >>> from vFense.plugins.vuln.search.vuln_search import FetchVulns
        >>> os_string = 'Ubuntu 14.04 trusty'
        >>> count = 30
        >>> offset = 0
        >>> sort = 'desc'
        >>> sort_key = 'date_posted'
        >>> search = FetchVulns(os_string, count, offset, sort, sort_key)

    Attributes:
        self.os_string
        self.collection
        self.count
        self.offset
        self.sort
        self.sort_key
        self.search
        self.redhat
        self.ubuntu
        self.windows

    """
    def __init__(self, os_string, **kwargs):
        self.os_string = os_string
        self.windows = False
        self.ubuntu = False
        self.redhat = False
        if re.search(r'Windows', os_string, re.IGNORECASE):
            self.search = FetchWindowsVulns(**kwargs)
            self.windows = True

        elif re.search(r'Ubuntu|Mint', os_string, re.IGNORECASE):
            self.search = FetchUbuntuVulns(**kwargs)
            self.ubuntu = True

        elif re.search('|'.join(REDHAT_DISTROS), os_string, re.IGNORECASE):
            self.search = FetchRedhatVulns(**kwargs)
            self.redhat = True


    def by_app_info(self, name=None, version=None, kb=None):
        """Search by name and version or by kb
        Kwargs:
            name (str): The name of the application you are searching for.
            version (str): The version of the application you are
            kb (str): The knowledge base. Example.. KB246731

        Basic Usage:
            >>> from vFense.plugins.vuln.search.vuln_search import FetchVulns
            >>> search = FetchVulns()
            >>> search.by_app_info(name="kernel-kdump-devel", version="2.6.32431.20.5.el6")

        Returns:
            Tuple (count, list of dictionaries)
[
    1,
    [
        {
            "os_strings": null,
            "support_url": "https://rhn.redhat.com/errata/RHSA-2014-0924.html",
            "apps": {
                "version": "2.6.32431.20.5.el6",
                "arch": "s390x",
                "app_id": "8fa7d3d638a96859f178803e7b6d1685821f3ee59651d7d4f53c2f0a993fe737",
                "name": "kernel-kdump-devel"
            },
            "cve_ids": [
                "CVE-2014-4699",
                "CVE-2014-4943"
            ],
            "details": "The kernel packages contain the Linux kernel, the core of any Linux\noperating system.\n\n* It was found that th
e Linux kernel's ptrace subsystem allowed a traced\nprocess' instruction pointer to be set to a non-canonical memory address\nwithout fo
rcing the non-sysret code path when returning to user space.\nA local, unprivileged user could use this flaw to crash the system or,\npo
tentially, escalate their privileges on the system. (CVE-2014-4699,\nImportant)\n\nNote: The CVE-2014-4699 issue only affected systems u
sing an Intel CPU.\n\n* A flaw was found in the way the pppol2tp_setsockopt() and\npppol2tp_getsockopt() functions in the Linux kernel's
 PPP over L2TP\nimplementation handled requests with a non-SOL_PPPOL2TP socket option\nlevel. A local, unprivileged user could use this
flaw to escalate their\nprivileges on the system. (CVE-2014-4943, Important)\n\nRed Hat would like to thank Andy Lutomirski for reportin
g CVE-2014-4699,\nand Sasha Levin for reporting CVE-2014-4943.\n\nAll kernel users are advised to upgrade to these updated packages, whi
ch\ncontain backported patches to correct these issues. The system must be\nrebooted for this update to take effect.",
            "date_posted": 1406088000,
            "vulnerability_id": "RHSA-2014:0924-01"
        }
    ]
]
        """
        data = Vulnerability()

        if name and version:
            count, data = self.search.by_app_name_and_version(name, version)
            if count > 0 :
                data = data[0]
                if self.redhat:
                    data = Redhat(**data)
                else:
                    data = Ubuntu(**data)
        elif kb:
            count, data = self.search.by_component_kb(kb)
            if count > 0 :
                data = data[0]
                data = Windows(**data)

        return data
