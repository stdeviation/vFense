#!/usr/bin/env python

import logging
import logging.config
from vFense import VFENSE_LOGGING_CONFIG
from vFense.errorz._constants import ApiResultKeys
from vFense.core._constants import SortValues, DefaultQueryValues

from vFense.core.user._db_model import (
    UserCollections, UserKeys, UserMappedKeys, UserIndexes
)

from vFense.core.group._db_model import (
    GroupCollections, GroupKeys, GroupIndexes
)

from vFense.core.view._db_model import (
    ViewCollections, ViewKeys, ViewIndexes, ViewMappedKeys
)

from vFense.core.user.search._db import FetchUsers
from vFense.errorz.status_codes import (
    GenericCodes, GenericFailureCodes
)

from vFense.core.permissions._constants import (
    Permissions
)
from vFense.core.decorators import time_it

logging.config.fileConfig(VFENSE_LOGGING_CONFIG)
logger = logging.getLogger('rvapi')

class RetrieveUsers(object):
    def __init__(
        self, view_name=None, count=DefaultQueryValues.COUNT,
        offset=DefaultQueryValues.OFFSET, sort=SortValues.ASC,
        sort_key=UserKeys.UserName, is_global=False
        ):

        self.view_name = view_name
        self.count = count
        self.offset = offset
        self.sort = sort
        self.is_global = is_global

        self.valid_keys_to_filter_by = (
            [
                UserKeys.UserName,
                UserKeys.FullName,
                UserKeys.Email,
            ]
        )

        valid_keys_to_sort_by = (
            [
                UserKeys.UserName,
                UserKeys.FullName,
                UserKeys.Email,
            ]
        )
        if sort_key in valid_keys_to_sort_by:
            self.sort_key = sort_key
        else:
            self.sort_key = UserKeys.UserName

        self.fetch_users = (
            FetchUsers(
                view_name, self.count, self.offset,
                self.sort, self.sort_key, is_global=is_global
            )
        )


    @time_it
    def by_name(self, name):
        """Query users by username.
        Args:
            name (str): The regex you are searching by

        Basic Usage:
            >>> from vFense.core.user.search.search import RetrieveUsers
            >>> search_users = RetrieveUsers(view_name='global')
            >>> search_users.by_name('global')

        Returns:
            List of dictionairies.
        """
        count, data = self.fetch_users.by_name(name)
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
        """Retrieve all agents.
        Basic Usage:
            >>> from vFense.core.user.search.search import RetrieveUsers
            >>> search_users = (
                    RetrieveUsers(
                        view_name='global', is_global=True
                    )
                )
            >>> search_users.all()

        Returns:
        """
        count, data = self.fetch_users.all()
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
