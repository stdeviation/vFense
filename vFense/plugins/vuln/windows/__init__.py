from vFense.plugins.vuln import Vulnerability
from vFense.plugins.vuln._constants import VulnDefaults
from vFense.plugins.vuln.windows._db_model import WindowsVulnerabilityKeys
from vFense.plugins.vuln.windows._constants import WindowsVulnSubKeys


class Windows(Vulnerability):
    """Used to represent an instance of an app."""

    def __init__(self, kb=None, impact=None, severity=None, **kwargs):
        """
        Kwargs:
        """
        super(Windows, self).__init__(**kwargs)
        self.kb = kb
        self.impact = impact
        self.severity = severity


    def to_dict(self):
        """ Turn the view fields into a dictionary.

        Returns:
            (dict): A dictionary with the fields corresponding to the
                install operation.

        """
        vuln_data = super(Windows, self).to_dict()
        data = {
            WindowsVulnerabilityKeys.KB: self.kb,
            WindowsVulnerabilityKeys.Impact: self.impact,
            WindowsVulnerabilityKeys.Severity: self.severity,
        }

        return dict(vuln_data.items() + data.items())


    def to_dict_db(self):
        """ Turn the view fields into a dictionary.

        Returns:
            (dict): A dictionary with the fields corresponding to the
                install operation.

        """
        vuln_data = super(Windows, self).to_dict_db()

        return dict(vuln_data.items() + self.to_dict().items())


class WindowsVulnApp(object):
    """Used to represent an instance of an app."""

    def __init__(self, kb=None, component=None, impact=None, product=None,
                 cve_ids=None, supercedes=None, reboot=None):
        """
        Kwargs:
        """
        self.kb = kb
        self.component = component
        self.impact = impact
        self.product = component
        self.cve_ids = cve_ids
        self.supercedes = supercedes
        self.reboot = reboot


    def fill_in_defaults(self):
        """Replace all the fields that have None as their value with
        the hardcoded default values.

        Use case(s):
            Useful when you want to create an install instance and only
            want to fill in a few fields, then allow the install
            functions to call this method to fill in the rest.
        """
        if not self.supercedes:
            self.supercedes = VulnDefaults.supercedes()

        if not self.cve_ids:
            self.cve_ids = VulnDefaults.cve_ids()


    def to_dict(self):
        """ Turn the view fields into a dictionary.

        Returns:
            (dict): A dictionary with the fields corresponding to the
                install operation.

        """
        return {
            WindowsVulnSubKeys.KB: self.kb,
            WindowsVulnSubKeys.IMPACT: self.impact,
            WindowsVulnSubKeys.COMPONENT: self.component,
            WindowsVulnSubKeys.PRODUCT: self.product,
            WindowsVulnSubKeys.CVE_IDS: self.cve_ids,
            WindowsVulnSubKeys.SUPERCEDES: self.supercedes,
            WindowsVulnSubKeys.REBOOT: self.reboot,
        }


    def to_dict_non_null(self):
        """ Use to get non None fields of an install. Useful when
        filling out just a few fields to perform an install.

        Returns:
            (dict): a dictionary with the non None fields of this install.
        """
        install_dict = self.to_dict()

        return {k:install_dict[k] for k in install_dict
                if install_dict[k] != None}
