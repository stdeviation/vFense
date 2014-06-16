#!/usr/bin/env python

import logging
import logging.config
from vFense import VFENSE_LOGGING_CONFIG
from vFense.errorz._constants import ApiResultKeys
from vFense.core._constants import SortValues, DefaultQueryValues

from vFense.core.view._db_model import ViewKeys

from vFense.core.view.search._db import FetchViews
from vFense.errorz.status_codes import (
    GenericCodes, GenericFailureCodes
)

from vFense.core.decorators import time_it

logging.config.fileConfig(VFENSE_LOGGING_CONFIG)
logger = logging.getLogger('rvapi')

class RetrieveViews(object):
    def __init__(
        self, parent_view=None, count=DefaultQueryValues.COUNT,
        offset=DefaultQueryValues.OFFSET, sort=SortValues.ASC,
        sort_key=ViewKeys.ViewName, is_global=False
        ):

        self.parent_view = parent_view
        self.count = count
        self.offset = offset
        self.sort = sort
        self.is_global = is_global

        self.valid_keys_to_filter_by = (
            [
                ViewKeys.ViewName,
            ]
        )

        valid_keys_to_sort_by = (
            [
                ViewKeys.ViewName,
            ]
        )
        if sort_key in valid_keys_to_sort_by:
            self.sort_key = sort_key
        else:
            self.sort_key = ViewKeys.ViewName

        self.fetch_views = (
            FetchViews(
                parent_view, self.count, self.offset,
                self.sort, self.sort_key, is_global=is_global
            )
        )


    @time_it
    def by_regex(self, name):
        """Query views by regex.
        Args:
            name (str): The regex you are searching by

        Basic Usage:
            >>> from vFense.core.views.search.search import RetrieveViews
            >>> search_views = RetrieveViews()
            >>> search_views.by_regex('global')

        Returns:
            List of dictionairies.
        """
        count, data = self.fetch_views.by_regex(name)
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
    def by_name(self, name):
        """Get view by name.
        Args:
            name (str): The regex you are searching by

        Basic Usage:
            >>> from vFense.core.views.search.search import RetrieveViews
            >>> search_views = RetrieveViews()
            >>> search_views.by_name('global')

        Returns:
            List of dictionairies.
        """
        count, data = self.fetch_views.by_name(name)
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
    def all(self):
        """Retrieve all views.
        Basic Usage:
            >>> from vFense.core.view.search.search import RetrieveViews
            >>> search_views = RetrieveViews()
            >>> search_views.all()

        Returns:
        """
        count, data = self.fetch_views.all()
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
    def for_user(self, name):
        """Get all views for a user.
        Args:
            name (str): The name of the user of the
                views you are searching for.

        Basic Usage:
            >>> from vFense.core.views.search.search import RetrieveViews
            >>> search_views = RetrieveViews(is_global=True)
            >>> search_views.for_user('global_admin')

        Returns:
            List of dictionairies.
        """
        count, data = self.fetch_views.for_user(name)
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
