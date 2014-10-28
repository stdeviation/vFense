import logging
from vFense._constants import VFENSE_LOGGING_CONFIG
from vFense.core.decorators import time_it
from vFense.core.tag import Tag
from vFense.core.tag._db import fetch_tag

logging.config.fileConfig(VFENSE_LOGGING_CONFIG)
logger = logging.getLogger('rvapi')

@time_it
def validate_tag_ids(tag_ids):
    """Validate a list of tag ids.
    Args:
        tag_ids (list): List of tag_ids.

    Basic Usage:
        >>> from vFense.tag.tags import validate_tag_ids
        >>> tag_ids = ['tag1', 'tag2']
        >>> validate_tag_ids(tag_ids)

    Return:
        Tuple - (Boolean, [valid list], [invalid list])
        (False, ['tag1'], ['tag2'])
    """
    validated = True
    invalid_ids = []
    valid_ids = []
    if isinstance(tag_ids, list):
        for tag_id in tag_ids:
            if fetch_tag(tag_id):
                valid_ids.append(tag_id)
            else:
                invalid_ids.append(tag_id)
                validated = False

    return(validated, valid_ids, invalid_ids)

@time_it
def validate_tag_ids_in_views(tag_ids, views):
    """Validate a list of tag ids.
    Args:
        tag_ids (list): List of tag_ids.
        views (list): List of view names.

    Basic Usage:
        >>> from vFense.tag.tags import validate_tag_ids_in_views
        >>> tag_ids = ['tag1', 'tag2']
        >>> views = ['global', 'test1']
        >>> validate_tag_ids_in_views(tag_ids, views)

    Return:
        Tuple - (Boolean, [valid list], [invalid list])
        (False, ['tag1'], ['tag2'])
    """
    validated = False
    invalid_ids = []
    valid_ids = []
    if isinstance(tag_ids, list) and isinstance(views, list):
        for tag_id in tag_ids:
            tag = fetch_tag(tag_id)
            if tag:
                tag = Tag(**tag)
                if tag.view_name in views:
                    valid_ids.append(tag_id)
                elif tag.is_global:
                    valid_ids.append(tag_id)
                else:
                    invalid_ids.append(tag_id)

    if valid_ids and not invalid_ids:
        validated = True

    return(validated, valid_ids, invalid_ids)
