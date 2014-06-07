import logging
from vFense import VFENSE_LOGGING_CONFIG
from vFense.core.user._db_model import UserKeys

from vFense.core.user._db import fetch_user

from vFense.core.decorators import time_it

logging.config.fileConfig(VFENSE_LOGGING_CONFIG)
logger = logging.getLogger('rvapi')


@time_it
def user_is_global(username):
    """Return True if user is global
    Args:
        username (str): Name of the user.

    Basic Usage:
        >>> from vFense.user._db import user_is_global
        >>> username = 'admin'
        >>> user_is_global(username)

    Returns:
        Boolean
    """
    data = fetch_user(username)
    if data:
        if data[UserKeys.Global]:
            data = True
        else:
            data = False

    return data

@time_it
def validate_user_names(user_names, is_global=False):
    """Validate a list of user names exist in the database.
    Args:
        user_names (list): List of user names

    Basic Usage:
        >>> from vFense.group.groups import validate_user_names
        >>> user_names = ['tester1', 'tester2']
        >>> validate_user_names(user_names)

    Return:
        Tuple (Boolean, [valid_user_names], [invalid_user_names])
        (True, ['tester1', 'tester2'], [])
    """
    validated = False
    invalid_user_names = []
    valid_user_names = []
    if isinstance(user_names, list):
        for user_name in user_names:
            user = fetch_user(user_name)
            if user:
                if user[UserKeys.Global] == is_global:
                    valid_user_names.append(user_name)
                    validated = True
                else:
                    invalid_user_names.append(user_name)
            else:
                invalid_user_names.append(user_name)
                validated = False

    return(validated, valid_user_names, invalid_user_names)

@time_it
def validate_users_in_views(usernames, views):
    """Validate a list of user names exist in the database.
    Args:
        usernames (list): List of user names.
        views (list): List of views.

    Basic Usage:
        >>> from vFense.group.groups import validate_users_in_views
        >>> user_names = ['tester1', 'tester2']
        >>> views = ['global', 'Test View 1']
        >>> validate_users_in_views(user_names, views)

    Returns:
        Tuple
        >>>(
            [invalid_usernames], [global_usernames], [local_usernames]
        )
    """
    invalid_users = []
    valid_global_users = []
    valid_local_users = []
    if isinstance(usernames, list) and isinstance(views, list):
        for user in usernames:
            user_data = fetch_user(user)
            if user_data:
                if user_data[UserKeys.Global]:
                    valid_global_users.append(user)
                else:
                    if set(views).issubset(user_data[UserKeys.Views]):
                        valid_local_users.append(user)
                    else:
                        invalid_users.append(user)
            else:
                invalid_users.append(user)

    return(invalid_users, valid_global_users, valid_local_users)
