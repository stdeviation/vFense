import logging
import logging.config
from vFense._constants import VFENSE_LOGGING_CONFIG

from vFense.core.status_codes import GenericCodes
from vFense.core.results import ExternalApiResults

from vFense.core.user import User
from vFense.core.user._db_model import UserCollections
from vFense.core.user._constants import DefaultUsers
from vFense.core.user._db import fetch_user

from vFense.core.permissions._constants import Permissions
from vFense.core.permissions._db import validate_permission_for_user

from vFense.core._db import retrieve_object
from vFense.core.decorators import time_it, catch_it
from vFense.utils.security import Crypto

logging.config.fileConfig(VFENSE_LOGGING_CONFIG)
logger = logging.getLogger('vfense_api')


def return_results_for_permissions(
    username, granted, status_code,
    permission, uri, http_method
    ):
    """Return the vFense supported results for permissions
    Args:
        username (str): The name of the user
        granted (boolean): True or False
        status_code (int): The status_code of the validation
        permission (str): The permission used
        uri (str): The api call
        http_method (str): The http method used to make this call
    Basic Usage:

    Return:
        instance of ExternalApiResults (Check vFense.core.results)
    """
    results = ExternalApiResults()
    results.fill_in_defaults()
    results.username = username
    results.http_method = http_method
    results.uri = uri
    results.generic_status_code = status_code
    results.vfense_status_code = status_code
    if not granted and status_code == GenericCodes.PermissionDenied:
        results.http_status_code = 403
        results.message = (
            'Permission {0} denied for user {1}'
            .format(permission, username)
        )

    elif not granted and status_code == GenericCodes.InvalidPermission:
        results.http_status_code = 404
        results.message = (
            'Invalid permission {0} for user {1}'
            .format(permission, username)
        )

    elif not granted and status_code == GenericCodes.InvalidId:
        results.http_status_code = 404
        results.message = (
            'Invalid username {0}'.format(username)
        )

    return results

@catch_it((False, 0))
def verify_permission_for_user(
    username, permission,
    view_name=None, all_views=False):
    """Verify if a user has permission to this resource.
    Args:
        username (str): The name of the user.
        permission (str): The permission to be verified.

    Kwargs:
        view_name (str): Name of the view that is being verified.

    Basic Usage:
        >>> from vFense.core.permissions.permissions import verify_permission_for_user
        >>> username = 'admin'
        >>> permission = 'install'
        >>> verify_permission_for_user(username, permission)

    Returns:
        Returns a Tuple (Boolean, status_code)

    """
    granted = False
    status_code = GenericCodes.PermissionDenied
    if username == DefaultUsers.GLOBAL_ADMIN:
        granted = True
        status_code = GenericCodes.PermissionGranted
        return(granted, status_code)

    user_exist = fetch_user(username)
    if permission in Permissions().get_valid_permissions() and user_exist:
        if not view_name:
            user = User(**user_exist)
            view_name = user.current_view

        granted = (
            validate_permission_for_user(username, view_name, permission)
        )

        if granted:
            status_code = GenericCodes.PermissionGranted

    elif not permission in Permissions.get_valid_permissions():
        status_code = GenericCodes.InvalidPermission

    elif not user_exist:
        status_code = GenericCodes.InvalidId

    return(granted, status_code)

@time_it
@catch_it(False)
def authenticate_user(username, password):
    authenticated = False
    user_exist = retrieve_object(username, UserCollections.Users)
    if user_exist:
        user = User(**user_exist)
        if user.enabled:
            original_encrypted_password = user.password.encode('utf-8')
            password_verified = (
                Crypto().verify_bcrypt_hash(
                    password, original_encrypted_password
                )
            )
            if password_verified:
                authenticated = True

    return authenticated
