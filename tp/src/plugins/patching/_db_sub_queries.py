#!/usr/bin/env python

import logging
import logging.config
from vFense.db.client import r
from vFense.plugins.patching import DbCommonAppKeys


logging.config.fileConfig('/opt/TopPatch/conf/logging.config')
logger = logging.getLogger('rvapi')


class AppsMerge():
    RELEASE_DATE = {
        DbCommonAppKeys.ReleaseDate: (
            r.row[DbCommonAppKeys.ReleaseDate].to_epoch_time()
        ),
    }
