import logging
import logging.config
from vFense import VFENSE_LOGGING_CONFIG

from vFense.db.client import db_create_close, r
from vFense.core._constants import SortValues, DefaultQueryValues, SortLogic
from vFense.plugins.vuln.cve._db_model import CveKeys, CVECollections
from vFense.plugins.vuln.cve._constants import *

logging.config.fileConfig(VFENSE_LOGGING_CONFIG)
logger = logging.getLogger('cve')

class FetchCves(object):
    def __init__(
        self, count=DefaultQueryValues.COUNT,
        offset=DefaultQueryValues.OFFSET, sort=SortValues.DESC,
        sort_key=CveKeys.DatePosted
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


    @db_create_close
    def by_score(self, score_name, score, logic=None, conn=None):
        count = 0
        data = []
        base_filter = self._set_base_query()
        map_hash = self._set_map_hash()

        try:
            if not logic:
                count = (
                    base_filter
                    .filter(
                        {
                            score_name: score
                        }
                    )
                    .count()
                    .run(conn)
                )

                data = list(
                    base_filter
                    .filter(
                        {
                            score_name: score
                        }
                    )
                    .order_by(self.sort(self.sort_key))
                    .skip(self.offset)
                    .limit(self.count)
                    .map(map_hash)
                    .run(conn)
                )
            else:
                if logic in SortLogic.VALID_VALUES:
                    logic_filter = (
                        self._set_filter_logic(
                            score_name, score, logic
                        )
                    )
                    count = (
                        base_filter
                        .filter(logic_filter)
                        .count()
                        .run(conn)
                    )

                    data = list(
                        base_filter
                        .filter(logic_filter)
                        .order_by(self.sort(self.sort_key))
                        .skip(self.offset)
                        .limit(self.count)
                        .map(map_hash)
                        .run(conn)
                    )

        except Exception as e:
            logger.exception(e)

        return(count, data)


    def _set_base_query(self):
        base = r.table(CVECollections.CVE)

        return base


    def _set_merge_hash(self):
        merge_hash = (
            lambda x:
            {
                CveKeys.DatePosted: (
                    x[CveKeys.DatePosted].to_epoch_time()
                ),
                CveKeys.DateModified: (
                    x[CveKeys.DateModified].to_epoch_time()
                ),
            }
        )

        return merge_hash

    def _set_map_hash(self):
        map_hash = (
            lambda x:
            {
                CveKeys.DatePosted: (
                    x[CveKeys.DatePosted].to_epoch_time()
                ),
                CveKeys.DateModified: (
                    x[CveKeys.DateModified].to_epoch_time()
                ),
                CveKeys.CveId: x[CveKeys.CveId],
                CveKeys.CvssScore: x[CveKeys.Score],
                CveKeys.CvssBaseScore: x[CveKeys.BaseScore],
                CveKeys.CvssExploitSubScore: x[CveKeys.ExploitSubScore],
            }
        )

        return map_hash


    def _set_filter_logic(self, key, value, logic):
        if logic == SortLogic.EQ:
            base_filter = (
                lambda x:
                x[key] == value
            )

        elif logic == SortLogic.GE:
            base_filter = (
                lambda x:
                x[key] >= value
            )

        elif logic == SortLogic.LE:
            base_filter = (
                lambda x:
                x[key] <= value
            )

        elif logic == SortLogic.GT:
            base_filter = (
                lambda x:
                x[key] > value
            )

        elif logic == SortLogic.LT:
            base_filter = (
                lambda x:
                x[key] < value
            )

        elif logic == SortLogic.NE:
            base_filter = (
                lambda x:
                x[key] != value
            )

        return base_filter
