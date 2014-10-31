from vFense.core.views._db import (
    token_exist_in_current, token_exist_in_previous
)


def validate_token(token):
    """Validate the token that was passed
    Args:
        token (str): 36 character uuid

    Basic Usage:
        >>> from vFense.core.receiver.tokens import validate_token
        >>> validated = validate_token("")

    Returns:
        Boolean
    """
    token_validated = False

    valid_current_token = token_exist_in_current(token)
    valid_previous_token = token_exist_in_previous(token)
    if valid_current_token or valid_previous_token:
        token_validated = True

    return token_validated

