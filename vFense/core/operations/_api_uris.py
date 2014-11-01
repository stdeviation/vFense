from vFense.core.api.agent_operations import (
    GetTransactionsHandler, OperationHandler
)

def api_handlers():
    handlers = [
        ##### Operations API Handlers
        (r"/api/v1/operations?", GetTransactionsHandler),
        (r"/api/v1/operation/([a-f0-9]{8}-[a-f0-9]{4}-4[a-f0-9]{3}-[a-f0-9]{4}-[a-f0-9]{12})?", OperationHandler),
    ]
    return handlers
