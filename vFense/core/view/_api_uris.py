from vFense.core.api.view import ViewHandler, ViewsHandler

def api_handlers():
    handlers = [
        ##### New View API
        (r'/api/v1/view/((?:\w(?!%20+")|%20(?!%20*")){1,36})?', ViewHandler),
        (r"/api/v1/views?", ViewsHandler),
    ]
    return handlers
