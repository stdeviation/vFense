import logging
import logging.config
from vFense import VFENSE_LOGGING_CONFIG

from vFense.result.error_messages import GenericResults, PackageResults
from vFense.result._constants import ApiResultKeys
from vFense.core.decorators import time_it
from vFense.core._constants import (
    SortValues, DefaultQueryValues, SortLogic
)
from vFense.plugins.vuln.cve._db_model import CveKeys
from vFense.plugins.vuln.cve._constants import *
from vFense.plugins.vuln.cve.search._db import FetchCves

from vFense.result.status_codes import (
    GenericCodes, GenericFailureCodes
)

logging.config.fileConfig(VFENSE_LOGGING_CONFIG)
logger = logging.getLogger('cve')

class RetrieveCVEs(object):
    def __init__(
        self, count=DefaultQueryValues.COUNT,
        offset=DefaultQueryValues.OFFSET, sort=SortValues.DESC,
        sort_key=CveKeys.CvePublishedDate
        ):

        self.count = count
        self.offset = offset
        self.sort = sort

        self.valid_keys_to_filter_by = (
            [
                CveKeys.CveId,
                CveKeys.CvssScore,
                CveKeys.CvssBaseScore,
                CveKeys.CvssExploitSubScore,
                CveKeys.CveCategories,
            ]
        )

        valid_keys_to_sort_by = (
            [
                CveKeys.CveId,
                CveKeys.CvssScore,
                CveKeys.CvssBaseScore,
                CveKeys.CvssExploitSubScore,
                CveKeys.CveModifiedDate,
                CveKeys.CvePublishedDate,
            ]
        )

        if sort_key in valid_keys_to_sort_by:
            self.sort_key = sort_key
        else:
            self.sort_key = CveKeys.CvePublishedDate

        self.fetch_cves = (
            FetchCves(self.count, self.offset, self.sort, self.sort_key)
        )

    @time_it
    def by_id(self, cve_id):
        """Retrieve cve by id.
        Args:
            cve_id (str): The cve_id.
                Example: 'CVE-2014-1817'

        Basic Usage:
            >>> from vFense.plugins.vuln.cve.search.search import RetrieveCVEs
            >>> search_cves = RetrieveCVEs()
            >>> search_cves.by_id('CVE-2014-1817')

        Returns:
            List of dictionairies.
        """
        count, data = self.fetch_cves.by_id(cve_id)
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

    @time_it
    def by_base_score(self, score, logic=None):
        """Retrieve cve data by cve base score.
        Args:
            score (float): Number from 0.0 to 10
                Example: 9.3
            logic (str): valid filters == ( ==, <=, >=, !=, >, < )

        Basic Usage:
            >>> from vFense.plugins.vuln.cve.search.search import RetrieveCVEs
            >>> search_cves = RetrieveCVEs()
            >>> search_cves.by_base_score(5, '>')

        Returns:
            List of dictionairies.
        """
        count, data = (
            self.fetch_cves.by_score(CveKeys.CvssBaseScore, score, logic)
        )
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

    @time_it
    def by_score(self, score, logic=None):
        """Retrieve cve data by cve score.
        Args:
            score (float): Number from 0.0 to 10
                Example: 9.3
            logic (str): valid filters == ( ==, <=, >=, !=, >, < )

        Basic Usage:
            >>> from vFense.plugins.vuln.cve.search.search import RetrieveCVEs
            >>> search_cves = RetrieveCVEs()
            >>> search_cves.by_base_score(5, '>')

        Returns:
            List of dictionairies.
        """
        count, data = (
            self.fetch_cves.by_score(CveKeys.CvssScore, score, logic)
        )
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

    @time_it
    def by_exploit_sub_score(self, score, logic=None):
        """Retrieve cve data by cve score.
        Args:
            score (float): Number from 0.0 to 10
                Example: 9.3
            logic (str): valid filters == ( ==, <=, >=, !=, >, < )

        Basic Usage:
            >>> from vFense.plugins.vuln.cve.search.search import RetrieveCVEs
            >>> search_cves = RetrieveCVEs()
            >>> search_cves.by_base_score(5, '>')

        Returns:
            List of dictionairies.
        """
        count, data = (
            self.fetch_cves.by_score(
                CveKeys.CvssExploitSubScore, score, logic
            )
        )
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
