from functools import wraps
from json import dumps

from vFense.core.status_codes import GenericCodes
from vFense.core.results import Results, ApiResultKeys
from vFense.core.permissions.permissions import verify_permission_for_user
from vFense.core.group._db_model import GroupKeys


def check_permissions(permission):
    def wrapper(fn):
        def wrapped(*args, **kwargs):
            granted = False
            tornado_handler = args[0]
            active_user = tornado_handler.get_current_user()
            uri = tornado_handler.request.uri
            http_method = tornado_handler.request.method
            granted, status_code = (
                verify_permission_for_user(active_user, permission)
            )
            if granted and status_code == GenericCodes.PermissionGranted:
                data = fn(*args, **kwargs)
                return data

            elif not granted and status_code == GenericCodes.PermissionDenied:
                results = (
                    Results(
                        active_user, uri, http_method
                    ).permission_denied()
                )

                tornado_handler.set_header('Content-Type', 'application/json')

                tornado_handler.write(dumps(results, indent=4))

            elif not granted and status_code == GenericCodes.InvalidPermission:
                data = {
                    ApiResultKeys.DATA: (
                        {
                            GroupKeys.Permissions: [permission]
                        }
                    )
                }
                results = (
                    Results(
                        active_user, uri, http_method
                    ).invalid_permission(**data)
                )

                tornado_handler.set_header('Content-Type', 'application/json')
                tornado_handler.write(dumps(results, indent=4))

            elif not granted and status_code == GenericCodes.InvalidId:
                msg = {
                    ApiResultKeys.MESSAGE: (
                        'Invalid username {0}'.format(active_user)
                    )
                }
                results = (
                    Results(
                        active_user, uri, http_method
                    ).invalid_id(**msg)
                )

                tornado_handler.set_header('Content-Type', 'application/json')
                tornado_handler.write(dumps(results, indent=4))

        return wraps(fn)(wrapped)

    return(wrapper)
