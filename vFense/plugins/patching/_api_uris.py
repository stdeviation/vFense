from vFense.plugins.patching.api.os_apps import (
    AppIdAppsHandler, GetAgentsByAppIdHandler, AppsHandler, UploadHandler
)

def api_handlers():
    handlers = [
        ##### Apps API Handlers
        (r"/api/v1/app/(os|supported|agentupdates|)/([0-9A-Za-z]{64})?", AppIdAppsHandler),
        (r"/api/v1/app/(os|supported|agentupdates)/([0-9A-Za-z]{64})/agents?", GetAgentsByAppIdHandler),
        (r"/api/v1/apps/(os|supported|agentupdates)", AppsHandler),
        (r"/api/v1/apps/upload?", UploadHandler),
    ]
    return handlers
