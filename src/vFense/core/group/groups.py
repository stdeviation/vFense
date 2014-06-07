import logging, logging.config
from vFense import VFENSE_LOGGING_CONFIG
from vFense.core.group._db_model import GroupKeys
from vFense.core.group._db import fetch_group

from vFense.core.decorators import time_it

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
                    print views, group_data[GroupKeys.Views]
                    if set(group_data[GroupKeys.Views]).issubset(views):
                        valid_local_groups.append(group_id)
                    else:
                        invalid_groups.append(group_id)
            else:
                invalid_groups.append(group_id)

    return(invalid_groups, valid_global_groups, valid_local_groups)
