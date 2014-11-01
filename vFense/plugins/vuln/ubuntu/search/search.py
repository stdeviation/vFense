import logging
import logging.config
from vFense._constants import VFENSE_LOGGING_CONFIG

from vFense.core.results import ApiResultKeys
from vFense.core.decorators import time_it
from vFense.core._constants import (
    SortValues, DefaultQueryValues
)
from vFense.plugins.vuln.ubuntu._db_model import UbuntuVulnerabilityKeys
from vFense.plugins.vuln.ubuntu.search._db import FetchUbuntuVulns

from vFense.core.status_codes import (
    GenericCodes, GenericFailureCodes
)

logging.config.fileConfig(VFENSE_LOGGING_CONFIG)
logger = logging.getLogger('cve')

class RetrieveUbuntuVulns(object):
    def __init__(
        self, count=DefaultQueryValues.COUNT,
        offset=DefaultQueryValues.OFFSET, sort=SortValues.DESC,
        sort_key=UbuntuVulnerabilityKeys.DatePosted
        ):

        self.count = count
        self.offset = offset
        self.sort = sort

        self.valid_keys_to_filter_by = (
            [
                UbuntuVulnerabilityKeys.VulnerabilityId,
                UbuntuVulnerabilityKeys.DatePosted,
            ]
        )

        valid_keys_to_sort_by = (
            [
                UbuntuVulnerabilityKeys.VulnerabilityId,
                UbuntuVulnerabilityKeys.DatePosted,
            ]
        )

        if sort_key in valid_keys_to_sort_by:
            self.sort_key = sort_key
        else:
            self.sort_key = UbuntuVulnerabilityKeys.VulnerabilityId

        self.fetch_vulns = (
            FetchUbuntuVulns(
                count=self.count, offset=self.offset,
                sort=self.sort, sort_key=self.sort_key
            )
        )

    @time_it
    def by_id(self, bulletin_id):
        """Retrieve vulnerability by id.
        Args:
            bulletin_id (str): The Ubuntu USN bulletin id.
                Example: 'USN-2250-1'

        Basic Usage:
            >>> from vFense.plugins.vuln.ubuntu.search.search import RetrieveUbuntuVulns
            >>> search = RetrieveUbuntuVulns()
            >>> search.by_id('USN-2250-1')

        Returns:
            List of dictionairies.
        """
        count, data = self.fetch_vulns.by_id(bulletin_id)
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
