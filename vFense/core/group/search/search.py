#!/usr/bin/env python

import logging
import logging.config
from vFense._constants import VFENSE_LOGGING_CONFIG
from vFense.core.results import ApiResults
from vFense.core._constants import SortValues, DefaultQueryValues

from vFense.core.group._db_model import GroupKeys


from vFense.core.group.search._db import FetchGroups
from vFense.core.status_codes import (
    GenericCodes, GenericFailureCodes
)

from vFense.core.decorators import time_it

logging.config.fileConfig(VFENSE_LOGGING_CONFIG)
logger = logging.getLogger('rvapi')

class RetrieveGroups(object):
    def __init__(
        self, view_name=None, count=DefaultQueryValues.COUNT,
        offset=DefaultQueryValues.OFFSET, sort=SortValues.ASC,
        sort_key=GroupKeys.GroupName, is_global=False
        ):

        self.view_name = view_name
        self.count = count
        self.offset = offset
        self.sort = sort
        self.is_global = is_global

        self.valid_keys_to_filter_by = (
            [
                GroupKeys.GroupName,
                GroupKeys.Email,
            ]
        )

        valid_keys_to_sort_by = (
            [
                GroupKeys.GroupName,
                GroupKeys.Email,
            ]
        )
        if sort_key in valid_keys_to_sort_by:
            self.sort_key = sort_key
        else:
            self.sort_key = GroupKeys.GroupName

        self.fetch_groups = (
            FetchGroups(
                view_name, self.count, self.offset,
                self.sort, self.sort_key, is_global=is_global
            )
        )


    @time_it
    def by_id(self, group_id):
        """Retrieve group by group id
        Args:
            group_id (str): The 36 character UUID of the group.

        Basic Usage:
            >>> from vFense.core.groups.search.search import RetrieveGroups
            >>> search_groups = RetrieveGroups(view_name='global')
            >>> search_groups.by_name('global')

        Returns:
            List of dictionairies.
        """
        count, data = self.fetch_groups.by_id(group_id)
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
        """Query groups by group name.
        Args:
            name (str): The name of the group you are searching for.

        Basic Usage:
            >>> from vFense.core.groups.search.search import RetrieveGroups
            >>> search_groups = RetrieveGroups(view_name='global')
            >>> search_groups.by_name('global')

        Returns:
            List of dictionairies.
        """
        count, data = self.fetch_groups.by_name(name)
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
    def by_regex(self, name):
        """Query groups by regex on group name.
        Args:
            name (str): The regex you are searching by

        Basic Usage:
            >>> from vFense.core.groups.search.search import RetrieveGroups
            >>> search_groups = RetrieveGroups(view_name='global')
            >>> search_groups.by_name('global')

        Returns:
            List of dictionairies.
        """
        count, data = self.fetch_groups.by_regex(name)
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
        """Retrieve all groups.
        Basic Usage:
            >>> from vFense.core.group.search.search import RetrieveGroups
            >>> search_groups = (
                    RetrieveGroups(
                        view_name='global', is_global=True
                    )
                )
            >>> search_groups.all()

        Returns:
        """
        count, data = self.fetch_groups.all()
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


    def _set_results(self, generic_status_code, vfense_status_code,
                     msg, count, data):
        results = ApiResults()
        results.fill_in_defaults()
        results.generic_status_code = generic_status_code
        results.vfense_status_code = vfense_status_code
        results.message = msg
        results.count = count
        results.data = data

        return results
