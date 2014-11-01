from vFense import Base
from vFense.plugins.vuln import Vulnerability
from vFense.plugins.vuln._constants import VulnDefaults
from vFense.plugins.vuln.ubuntu._constants import UbuntuVulnSubKeys

class Ubuntu(Vulnerability):
    """Used to represent an instance of a vulnerability."""
    pass


class UbuntuVulnApp(Base):
    """Used to represent an instance of an app."""

    def __init__(self, name=None, version=None, os_string=None, app_id=None,
                 **kwargs):
        """
        Kwargs:
            name (str): The name of the application.
            version (str): The version of the application.
            arch (str): The architecture this application was built for.
            app_id (str): The primary key of the application.
        """
        super(UbuntuVulnApp, self).__init__(**kwargs)
        self.name = name
        self.version = version
        self.os_string = os_string
        self.app_id = app_id


    def fill_in_defaults(self):
        """Replace all the fields that have None as their value with
        the hardcoded default values.

        Use case(s):
            Useful when you want to create an install instance and only
            want to fill in a few fields, then allow the install
            functions to call this method to fill in the rest.
        """
        if not self.version:
            self.version = VulnDefaults.version()

        if not self.os_string:
            self.os_string = VulnDefaults.os_string()

    def to_dict(self):
        """ Turn the view fields into a dictionary.

        Returns:
            (dict): A dictionary with the fields corresponding to the
                install operation.

        """
        return {
            UbuntuVulnSubKeys.NAME: self.name,
            UbuntuVulnSubKeys.VERSION: self.version,
            UbuntuVulnSubKeys.OS_STRING: self.os_string,
            UbuntuVulnSubKeys.APP_ID: self.app_id,
        }
