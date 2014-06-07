import logging
from vFense import VFENSE_LOGGING_CONFIG
from vFense.core.view._db import fetch_view, update_view

from vFense.core.decorators import results_message, time_it
from vFense.errorz._constants import ApiResultKeys

logging.config.fileConfig(VFENSE_LOGGING_CONFIG)
logger = logging.getLogger('rvapi')

@time_it
def validate_view_names(view_names):
    """Validate a list of view names.
    Args:
        view_names (list): List of view names.

    Basic Usage:
        >>> from vFense.view.views import validate_view_names
        >>> view_names = ['default', 'TOpPatch']
        >>> validate_view_names(view_names)

    Return:
        Tuple - (Boolean, [valid list], [invalid list])
        (False, ['default'], ['TOpPatch'])
    """
    validated = True
    invalid_names = []
    valid_names = []
    if isinstance(view_names, list):
        for view_name in view_names:
            if fetch_view(view_name):
                valid_names.append(view_name)
            else:
                invalid_names.append(view_name)
                validated = False

    return(validated, valid_names, invalid_names)


@time_it
@results_message
def edit_view(view, **kwargs):
    """ Edit the properties of a view.

    Args:
        view (View): A view instance filled with values
            that should be changed.

    Kwargs:
        user_name (str): The name of the user who called this function.
        uri (str): The uri that was used to call this function.
        method (str): The HTTP methos that was used to call this function.

    Basic Usage:
        >>> from vFense.core.view.views edit_view
        >>> view_name = 'agent_api'
        >>> edit_view(view_name, server_queue_ttl=5)

    Returns:
        Dictionary of the status of the operation.
        {
            'uri': None,
            'rv_status_code': 1008,
            'http_method': None,
            'http_status': 200,
            'message': 'None - view modified - default was updated',
            'data': {
                'server_queue_ttl': 5
            }
        }
    """

    if not kwargs.get(ApiResultKeys.USERNAME):
        user_name = None
    else:
        user_name = kwargs.pop(ApiResultKeys.USERNAME)

    if not kwargs.get(ApiResultKeys.URI):
        uri = None
    else:
        uri = kwargs.pop(ApiResultKeys.URI)

    if not kwargs.get(ApiResultKeys.HTTP_METHOD):
        method = None
    else:
        method = kwargs.pop(ApiResultKeys.HTTP_METHOD)

    status = edit_view.func_name + ' - '
    update_data = view.to_dict_non_null()

    msg = ''
    generic_status_code = None
    vfense_status_code = None
    try:
        invalid_data = view.get_invalid_fields()

        if invalid_data:
            msg = (
                'data was invalid for view %s: %s- ' %
                (view.name, invalid_data)
            )
            status_code = DbCodes.Unchanged
            generic_status_code = GenericCodes.ObjectUnchanged
            vfense_status_code = ViewCodes.ViewUnchanged

        else:
            status_code, _, _, _ = update_view(
                view.name, update_data
            )

            if status_code == DbCodes.Replaced:
                msg = 'view %s updated - ' % (view.name)
                generic_status_code = GenericCodes.ObjectUpdated
                vfense_status_code = ViewCodes.ViewUpdated

            elif status_code == DbCodes.Unchanged:
                msg = 'view %s unchanged - ' % (view.name)
                generic_status_code = GenericCodes.ObjectUnchanged
                vfense_status_code = ViewCodes.ViewUnchanged

            elif status_code == DbCodes.Skipped:
                msg = 'view %s does not exist - ' % (view.name)
                generic_status_code = GenericCodes.InvalidId
                vfense_status_code = ViewFailureCodes.InvalidViewName

    except Exception as e:
        logger.exception(e)
        msg = 'Failed to modify view %s: %s' % (view.name, str(e))
        status_code = DbCodes.Errors
        generic_status_code = GenericFailureCodes.FailedToUpdateObject
        vfense_status_code = ViewFailureCodes.FailedToRemoveView

    results = {
        ApiResultKeys.DB_STATUS_CODE: status_code,
        ApiResultKeys.GENERIC_STATUS_CODE: generic_status_code,
        ApiResultKeys.VFENSE_STATUS_CODE: vfense_status_code,
        ApiResultKeys.MESSAGE: status + msg,
        ApiResultKeys.DATA: [update_data],
        ApiResultKeys.USERNAME: user_name,
        ApiResultKeys.URI: uri,
        ApiResultKeys.HTTP_METHOD: method
    }

    return results
