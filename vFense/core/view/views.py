from vFense.core.decorators import time_it
from vFense.core.view._db import fetch_view


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
    validated = False
    invalid_names = []
    valid_names = []
    if isinstance(view_names, list):
        for view_name in view_names:
            if fetch_view(view_name):
                valid_names.append(view_name)
                validated = True
            else:
                invalid_names.append(view_name)
                validated = False

    return(validated, valid_names, invalid_names)
