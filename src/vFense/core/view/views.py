import logging
from vFense import VFENSE_LOGGING_CONFIG
from vFense.core.view._db import fetch_view, update_view

from vFense.core.decorators import results_message, time_it
from vFense.result._constants import ApiResultKeys

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
