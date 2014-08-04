from vFense.plugins.vuln._db_model import VulnerabilityKeys

class WindowsSecurityCollection():
    Bulletin = 'windows_security_bulletin'


class WindowsSecurityBulletinKey(VulnerabilityKeys):
    Kb = 'kb'
    BulletinSeverity = 'bulletin_severity'
    BulletinImpact = 'bulletin_impact'
    AffectedProduct = 'affected_product'
    ComponentKb = 'component_kb'
    AffectedComponent = 'affected_component'
    ComponentImpact = 'component_impact'
    ComponentSeverity = 'component_severity'
    SupersedesBulletinId = 'supercedes_bulletin_id'
    SupersedesBulletinKb = 'supercedes_bulletin_kb'
    Supersedes = 'supercedes'
    Reboot = 'reboot'

class WindowsSecurityBulletinIndexes():
    BulletinId = 'bulletin_id'
    ComponentKb = 'component_kb'
    CveIds = 'cve_ids'
