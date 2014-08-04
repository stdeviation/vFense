from vFense.plugins.vuln._db_model import VulnerabilityKeys

class UbuntuSecurityCollection():
    Bulletin = 'ubuntu_security_bulletin'


class UbuntuSecurityBulletinKey(VulnerabilityKeys):
    pass

class UbuntuSecurityBulletinIndexes():
    VulnerabilityId = 'vulnerability_id'
    NameAndVersion = 'name_and_version'
    CveIds = 'cve_ids'
