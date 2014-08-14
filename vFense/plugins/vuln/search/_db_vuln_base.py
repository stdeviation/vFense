import logging
import logging.config
from vFense import VFENSE_LOGGING_CONFIG

from vFense.db.client import db_create_close, r
from vFense.core._constants import SortValues, DefaultQueryValues
from vFense.plugins.vuln._db_model import (
    VulnerabilityIndexes, VulnerabilityKeys
)

logging.config.fileConfig(VFENSE_LOGGING_CONFIG)
logger = logging.getLogger('cve')

class FetchVulns(object):
    def __init__(
        self, collection, count=DefaultQueryValues.COUNT,
        offset=DefaultQueryValues.OFFSET, sort=SortValues.DESC,
        sort_key=VulnerabilityKeys.DatePosted
        ):
        self.collection = collection
        self.count = count
        self.offset = offset
        self.sort = sort
        self.sort_key = sort_key

        if sort == SortValues.ASC:
            self.sort = r.asc
        else:
            self.sort = r.desc


    @db_create_close
    def by_id(self, bulletin_id, conn=None):
        count = 0
        data = []
        base_filter = self._set_base_query()
        merge_hash = self._set_merge_hash()

        try:
            count = (
                base_filter
                .get_all(bulletin_id)
                .count()
                .run(conn)
            )

            data = list(
                base_filter
                .get_all(bulletin_id)
                .order_by(self.sort(self.sort_key))
                .skip(self.offset)
                .limit(self.count)
                .merge(merge_hash)
                .run(conn)
            )

        except Exception as e:
            logger.exception(e)

        return(count, data)

    @db_create_close
    def by_app_name_and_version(self, name, version, conn=None):
        count = 0
        data = []
        base_filter = self._set_base_query()
        merge_hash = self._set_merge_hash()

        try:
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

        except Exception as e:
            logger.exception(e)

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
