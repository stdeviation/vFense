from vFense.plugins.patching.api.apps import (
    AppIdAppsHandler, GetAgentsByAppIdHandler, AppsHandler, UploadHandler,
    StoreUploadHandler
)
from vFense.plugins.patching.api.stats import (
    ViewStatsByOsHandler, WidgetHandler, OsAppsOverTimeHandler,
    TopAppsNeededHandler, RecentlyReleasedHandler, ViewSeverityHandler
)
from vFense.plugins.patching.apps._constants import os_appid
from vFense.plugins.patching.apps.custom._constants import custom_appid

def api_handlers():
    handlers = [
        ##### Apps API Handlers
        (
            r"/api/v1/app/(os|supported|agentupdates|custom)/({0}|{1})?"
            .format(os_appid(), custom_appid()),
            AppIdAppsHandler
        ),
        (
            r"/api/v1/app/(os|supported|agentupdates|custom)/({0}|{1})/agents?"
            .format(os_appid(), custom_appid()),
            GetAgentsByAppIdHandler
        ),
        (r"/api/v1/apps/(os|supported|agentupdates|custom)", AppsHandler),
        ##### Upload API
        (r"/api/v1/apps/upload", UploadHandler),
        (r"/api/v1/apps/finalize/upload", StoreUploadHandler),

        ##### Dashboard API Handlers
        (r"/api/v1/dashboard/graphs/bar/severity?",ViewSeverityHandler),
        (r"/api/v1/dashboard/graphs/bar/stats_by_os?", ViewStatsByOsHandler),
        (r"/api/v1/dashboard/graphs/column/range/apps/os?", OsAppsOverTimeHandler),
        (r"/api/v1/dashboard/widgets/unique_count?", WidgetHandler),
        (r"/api/v1/dashboard/widgets/top_needed?", TopAppsNeededHandler),
        (r"/api/v1/dashboard/widgets/recently_released?", RecentlyReleasedHandler)
    ]
    return handlers
