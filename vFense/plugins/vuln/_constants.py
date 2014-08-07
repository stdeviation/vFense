from datetime import date

class DateValues():
    CURRENT_YEAR = date.today().year


class VulnCommonKeys():
    VULN = 'Vulnerabilities'


class VulnDefaults():
    CVE_IDS = []
    OS_STRINGS = []
    APPS = list()
    DETAILS = ''
    SUPPORT_URL = ''
    SUPERCEDES = []
