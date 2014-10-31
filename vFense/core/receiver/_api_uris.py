from vFense.core.receiver.api.generics import ValidateToken
from vFense.core.api.base import (
    RootHandler, RvlLoginHandler, RvlLogoutHandler
)

def api_handlers():
    handlers = [
        #Login and Logout Operations
        (r"/rvl/?", RootHandler),
        (r"/rvl/login/?", RvlLoginHandler),
        (r"/rvl/logout/?", RvlLogoutHandler),
        (r"/rvl/validate?", ValidateToken),
    ]
    return handlers
