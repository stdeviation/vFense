import logging
from vFense import VFENSE_LOGGING_CONFIG
from vFense.core._constants import *
from vFense.errorz._constants import *
from vFense.core.user._db_model import UserKeys
from vFense.core.user._constants import DefaultUsers
from vFense.core.group._db_model import *
from vFense.core.group._constants import *
from vFense.core.view._db_model import *

from vFense.core.user._db import fetch_user, delete_users


from vFense.core.group.groups import remove_groups_from_user

from vFense.core.view.views import remove_views_from_user

from vFense.core.decorators import results_message, time_it
from vFense.errorz.status_codes import *

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
                    if user_data[UserKey.Views] in views:
                        valid_local_users.append(user)
                    else:
                        invalid_users.append(user)
            else:
                invalid_users.append(user)

    return(invalid_users, valid_global_users, valid_local_users)

@time_it
@results_message
def remove_users(usernames, user_name=None, uri=None, method=None):
    """Remove a user from vFense
    Args:
        usernames (list): List of usernames that will be deleted.

    Kwargs:
        user_name (str): The name of the user who called this function.
        uri (str): The uri that was used to call this function.
        method (str): The HTTP methos that was used to call this function.

    Return:
        Dictionary of the status of the operation.
    """

    status = change_password.func_name + ' - '
    usernames_not_to_delete = []
    usernames_to_delete = []
    generic_status_code = 0
    vfense_status_code = 0
    msg = ''
    try:
        if not isinstance(usernames, list):
            usernames = usernames.split(',')
        for username in usernames:
            user_exist = get_user(username)
            status = remove_users.func_name + ' - '
            if user_exist and username != DefaultUsers.ADMIN:
                remove_groups_from_user(username)
                remove_views_from_user(username)
                usernames_to_delete.append(username)

            elif username == DefaultUsers.ADMIN:
                msg = 'Can not delete the %s user' % (username)
                usernames_not_to_delete.append(username)
                generic_status_code = GenericCodes.CouldNotBeDeleted
                vfense_status_code = UserFailureCodes.AdminUserCanNotBeDeleted
                object_status = DbCodes.Skipped

            else:
                msg = 'User does not exist %s' % (username)
                usernames_not_to_delete.append(username)
                generic_status_code = GenericCodes.InvalidId
                vfense_status_code = UserFailureCodes.UserNameDoesNotExist
                object_status = DbCodes.Skipped

        if len(usernames_to_delete) > 0:
            object_status, _, _, _ = (
                delete_users(usernames_to_delete)
            )

            if object_status == DbCodes.Deleted:
                generic_status_code = GenericCodes.ObjectDeleted
                vfense_status_code = UserCodes.UserDeleted
                msg = 'Users removed %s' % (' and '.join(usernames_to_delete))

            if object_status == DbCodes.DoesNotExist:
                generic_status_code = GenericCodes.DoesNotExist
                vfense_status_code = UserFailureCodes.UserNameDoesNotExist
                msg = 'Users  %s do not exist' % (' and '.join(usernames_to_delete))

        else:
            object_status = DbCodes.Unchanged
            generic_status_code = GenericFailureCodes.FailedToDeleteObject
            vfense_status_code = UserFailureCodes.FailedToRemoveUser
            msg = 'Users can not be removed %s' % (
                ' and '.join(usernames_not_to_delete))

        results = {
            ApiResultKeys.DB_STATUS_CODE: object_status,
            ApiResultKeys.GENERIC_STATUS_CODE: generic_status_code,
            ApiResultKeys.VFENSE_STATUS_CODE: vfense_status_code,
            ApiResultKeys.MESSAGE: status + msg,
            ApiResultKeys.UNCHANGED_IDS: usernames_not_to_delete,
            ApiResultKeys.DELETED_IDS: usernames_to_delete,
            ApiResultKeys.DATA: [],
            ApiResultKeys.USERNAME: user_name,
            ApiResultKeys.URI: uri,
            ApiResultKeys.HTTP_METHOD: method
        }


    except Exception as e:
        logger.exception(e)
        msg = 'Failed to remove user %s: %s' % (username, str(e))
        generic_status_code = GenericFailureCodes.FailedToDeleteObject
        vfense_status_code = UserFailureCodes.FailedToRemoveUser

        results = {
            ApiResultKeys.DB_STATUS_CODE: DbCodes.Errors,
            ApiResultKeys.GENERIC_STATUS_CODE: generic_status_code,
            ApiResultKeys.VFENSE_STATUS_CODE: vfense_status_code,
            ApiResultKeys.MESSAGE: status + msg,
            ApiResultKeys.UNCHANGED_IDS: usernames_not_to_delete,
            ApiResultKeys.DELETED_IDS: usernames_to_delete,
            ApiResultKeys.DATA: [],
            ApiResultKeys.USERNAME: user_name,
            ApiResultKeys.URI: uri,
            ApiResultKeys.HTTP_METHOD: method
        }

    return results
