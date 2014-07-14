from functools import wraps
from json import dumps

from vFense.core.status_codes import GenericCodes
from vFense.result.error_messages import GenericResults
from vFense.core.permissions.permissions import verify_permission_for_user


def check_permissions(permission):
    def wrapper(fn):
        def wrapped(*args, **kwargs):
            granted = False
            tornado_handler = args[0]
            username = tornado_handler.get_current_user()
            uri = tornado_handler.request.uri
            method = tornado_handler.request.method
            granted, status_code = (
                verify_permission_for_user(username, permission)
            )
            if granted and status_code == GenericCodes.PermissionGranted:
                data = fn(*args, **kwargs)
                return data

            elif not granted and status_code == GenericCodes.PermissionDenied:
                results = (
                    GenericResults(
                        username, uri, method
                    ).permission_denied(username)
                )

                tornado_handler.set_header('Content-Type', 'application/json')

                tornado_handler.write(dumps(results, indent=4))

            elif not granted and status_code == GenericCodes.InvalidPermission:
                results = (
                    GenericResults(
                        username, uri, method
                    ).invalid_permission(username, permission)
                )

                tornado_handler.set_header('Content-Type', 'application/json')
                tornado_handler.write(dumps(results, indent=4))

            elif not granted and status_code == GenericCodes.InvalidId:
                results = (
                    GenericResults(
                        username, uri, method
                    ).invalid_id(username, 'permissions')
                )

                tornado_handler.set_header('Content-Type', 'application/json')
                tornado_handler.write(dumps(results, indent=4))

        return wraps(fn)(wrapped)

    return(wrapper)
