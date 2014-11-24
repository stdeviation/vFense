from vFense.plugins.reports.api.hardware import HardwareReportsHandler

def api_handlers():
    handlers = [
        ##### Stats API Handlers
        (r"/api/v1/reports/(os|network|memory|cpu|hardware|file_system)?"
         , HardwareReportsHandler)
    ]
    return handlers
