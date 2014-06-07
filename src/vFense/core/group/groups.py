import re
import logging, logging.config
from vFense import VFENSE_LOGGING_CONFIG
from vFense.core._constants import *
from vFense.core.group._db_model import *
from vFense.core.group._constants import *
from vFense.core.user._db_model import UserCollections
from vFense.core.user._constants import *
from vFense.core.view._db_model import *
from vFense.core.view._constants import *
from vFense.core.permissions._constants import *
from vFense.core._db import retrieve_object
from vFense.core.group._db import insert_group, fetch_group, fetch_groups, \
    insert_group_per_user, fetch_group_by_name,  \
    fetch_users_in_group, fetch_groups_for_user, delete_group, \
    fetch_properties_for_all_groups, fetch_group_properties, \
    user_exist_in_group, users_exist_in_group_ids, delete_groups

from vFense.core.decorators import results_message, time_it
from vFense.errorz.status_codes import *
from vFense.errorz._constants import *

logging.config.fileConfig(VFENSE_LOGGING_CONFIG)
logger = logging.getLogger('rvapi')


@time_it
def validate_group_ids(group_ids, view_name=None, is_global=False):
    """Validate a list if group ids exist in the database.
    Args:
        group_ids (list): List of group ids

    Kwargs:
        view_name (str): Name of the view the group belongs too.

    Basic Usage:
        >>> from vFense.group.groups import validate_group_ids
        >>> group_ids = ['4b114647-a6ea-449f-a5a0-d5e1961afb28', '3e27f278-7839-416e-b516-fe4f7cbe98d7']
        >>> validate_group_ids(group_ids)

    Return:
        Tuple (Boolean, [valid_group_ids], [invalid_group_ids])
        (True, ['3ffc2a67-1203-4cb0-ada2-2ae870072680', '0834e656-27a5-4b13-ba56-635797d0d1fc'], [])
    """
    validated = True
    invalid_groups = []
    valid_groups = []
    if isinstance(group_ids, list):
        for group_id in group_ids:
            group = fetch_group(group_id)
            if group:
                if view_name:
                    if view_name in group.get(GroupKeys.Views):
                        if group.get(GroupKeys.Global) == is_global:
                            valid_groups.append(group_id)
                        else:
                            invalid_groups.append(group_id)
                            validated = False
                    else:
                        invalid_groups.append(group_id)
                        validated = False
                else:
                    if group.get(GroupKeys.Global) == is_global:
                        valid_groups.append(group_id)
                    else:
                        invalid_groups.append(group_id)
                        validated = False
            else:
                invalid_groups.append(group_id)
                validated = False
    else:
        validated = False
        invalid_groups = [group_ids]

    return(validated, valid_groups, invalid_groups)


@time_it
def validate_groups_in_views(group_ids, views):
    """Validate a list of group ids against a list of views.
    Args:
        group_ids (list): List of group ids.
        views (list): List of views.

    Basic Usage:
        >>> from vFense.group.groups import validate_groups_in_views
        >>> group_ids = ['tester1', 'tester2']
        >>> views = ['global', 'Test View 1']
        >>> validate_groups_in_views(group_ids, views)

    Returns:
        Tuple
        >>>(
            [invalid_group_ids], [global_group_ids], [local_group_ids]
        )
    """
    invalid_groups = []
    valid_global_groups = []
    valid_local_groups = []
    if isinstance(group_ids, list) and isinstance(views, list):
        for group_id in group_ids:
            group_data = fetch_group(group_id)
            if group_data:
                if group_data[GroupKeys.Global]:
                    valid_global_groups.append(group_id)
                else:
                    if group_data[GroupKey.Views] in views:
                        valid_local_groups.append(group_id)
                    else:
                        invalid_groups.append(group_id)
            else:
                invalid_groups.append(group_id)

    return(invalid_groups, valid_global_groups, valid_local_groups)


@time_it
@results_message
def remove_groups(group_ids, user_name=None, uri=None, method=None):
    """Remove multiple groups in vFense
    Args:
        group_ids (list): List of group ids

    Kwargs:
        user_name (str): The name of the user who called this function.
        uri (str): The uri that was used to call this function.
        method (str): The HTTP methos that was used to call this function.

    Basic Usage::
        >>> from vFense.core.group.groups import remove_groups
        >>> group_ids = ['b4c29dc2-aa44-4ff7-bfc9-f84d38cc7686']
        >>> remove_groups(group_ids)

    Returns:
        Returns the results in a dictionary
        {
            'rv_status_code': 1012,
            'message': 'None - remove_group - b4c29dc2-aa44-4ff7-bfc9-f84d38cc7686 was deleted',
            'http_method': None,
            'uri': None,
            'http_status': 200
        }
    """
    status = remove_groups.func_name + ' - '
    ids_deleted = []
    try:
        users_exist = users_exist_in_group_ids(group_ids)
        groups_exist = validate_group_ids(group_ids)
        if not users_exist and groups_exist[0]:
            status_code, status_count, error, generated_id = (
                delete_groups(group_ids)
            )
            if status_code == DbCodes.Deleted:
                msg = 'group_id %s deleted' % (group_ids)
                generic_status_code = GenericCodes.ObjectDeleted
                vfense_status_code = GroupCodes.GroupDeleted
                ids_deleted = group_ids

        elif users_exist:
            msg = (
                'users exist for groups %s' % (' and'.join(group_ids))
            )
            status_code = DbCodes.Unchanged
            generic_status_code = GenericCodes.ObjectUnchanged
            vfense_status_code = GroupCodes.GroupUnchanged

        elif not group_exist:
            msg = 'group_ids %s does not exist' % (' and '.join(group_ids))
            status_code = DbCodes.Skipped
            generic_status_code = GenericCodes.ObjectUnchanged
            vfense_status_code = GroupCodes.GroupUnchanged

        results = {
            ApiResultKeys.DB_STATUS_CODE: status_code,
            ApiResultKeys.GENERIC_STATUS_CODE: generic_status_code,
            ApiResultKeys.DELETED_IDS: ids_deleted,
            ApiResultKeys.VFENSE_STATUS_CODE: vfense_status_code,
            ApiResultKeys.MESSAGE: status + msg,
            ApiResultKeys.DATA: [],
            ApiResultKeys.USERNAME: user_name,
            ApiResultKeys.URI: uri,
            ApiResultKeys.HTTP_METHOD: method
        }

    except Exception as e:
        logger.exception(e)
        status_code = DbCodes.Errors
        generic_status_code = GenericFailureCodes.FailedToDeleteObject
        vfense_status_code = GroupFailureCodes.FailedToRemoveGroup
        msg = 'failed to remove groups %s: %s' % (group_ids, str(e))

        results = {
            ApiResultKeys.DB_STATUS_CODE: status_code,
            ApiResultKeys.GENERIC_STATUS_CODE: generic_status_code,
            ApiResultKeys.VFENSE_STATUS_CODE: vfense_status_code,
            ApiResultKeys.DELETED_IDS: ids_deleted,
            ApiResultKeys.MESSAGE: status + msg,
            ApiResultKeys.DATA: [],
            ApiResultKeys.USERNAME: user_name,
            ApiResultKeys.URI: uri,
            ApiResultKeys.HTTP_METHOD: method
        }

    return(results)
