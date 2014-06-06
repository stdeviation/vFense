from vFense.core.view import View
from vFense.core.view._constants import DefaultViews
from vFense.core.view._db_model import ViewKeys
from vFense.core.user._db import (
    update_views_for_users, fetch_usernames
)
from vFense.core.view._db import (
    fetch_view, insert_view, update_children_for_view
)
from vFense.core.decorators import time_it
from vFense.errorz._constants import ApiResultKeys

from vFense.errorz.status_codes import (
    DbCodes, ViewCodes, GenericCodes,
    GenericFailureCodes, ViewFailureCodes
)

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
    def create(self, view):
        """Create a new view inside of vFense

        Args:
            view (View): A view instance filled out with the
                appropriate fields.

        Kwargs:
            username (str): Name of the user that you are adding to this view.
                Default=None

        Basic Usage:
            >>> from vFense.core.view import View
            >>> from vFense.core.view.manager import ViewManager
            >>> view = View(
                'global'
                package_download_url='https://10.0.0.15/packages/'
            )
            >>> manager = ViewManager(view.name)
            >>> manager.create(view)

        Returns:
            Dictionary of the status of the operation.
            >>>
            {
                "data": [
                    {
                        "server_queue_ttl": 10,
                        "cpu_throttle": "normal",
                        "view_name": "global",
                        "ancestors": [],
                        "package_download_url_base": "https://10.0.0.15/packages/",
                        "agent_queue_ttl": 10,
                        "parent": null,
                        "net_throttle": 0,
                        "children": [],
                        "users": []
                    }
                ],
                "message": "create - view global created - ",
                "errors": [],
                "vfense_status_code": 14000,
                "generic_status_code": 1010
            }
        """
        view_exist = self.properties
        status = self.create.func_name + ' - '
        msg = ''
        results = {}
        invalid_fields = view.get_invalid_fields()
        results[ApiResultKeys.ERRORS] = invalid_fields

        if not invalid_fields and not view_exist:
            # Fill in any empty fields
            view.fill_in_defaults()
            parent_view = {}
            if view.name == DefaultViews.GLOBAL:
                view.parent = None
                view.ancestors = []
                view.children = []

            else:
                if not view.parent:
                    view.parent = DefaultViews.GLOBAL
                    view.ancestors = [view.parent]
                    parent_view = fetch_view(view.parent)

                else:
                    parent_view = fetch_view(view.parent)
                    if parent_view:
                        parent_view[ViewKeys.Children].append(view.name)
                        view.ancestors = parent_view[ViewKeys.Ancestors]
                        view.ancestors.append(view.parent)

            if not view.package_download_url:
                view.package_download_url = (
                    fetch_view(
                        DefaultViews.GLOBAL,
                        [ViewKeys.PackageUrl]
                    ).get(ViewKeys.PackageUrl)
                )

            usernames = list(set(fetch_usernames(True) + view.users))
            view.users = usernames
            object_status, _, _, generated_ids = (
                insert_view(view.to_dict())
            )

            if object_status == DbCodes.Inserted:
                generated_ids.append(view.name)
                msg = 'view %s created - ' % (view.name)
                results[ApiResultKeys.GENERIC_STATUS_CODE] = (
                    GenericCodes.ObjectCreated
                )
                results[ApiResultKeys.VFENSE_STATUS_CODE] = (
                    ViewCodes.ViewCreated
                )
                results[ApiResultKeys.MESSAGE] = status + msg
                results[ApiResultKeys.DATA] = [view.to_dict()]

                if usernames:
                    update_views_for_users(
                        usernames, [view.name]
                    )
                print parent_view, 'foo bar'
                if parent_view:
                    update_children_for_view(
                        parent_view[ViewKeys.ViewName], view.name
                    )

        elif view_exist:
            msg = 'view name %s already exists' % (view.name)
            results[ApiResultKeys.GENERIC_STATUS_CODE] = (
                GenericCodes.ObjectExists
            )
            results[ApiResultKeys.VFENSE_STATUS_CODE] = (
                ViewFailureCodes.ViewExists
            )
            results[ApiResultKeys.MESSAGE] = status + msg

        return results
