from vFense import Base
from vFense.core.results import ApiResultKeys

class MightyMouse(Base):
    """Used to represent an instance of an agent."""

    def __init__(self, relay_name=None, address=None, views=None, **kwargs):
        """
        Kwargs:
            relay_name (str): The name of the relay server.
            views (list): List of view names, this relay server belongs too.
            address (str): The ip_address or dns nmae of the mightymouse.
        """
        super(MightyMouse, self).__init__(**kwargs)
        self.relay_name = relay_name
        self.views = views
        self.address = address
