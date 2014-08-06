from vFense.plugins.vuln._db_model import VulnerabilityKeys

class WindowsVulnerabilityCollections():
    Vulnerabiltiies = 'windows_vulnerabilities'


class WindowsVulnerabilityKeys(VulnerabilityKeys):
    KB = 'kb'
    Severity = 'severity'
    Impact = 'impact'

class WindowsVulnerabilityIndexes():
    ComponentKb = 'component_kb'
    CveIds = 'cve_ids'
