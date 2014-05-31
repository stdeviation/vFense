from vFense.core.view._db_model import View
from vFense.core.view._db import (
    fetch_view
)
from vFense.core.decorators import time_it

class ViewManager(object):
    def __init__(self, name):
        self.name = name
        self.properties = self._view_properties()

    def _view_properties(self):
        """Retrieve view information.
        Basic Usage:
            >>> from vFense.view.manager import ViewManager
            >>> view_name = 'default'
            >>> view = ViewManager(view_name)
            >>> view._view_properties()

        Returns:
            Dictionary of view properties.
            {
                u'cpu_throttle': u'normal',
                u'package_download_url_base': u'http: //10.0.0.21/packages/',
                u'operation_ttl': 10,
                u'net_throttle': 0,
                u'view_name': u'default'
            }
        """
        view_data = fetch_view(self.name)

        return view_data

    @time_it
    def create_view(view, username=None, init=None):
        """Create a new view inside of vFense

        Args:
            view (View): A view instance filled out with the
                appropriate fields.

        Kwargs:
            username (str): Name of the user that you are adding to this view.
                Default=None
                If init is set to True, then it can stay as None
                else, then a valid user must be passed
            init (boolean): Create the view, without adding a user into it.
                Default=False

        Basic Usage:
            >>> from vFense.core.view._db_model import View
            >>> from vFense.core.view.views import create_view
            >>> view = View('NewView', package_download_url='https://10.0.0.16/packages/')
            >>> username = 'api_user'
            >>> create_view(view, api_user)

        Returns:
            Dictionary of the status of the operation.
            {
                'uri': None,
                'rv_status_code': 1010,
                'http_method': None,
                'http_status': 200,
                'message': 'api_user - view vFense was created',
                'data': {
                    'cpu_throttle': 'normal',
                    'package_download_url_base': 'https: //10.0.0.21/packages/',
                    'server_queue_ttl': 10,
                    'agent_queue_ttl': 10,
                    'net_throttle': 0,
                    'view_name': 'vFense'
                }
            }
        """
