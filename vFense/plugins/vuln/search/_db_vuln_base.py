from vFense.db.client import db_create_close, r
from vFense.core.decorators import catch_it, time_it
from vFense.plugins.vuln._db_model import (
    VulnerabilityIndexes, VulnerabilityKeys
)
from vFense.search._db_base import FetchBase

class FetchVulnBase(FetchBase):
    """Vulnerabilty base search class.
    Args:
        collection (str): The name of the database collection to use.
    Kwargs:
        sort_key (str): Which key to sort by. default=date_posted

        For the rest of the kwargs, please check vFense.search._db_base

    Basic Usage:
        >>> from vFense.plugins.vuln.search._db_vuln_base import FetchVulnBase
        >>> table = 'redhat_vulnerabilities'
        >>> count = 30
        >>> offset = 0
        >>> sort = 'desc'
        >>> sort_key = 'date_posted'
        >>> search = FetchVulnBase(table, count, offset, sort, sort_key)

    Attributes:
        self.collection
        self.count
        self.offset
        self.sort
        self.sort_key
    """
    def __init__(
        self, collection=None, sort_key=VulnerabilityKeys.DatePosted, **kwargs
    ):
        super(FetchVulnBase, self).__init__(**kwargs)
        self.collection = collection

    @time_it
    @catch_it((0, []))
    @db_create_close
    def by_id(self, vulnerability_id, conn=None):
        """Retrieve vulnerabilities by vulnerability id.
        Args:
            vulnerability_id (str): Examples...
                USN-973-1 | RHSA-2014:0924-01| MS99-053

        Basic Usage:
            >>> from vFense.plugins.vuln.search._db_vuln_base import FetchVulnBase
            >>> search = FetchVulnBase()
            >>> search.by_id("RHSA-2014:0924-01")

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
        base_filter = self._set_base_query()
        merge_hash = self._set_merge_hash()

        count = (
            base_filter
            .get_all(vulnerability_id)
            .count()
            .run(conn)
        )

        data = list(
            base_filter
            .get_all(vulnerability_id)
            .order_by(self.sort(self.sort_key))
            .skip(self.offset)
            .limit(self.count)
            .merge(merge_hash)
            .run(conn)
        )

        return(count, data)

    @time_it
    @catch_it((0, []))
    @db_create_close
    def by_app_name_and_version(self, name, version, conn=None):
        """Retrieve vulnerability information by the name and the version
            of the application.

        Args:
            name (str): The name of the application you are searching for.
            version (str): The version of the application you are
                searching for.

        Basic Usage:
            >>> from vFense.plugins.vuln.search._db_vuln_base import FetchVulnBase
            >>> search = FetchVulnBase()
            >>> search.by_app_name_and_version("kernel-kdump-devel", "2.6.32431.20.5.el6")

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
        base_filter = self._set_base_query()
        merge_hash = self._set_merge_hash()

        count = (
            base_filter
            .get_all(
                [name, version],
                index=VulnerabilityIndexes.NameAndVersion
            )
            .count()
            .run(conn)
        )

        data = list(
            base_filter
            .get_all(
                [name, version],
                index=VulnerabilityIndexes.NameAndVersion
            )
            .order_by(self.sort(self.sort_key))
            .skip(self.offset)
            .limit(self.count)
            .merge(merge_hash)
            .run(conn)
        )

        return(count, data)


    def _set_base_query(self):
        base = r.table(self.collection)
        return base


    def _set_merge_hash(self):
        merge_hash = (
            lambda x:
            {
                VulnerabilityKeys.DatePosted: (
                    x[VulnerabilityKeys.DatePosted].to_epoch_time()
                ),
            }
        )

        return merge_hash
