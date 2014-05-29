#!/usr/bin/env python

import logging
import logging.config
from vFense import VFENSE_LOGGING_CONFIG
from vFense.db.client import db_create_close, r
from vFense.core._constants import SortValues, DefaultQueryValues
from vFense.plugins.patching._db_model import *
from vFense.plugins.patching._constants import CommonAppKeys, CommonSeverityKeys

logging.config.fileConfig(VFENSE_LOGGING_CONFIG)
logger = logging.getLogger('rvapi')

class FetchApps(object):
    """
        This class is used to get agent data from within the Packages Page
    """
    def __init__(self, customer_name=None,
                 count=30, offset=0, sort='asc',
                 sort_key=AppsKey.Name,
                 show_hidden=CommonKeys.NO):
        """
        """

    def _set_global_properties(
            self, count, offset,
            show_hidden, sort_key, sort,
            customer_name
            ):
        self.count = count
        self.offset = offset
        self.customer_name = customer_name

        if show_hidden in CommonAppKeys.ValidHiddenVals:
            self.show_hidden = show_hidden
        else:
            self.show_hidden = CommonKeys.NO

        if sort_key in self.pluck_list:
            self.sort_key = sort_key
        else:
            self.sort_key = self.CurrentAppsKey.Name

        if sort == 'asc':
            self.sort = r.asc
        else:
            self.sort = r.desc

    def set_db_properties(self, apps_collection, apps_per_agent_collection):
        """ Set the global properties. """

        self.CurrentAppsCollection = apps_collection
        self.CurrentAppsPerAgentCollection = apps_per_agent_collection

        self.joined_map_hash = (
            {
                self.CurrentAppsKey.AppId:
                    r.row['right'][self.CurrentAppsKey.AppId],
                self.CurrentAppsKey.Version:
                    r.row['right'][self.CurrentAppsKey.Version],
                self.CurrentAppsKey.Name:
                    r.row['right'][self.CurrentAppsKey.Name],
                self.CurrentAppsKey.ReleaseDate:
                    r.row['right'][self.CurrentAppsKey.ReleaseDate].to_epoch_time(),
                self.CurrentAppsKey.RvSeverity:
                    r.row['right'][self.CurrentAppsKey.RvSeverity],
                self.CurrentAppsKey.VulnerabilityId:
                    r.row['right'][self.CurrentAppsKey.VulnerabilityId],
                self.CurrentAppsKey.Hidden:
                    r.row['right'][self.CurrentAppsKey.Hidden],
            }
        )

        self.map_hash = (
            {
                self.CurrentAppsKey.AppId: r.row[self.CurrentAppsKey.AppId],
                self.CurrentAppsKey.Version: r.row[self.CurrentAppsKey.Version],
                self.CurrentAppsKey.Name: r.row[self.CurrentAppsKey.Name],
                self.CurrentAppsKey.ReleaseDate: r.row[self.CurrentAppsKey.ReleaseDate].to_epoch_time(),
                self.CurrentAppsKey.RvSeverity: r.row[self.CurrentAppsKey.RvSeverity],
                self.CurrentAppsKey.VulnerabilityId: r.row[self.CurrentAppsKey.VulnerabilityId],
            }
        )
        self.pluck_list = (
            [
                self.CurrentAppsKey.AppId,
                self.CurrentAppsKey.Version,
                self.CurrentAppsKey.Name,
                self.CurrentAppsKey.ReleaseDate,
                self.CurrentAppsKey.RvSeverity,
                self.CurrentAppsKey.VulnerabilityId,
            ]
        )
