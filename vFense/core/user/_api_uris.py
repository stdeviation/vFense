from vFense.core.api.user import UserHandler, UsersHandler

def api_handlers():
    handlers = [
        ##### New User API
        (r"/api/v1/user/([a-zA-Z0-9_ ]+)?", UserHandler),
        (r"/api/v1/users?", UsersHandler),
    ]
    return handlers
