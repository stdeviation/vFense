from vFense.plugins.vuln import Vulnerability
from vFense.plugins.vuln.redhat._constants import RedhatVulnSubKeys

class Redhat(Vulnerability):
    """Used to represent an instance of a vulnerability."""
    pass


class RedhatVulnApp(object):
    """Used to represent an instance of an app."""

    def __init__(self, name=None, version=None, arch=None, app_id=None):
        """
        Kwargs:
        """
        self.name = name
        self.version = version
        self.arch = arch
        self.app_id = app_id


    def fill_in_defaults(self):
        """Replace all the fields that have None as their value with
        the hardcoded default values.

        Use case(s):
            Useful when you want to create an install instance and only
            want to fill in a few fields, then allow the install
            functions to call this method to fill in the rest.
        """
        pass

    def to_dict(self):
        """ Turn the view fields into a dictionary.

        Returns:
            (dict): A dictionary with the fields corresponding to the
                install operation.

        """
        return {
            RedhatVulnSubKeys.NAME: self.name,
            RedhatVulnSubKeys.VERSION: self.version,
            RedhatVulnSubKeys.ARCH: self.arch,
            RedhatVulnSubKeys.APP_ID: self.app_id,
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
