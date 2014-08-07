from vFense.plugins.vuln._db_model import VulnerabilityKeys

class UbuntuVulnerabilityCollections():
    Vulnerabilities = 'ubuntu_vulnerabilities'


class UbuntuVulnerabilityKeys(VulnerabilityKeys):
    pass

class UbuntuVulnerabilityIndexes():
    NameAndVersion = 'name_and_version'
    CveIds = 'cve_ids'
