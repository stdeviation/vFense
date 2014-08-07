from datetime import date

class DateValues():
    CURRENT_YEAR = date.today().year


class VulnCommonKeys():
    VULN = 'Vulnerabilities'


class VulnDefaults():
    @staticmethod
    def cve_ids():
        return list()

    @staticmethod
    def os_strings():
        return list()

    @staticmethod
    def apps():
        return list()

    @staticmethod
    def details():
        return ''

    @staticmethod
    def support_url():
        return ''

    @staticmethod
    def supercedes():
        return list()
