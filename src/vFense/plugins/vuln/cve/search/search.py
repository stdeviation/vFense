import logging
import logging.config
from vFense import VFENSE_LOGGING_CONFIG

from vFense.errorz.error_messages import GenericResults, PackageResults
from vFense.errorz._constants import ApiResultKeys
from vFense.core._constants import SortValues, DefaultQueryValues
from vFense.plugins.vuln.cve._db_model import CveKeys
from vFense.plugins.vuln.cve._constants import *
from vFense.plugins.vuln.cve.cve import get_cve_data
from vFense.plugins.vuln.cve.search._db import FetchCves

logging.config.fileConfig(VFENSE_LOGGING_CONFIG)
logger = logging.getLogger('cve')

class RetrieveCves(object):
    def __init__(
        self, count=DefaultQueryValues.COUNT,
        offset=DefaultQueryValues.OFFSET, sort=SortValues.ASC,
        sort_key=CveKeys.CveId
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
            self.sort_key = UserKeys.UserName

        self.fetch_cves = (
            FetchCves(self.count, self.offset, self.sort, self.sort_key)
        )
