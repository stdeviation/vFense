from vFense.core.api.email_api import (
    CreateEmailConfigHandler, GetEmailConfigHandler
)

def api_handlers():
    handlers = [
        ##### Email API Handlers
        (r"/api/email/config/create?", CreateEmailConfigHandler),
        (r"/api/email/config/list?", GetEmailConfigHandler),
    ]
    return handlers
