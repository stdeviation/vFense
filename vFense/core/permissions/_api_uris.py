from vFense.core.api.permission import RetrieveValidPermissionsHandler

def api_handlers():
    handlers = [
        (r"/api/v1/permissions?", RetrieveValidPermissionsHandler),
    ]
    return handlers
