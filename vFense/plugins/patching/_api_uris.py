from vFense.plugins.patching.api.os_apps import (
    AppIdAppsHandler, GetAgentsByAppIdHandler, AppsHandler, UploadHandler
)
from vFense.plugins.patching.api.custom_apps import (
    AppIdCustomAppsHandler, GetAgentsByCustomAppIdHandler, CustomAppsHandler
)
from vFense.plugins.patching.api.stats_api import (
    ViewStatsByOsHandler, WidgetHandler, OsAppsOverTimeHandler,
    TopAppsNeededHandler, RecentlyReleasedHandler, ViewSeverityHandler
)

def api_handlers():
    handlers = [
        ##### Apps API Handlers
        (r"/api/v1/app/(os|supported|agentupdates|)/([0-9A-Za-z]{64})?", AppIdAppsHandler),
        (r"/api/v1/app/(os|supported|agentupdates)/([0-9A-Za-z]{64})/agents?", GetAgentsByAppIdHandler),
        (r"/api/v1/apps/(os|supported|agentupdates)", AppsHandler),
        ##### Upload API
        (r"/api/v1/apps/upload?", UploadHandler),

        ##### Dashboard API Handlers
        (r"/api/v1/dashboard/graphs/bar/severity?",ViewSeverityHandler),
        (r"/api/v1/dashboard/graphs/bar/stats_by_os?", ViewStatsByOsHandler),
        (r"/api/v1/dashboard/graphs/column/range/apps/os?", OsAppsOverTimeHandler),
        (r"/api/v1/dashboard/widgets/unique_count?", WidgetHandler),
        (r"/api/v1/dashboard/widgets/top_needed?", TopAppsNeededHandler),
        (r"/api/v1/dashboard/widgets/recently_released?", RecentlyReleasedHandler),

        ##### Custom Apps API Handlers
        (r"/api/v1/app/custom/([a-f0-9]{8}-[a-f0-9]{4}-4[a-f0-9]{3}-[a-f0-9]{4}-[a-f0-9]{12})?", AppIdCustomAppsHandler),
        (r"/api/v1/app/custom/([a-f0-9]{8}-[a-f0-9]{4}-4[a-f0-9]{3}-[a-f0-9]{4}-[a-f0-9]{12})/agents?", GetAgentsByCustomAppIdHandler),
        (r"/api/v1/apps/custom?", CustomAppsHandler),

    ]
    return handlers
