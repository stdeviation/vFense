from vFense.core.operation._constants import operation_id
from vFense.core.api.agent_operations import (
    GetTransactionsHandler, OperationHandler
)

def api_handlers():
    handlers = [
        ##### Operations API Handlers
        (r"/api/v1/operations?", GetTransactionsHandler),
        (r"/api/v1/operation/{0})?".format(operation_id()),
            OperationHandler),
    ]
    return handlers
