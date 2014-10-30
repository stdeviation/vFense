from vFense.core.api.tag import TagHandler, TagsHandler
from vFense.plugins.patching.api.os_apps import TagIdAppsHandler
from vFense.core.api.agent_operations import TagOperationsHandler
from vFense.plugins.patching.api.stats_api import (
    TagSeverityHandler, TagOsAppsOverTimeHandler, TagStatsByOsHandler
)

def api_handlers():
    handlers = [
        ##### Tag API Handlers
        (r"/api/v1/tag/([a-f0-9]{8}-[a-f0-9]{4}-4[a-f0-9]{3}-[a-f0-9]{4}-[a-f0-9]{12})?", TagHandler),
        (r"/api/v1/tag/([a-f0-9]{8}-[a-f0-9]{4}-4[a-f0-9]{3}-[a-f0-9]{4}-[a-f0-9]{12})/graphs/bar/severity?",TagSeverityHandler),
        (r"/api/v1/tag/([a-f0-9]{8}-[a-f0-9]{4}-4[a-f0-9]{3}-[a-f0-9]{4}-[a-f0-9]{12})/graphs/column/range/apps/os?", TagOsAppsOverTimeHandler),
        #(r"/api/v1/tag/([a-f0-9]{8}-[a-f0-9]{4}-4[a-f0-9]{3}-[a-f0-9]{4}-[a-f0-9]{12})/graphs/linear/severity?",TagPackageSeverityOverTimeHandler),
        (r"/api/v1/tag/([a-f0-9]{8}-[a-f0-9]{4}-4[a-f0-9]{3}-[a-f0-9]{4}-[a-f0-9]{12})/apps/(os|agentupdates|supported|custom)?", TagIdAppsHandler),
        (r"/api/v1/tag/([a-f0-9]{8}-[a-f0-9]{4}-4[a-f0-9]{3}-[a-f0-9]{4}-[a-f0-9]{12})/operations?", TagOperationsHandler),
        (r"/api/v1/tag/([a-f0-9]{8}-[a-f0-9]{4}-4[a-f0-9]{3}-[a-f0-9]{4}-[a-f0-9]{12})/stats_by_os?", TagStatsByOsHandler),

        ##### Tags API Handlers
        (r"/api/v1/tags", TagsHandler),
    ]
    return handlers
