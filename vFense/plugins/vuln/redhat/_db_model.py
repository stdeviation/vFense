from vFense.plugins.vuln._db_model import VulnerabilityKeys

class RedHatVulnerabilityCollections():
    Vulnerabilities = 'redhat_vulnerabilities'


class RedhatVulnerabilityKeys(VulnerabilityKeys):
    Summary = 'summary'
    AppsLink = 'solution_apps'
    OsString = 'os_string'
    Solutions = 'solutions'
    Product = 'product'

class RedhatVulnerabilityIndexes():
    CveIds = 'cve_ids'
