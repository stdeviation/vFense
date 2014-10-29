from functools import wraps
from json import dumps

from vFense.core.status_codes import GenericCodes
from vFense.core.results import ExternalApiResults
from vFense.core.permissions.permissions import verify_permission_for_user

def check_permissions(permission):
    def wrapper(fn):
        def wrapped(*args, **kwargs):
            results = ExternalApiResults()
            results.fill_in_defaults()
            granted = False
            tornado_handler = args[0]
            results.username = tornado_handler.get_current_user()
            results.uri = tornado_handler.request.uri
            results.http_method = tornado_handler.request.method
            granted, status_code = (
                verify_permission_for_user(results.username, permission)
            )
            if granted and status_code == GenericCodes.PermissionGranted:
                results = fn(*args, **kwargs)
                return results

            elif not granted and status_code == GenericCodes.PermissionDenied:
                results.http_status_code = 403
                results.message = (
                    'Permission {0} denied for user {1}'
                    .format(permission, results.username)
                )
                tornado_handler.set_header('Content-Type', 'application/json')
                tornado_handler.write(
                    dumps(results.to_dict_non_null(), indent=4)
                )

            elif not granted and status_code == GenericCodes.InvalidPermission:
                results.http_status_code = 404
                results.message = (
                    'Invalid permission {0} for user {1}'
                    .format(permission, results.username)
                )
                tornado_handler.set_header('Content-Type', 'application/json')
                tornado_handler.write(dumps(results, indent=4))

            elif not granted and status_code == GenericCodes.InvalidId:
                results.http_status_code = 404
                results.message = (
                    'Invalid username {0}'.format(results.username)
                )
                tornado_handler.set_header('Content-Type', 'application/json')
                tornado_handler.write(dumps(results, indent=4))

        return wraps(fn)(wrapped)

    return wrapper
