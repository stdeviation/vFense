import re
from vFense.supported_platforms import REDHAT_DISTROS
from vFense.plugins.vuln import Vulnerability
from vFense.plugins.vuln.ubuntu import Ubuntu
from vFense.plugins.vuln.ubuntu.search._db import FetchUbuntuVulns
from vFense.plugins.vuln.redhat import Redhat
from vFense.plugins.vuln.redhat.search._db import FetchRedhatVulns
from vFense.plugins.vuln.windows import Windows
from vFense.plugins.vuln.windows.search._db import FetchWindowsVulns
from vFense.core.results import (
    ApiResultKeys
)


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


    def by_vuln_id(self, vuln_id):
        """Search by name and version or by kb
        Kwargs:
            name (str): The name of the application you are searching for.

        Basic Usage:
            >>> from vFense.plugins.vuln.search.vuln_search import FetchVulns
            >>> search = FetchVulns()
            >>> search.by_app_info(name="kernel-kdump-devel", version="2.6.32431.20.5.el6")

        Returns:
            Tuple (count, list of dictionaries)
        """

        data = Vulnerability()

        count, data = self.search.by_id(vuln_id)
        if count > 0 :
            data = data[0]
            if count > 0 :
                if self.redhat:
                    data = Redhat(**data)
                elif self.ubuntu:
                    data = Ubuntu(**data)
                else:
                    data = Windows(**data)

        return data


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

    def _set_results(self, gen_status_code, vfense_status_code,
                     msg, count, data):

        results = {
            ApiResultKeys.GENERIC_STATUS_CODE: gen_status_code,
            ApiResultKeys.VFENSE_STATUS_CODE: vfense_status_code,
            ApiResultKeys.MESSAGE: msg,
            ApiResultKeys.COUNT: count,
            ApiResultKeys.DATA: data,
        }

        return results
