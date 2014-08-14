import re
from vFense.supported_platforms import REDHAT_DISTROS
from vFense.core._constants import SortValues, DefaultQueryValues
from vFense.plugins.vuln._db_model import (
    VulnerabilityIndexes, VulnerabilityKeys
)
from vFense.plugins.vuln.ubuntu.search._db import FetchUbuntuVulns
from vFense.plugins.vuln.redhat.search._db import FetchRedhatVulns
from vFense.plugins.vuln.windows.search._db import FetchWindowsVulns


class FetchVulns(object):
    def __init__(self, os_string, **kwargs):
        self.os_string = os_string
        if re.search(r'Windows', os_string, re.IGNORECASE):
            self.search = FetchWindowsVulns(**kwargs)

        elif re.search(r'Ubuntu|Mint', os_string, re.IGNORECASE):
            self.search = FetchUbuntuVulns(**kwargs)

        elif re.search('|'.join(REDHAT_DISTROS), os_string, re.IGNORECASE):
            self.search = FetchRedhatVulns(**kwargs)


    def by_app_info(self, name=None, version=None, kb=None):
        data = None
        if name and version:
            count, data = self.search.by_name_and_version(name, version)
            if count > 0 :
                data = data[0]
        elif kb:
            count, data = self.search.by_kb(kb)
            if count > 0 :
                data = data[0]

        return data


