from vFense.plugins.ra.api.status import RDStatusQueue
from vFense.plugins.ra.api.rdsession import RDSession
from vFense.plugins.ra.api.settings import SetPassword

def api_handlers():
    handlers = [
        ##### RA Api
        (r"/api/ra/rd/password/?", SetPassword),
        (r"/api/ra/rd/([^/]+)/?", RDSession),
        (r"/ws/ra/status/?", RDStatusQueue),
    ]
    return handlers
