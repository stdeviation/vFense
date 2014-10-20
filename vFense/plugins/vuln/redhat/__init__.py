from vFense import Base
from vFense.plugins.vuln import Vulnerability
from vFense.plugins.vuln.redhat._constants import RedhatVulnSubKeys

class Redhat(Vulnerability):
    """Used to represent an instance of a vulnerability."""
    pass


class RedhatVulnApp(Base):
    """Used to represent an instance of an app."""

    def __init__(self, name=None, version=None, arch=None, app_id=None,
                 **kwargs):
        """
        Kwargs:
            name (str): The name of the application.
            version (str): The version of the application.
            arch (str): The architecture this application was built for.
            app_id (str): The primary key of the application.
        """
        super(RedhatVulnApp, self).__init__(**kwargs)
        self.name = name
        self.version = version
        self.arch = arch
        self.app_id = app_id

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
