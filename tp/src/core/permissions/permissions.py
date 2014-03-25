import logging
import logging.config

from vFense.errorz.status_codes import GenericCodes
from vFense.errorz.error_messages import GenericResults

from vFense.core.user import *
from vFense.core.user.users import get_user

from vFense.core.permissions import *
from vFense.core.permissions._constants import *
from vFense.core.permissions._db import validate_permission_for_user

logging.config.fileConfig('/opt/TopPatch/conf/logging.config')
logger = logging.getLogger('rvapi')


def return_results_for_permissions(
    username, granted, status_code,
    permission, uri, method
    ):
    """Return the vFense supported results for permissions
    Args:
        username (str): The name of the user
        granted (boolean): True or False
        status_code (int): The status_code of the validation
        permission (str): The permission used
        uri (str): The api call
        method (str): The http method used to make this call
    Basic Usage:

    Return:
        Dictionary of the failed response.
        {
            'rv_status_code': 1019,
            'message': 'Permission denied for user admin',
            'http_method': 'POST',
            'uri': '/foo',
            'http_status': 403
        }

    """
    results = None
    if not granted and status_code == GenericCodes.PermissionDenied:
        results = (
            GenericResults(
                username, uri, method
            ).permission_denied(username)
        )

    elif not granted and status_code == GenericCodes.InvalidPermission:
        results = (
            GenericResults(
                username, uri, method
            ).invalid_permission(username, permission)
        )

    elif not granted and status_code == GenericCodes.InvalidId:
        results = (
            GenericResults(
                username, uri, method
            ).invalid_id(username, 'permissions')
        )

    return(results)


def verify_permission_for_user(username, permission):
    """Verify if a user has permission to this resource.
    Args:
        username (str): The name of the user.
        permission (str): The permission to be verified.

    Basic Usage:
        >>> from vFense.core.permissions.permissions import verify_permission_for_user
        >>> username = 'admin'
        >>> permission = 'install'
        >>> verify_permission_for_user(username, customer_name, permission)

    Returns:
        Returns a Tuple (Boolean, status_code)

    """
    granted = False
    status_code = GenericCodes.PermissionDenied
    try:
        user_exist = get_user(username)
        if permission in Permissions().VALID_PERMISSIONS and user_exist:
            customer_name = user_exist.get(UserKeys.CurrentCustomer)
            granted = (
                validate_permission_for_user(
                    username, customer_name, permission
                )
            )
            if granted:
                status_code = GenericCodes.PermissionGranted

        elif not permission in Permissions.VALID_PERMISSIONS:
            status_code = GenericCodes.InvalidPermission

        elif not user_exist:
            status_code = GenericCodes.InvalidId

    except Exception as e:
        logger.exception(e)

    return(granted, status_code)
