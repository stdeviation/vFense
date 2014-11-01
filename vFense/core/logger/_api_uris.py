from vFense.core.api.log_api import (
    LoggingModifyerHandler, LoggingListerHandler
)

def api_handlers():
    handlers = [
        ##### Logger API Handlers
        (r"/api/logger/modifyLogging?", LoggingModifyerHandler),
        (r"/api/logger/getParams?", LoggingListerHandler),
    ]
    return handlers
