from vFense.core.api.base import LoginHandler, LogoutHandler, AdminHandler
from vFense.core.api.base import RootHandler, Authentication
from vFense.core.api.agent import (
    FetchSupportedOperatingSystems, FetchValidEnvironments, GenerateUUID
)

def api_handlers():
    handlers = [
        ##### Generic API Handlers
        (r"/?", RootHandler),
        (r"/login/?", LoginHandler),
        (r"/logout/?", LogoutHandler),
        #(r"/ws/?", WebSocketHandler),
        (r"/adminForm", AdminHandler),
        (r"/api/v1/authenticated?", Authentication),
        (r"/api/v1/supported/operating_systems?", FetchSupportedOperatingSystems),
        (r"/api/v1/supported/environments?", FetchValidEnvironments),
        (r"/api/v1/uuid?", GenerateUUID),
        #(r"/api/package/getDependecies?", GetDependenciesHandler),
    ]
    return handlers
