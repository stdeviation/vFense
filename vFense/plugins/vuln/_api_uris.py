from vFense.plugins.vuln.api.vulnerability import VulnerabilityHandler
from vFense.plugins.vuln.api.cve import CveIdHandler

def api_handlers():
    handlers = [
        ##### Vulnerability API Handlers
        (r'/api/v1/vulnerability/os/([A-Za-z0-9_-]+)?', VulnerabilityHandler),
        (r'/api/v1/vulnerability/cve/(CVE-[0-9]+-[0-9]+)?', CveIdHandler),
    ]
    return handlers
