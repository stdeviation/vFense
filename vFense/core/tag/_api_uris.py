from vFense.core.tag._constants import tag_id
from vFense.core.api.tag import (
    TagHandler, TagsHandler, TagJobsHandler, TagSchedulerReboot
)
from vFense.plugins.patching.api.apps import TagIdAppsHandler
from vFense.core.api.agent_operations import TagOperationsHandler
from vFense.plugins.patching.api.stats import (
    TagSeverityHandler, TagOsAppsOverTimeHandler, TagStatsByOsHandler
)

def api_handlers():
    handlers = [
        ##### Tag API Handlers
        (r"/api/v1/tag/({0})?".format(tag_id()), TagHandler),
        (r"/api/v1/tag/({0})/graphs/bar/severity?".format(tag_id()),
            TagSeverityHandler),
        (r"/api/v1/tag/({0})/graphs/column/range/apps/os?".format(tag_id()),
            TagOsAppsOverTimeHandler),
        #(r"/api/v1/tag/({0})/graphs/linear/severity?",TagPackageSeverityOverTimeHandler),
        (r"/api/v1/tag/({0})/apps/(os|agentupdates|supported|custom)?".format(tag_id()),
            TagIdAppsHandler),
        (r"/api/v1/tag/({0})/operations?".format(tag_id()),
            TagOperationsHandler),
        (r"/api/v1/tag/({0})/stats_by_os?".format(tag_id()),
            TagStatsByOsHandler),
        (r"/api/v1/tag/({0})/schedules?".format(tag_id()),
            TagJobsHandler),
        (r"/api/v1/tag/({0})/schedule/reboot?".format(tag_id()),
            TagSchedulerReboot),

        ##### Tags API Handlers
        (r"/api/v1/tags", TagsHandler),
    ]
    return handlers
