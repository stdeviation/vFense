#!/usr/bin/env python

from vFense.plugins.patching._db_model import DbCommonAppKeys


class AppsMerge():
    @staticmethod
    def release_date():
        release_date = (
            lambda x:
            {
                DbCommonAppKeys.ReleaseDate: (
                    x[DbCommonAppKeys.ReleaseDate].to_epoch_time()
                ),
            }
        )
        return release_date
