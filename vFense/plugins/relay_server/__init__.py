from time import time
from vFense import Base
from vFense.core._constants import CommonKeys
from vFense.core.results import ApiResultKeys
from vFense.core.status_codes import GenericCodes
from vFense.plugins.relay_server._db_model import RelayServerKeys
from vFense.plugins.relay_server._constants import RelayServerDefaults

class RelayServer(Base):
    """Used to represent an instance of an agent."""

    def __init__(self, relay_name=None, address=None, views=None, **kwargs):
        """
        Kwargs:
            relay_name (str): The name of the relay server.
            views (list): List of view names, this relay server belongs too.
            address (str): The ip_address or dns nmae of the mightymouse.
        """
        super(RelayServer, self).__init__(**kwargs)
        self.relay_name = relay_name
        self.views = views
        self.address = address

    def fill_in_defaults(self):
        """Replace all the fields that have None as their value with
        the hardcoded default values.
        """
        if not self.views:
            self.views = RelayServerDefaults.views()

    def get_invalid_fields(self):
        """Check for any invalid fields.
        Returns:
            (list): List of invalid fields
        """
        invalid_fields = []

        if self.views:
            if not isinstance(self.views, list):
                invalid_fields.append(
                    {
                        RelayServerKeys.Views: self.views,
                        CommonKeys.REASON: 'Must be a list value',
                        ApiResultKeys.VFENSE_STATUS_CODE: (
                            GenericCodes.InvalidValue
                        )
                    }
                )

