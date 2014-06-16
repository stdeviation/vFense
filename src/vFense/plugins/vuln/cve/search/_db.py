import logging
import logging.config
from vFense import VFENSE_LOGGING_CONFIG

from vFense.db.client import db_create_close, r
from vFense.errorz.error_messages import GenericResults, PackageResults
from vFense.errorz._constants import ApiResultKeys
from vFense.core._constants import SortValues, DefaultQueryValues
from vFense.plugins.vuln.cve._db_model import CveKeys, CVECollections
from vFense.plugins.vuln.cve._constants import *

logging.config.fileConfig(VFENSE_LOGGING_CONFIG)
logger = logging.getLogger('cve')

class FetchCves(object):
    def __init__(
        self, count=DefaultQueryValues.COUNT,
        offset=DefaultQueryValues.OFFSET, sort=SortValues.ASC,
        sort_key=CveKeys.CveId
        ):

        self.count = count
        self.offset = offset
        self.sort = sort
        self.sort_key = sort_key

        if sort == SortValues.ASC:
            self.sort = r.asc
        else:
            self.sort = r.desc


    @db_create_close
    def by_id(self, cve_id, conn=None):
        count = 0
        data = []
        base_filter = self._set_base_query()
        merge_hash = self._set_merge_hash()

        try:
            count = (
                base_filter
                .get_all(cve_id)
                .count()
                .run(conn)
            )

            data = list(
                base_filter
                .get_all(cve_id)
                .order_by(self.sort(self.sort_key))
                .skip(self.offset)
                .limit(self.count)
                .merge(merge_hash)
                .run(conn)
            )

        except Exception as e:
            logger.exception(e)

        return(count, data)


    def _set_base_query(self):
        base = r.table(CVECollections.CVE)

        return base


    def _set_merge_hash(self):
        map_hash = (
            lambda x:
            {
                CveKeys.CvePublishedDate: (
                    x[CveKeys.CvePublishedDate].to_epoch_time()
                ),
                CveKeys.CveModifiedDate: (
                    x[CveKeys.CveModifiedDate].to_epoch_time()
                ),
            }
        )

        return map_hash
