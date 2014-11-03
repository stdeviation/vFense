import logging, logging.config
import json
from datetime import datetime
from functools import wraps

from tornado.web import HTTPError

from vFense._constants import VFENSE_LOGGING_CONFIG
from vFense.core.results import (
    ApiResults, ExternalApiResults
)
from vFense.core.status_codes import (
    DbCodes, GenericCodes, GenericFailureCodes
)

logging.config.fileConfig(VFENSE_LOGGING_CONFIG)
logger = logging.getLogger('rvapi')


def return_status_tuple(fn):
    """Return the status of the db_call, plus the number of documents"""
    def db_wrapper(*args, **kwargs):
        status = fn(*args, **kwargs)
        if status['deleted'] > 0:
            return_code = (DbCodes.Deleted, status['deleted'], None, [])

        elif status['errors'] > 0:
            return_code = (
                DbCodes.Errors, status['errors'], status['first_error'], []
            )

        elif status['inserted'] > 0 and status['replaced'] < 1:
            if status.get('generated_keys'):
                return_code = (
                    DbCodes.Inserted, status['inserted'],
                    None, status['generated_keys']
                )
            else:
                return_code = (
                    DbCodes.Inserted, status['inserted'],
                    None, []
                )

        elif status['inserted'] > 0 and status['replaced'] > 0:
            if status.get('generated_keys'):
                return_code = (
                    DbCodes.Inserted, (status['inserted'], status['replaced']),
                    None, status['generated_keys']
                )
            else:
                return_code = (
                    DbCodes.Inserted, (status['inserted'], status['replaced']),
                    None, []
                )

        elif status['replaced'] > 0 and status['inserted'] < 1:
            return_code = (DbCodes.Replaced, status['replaced'], None, [])

        elif status['skipped'] > 0:
            return_code = (DbCodes.Skipped, status['skipped'], None, [])

        elif status['unchanged'] > 0:
            return_code = (DbCodes.Unchanged, status['unchanged'], None, [])

        else:
            return_code = (DbCodes.DoesNotExist, 0, None, [])

        return(return_code)

    return wraps(fn)(db_wrapper)

def results_message(fn):
    """Return the results in the vFense API standard"""
    def db_wrapper(*args, **kwargs):
        data = fn(*args, **kwargs)
        tornado_handler = args[0]

        if isinstance(data, ApiResults):
            status = ExternalApiResults(**data.to_dict_non_null())
            status.username = tornado_handler.get_current_user()
            status.uri = tornado_handler.request.uri
            status.http_method = tornado_handler.request.method

            if data.generic_status_code == GenericCodes.InformationRetrieved:
                status.http_status_code = 200
                if not status.message:
                    status.message = (
                        '{0}: data retrieved'.format(status.username)
                    )


            elif data.generic_status_code == GenericCodes.ObjectCreated:
                status.http_status_code = 200
                if not status.message:
                    status.message = (
                        '{0}: object created'.format(status.username)
                    )

            elif (
                data.generic_status_code ==
                GenericCodes.AuthorizationGranted
            ):
                status.http_status_code = 200
                if not status.message:
                    status.message = (
                        '{0}: authorization granted'.format(status.username)
                    )

            elif (
                data.generic_status_code ==
                GenericFailureCodes.FailedToCreateObject
            ):
                status.http_status_code = 409
                if not status.message:
                    status.message = (
                        '{0}: failed to create object'.format(status.username)
                    )

            elif (
                data.generic_status_code == GenericCodes.ObjectUpdated or
                data.generic_status_code == GenericCodes.ObjectsUpdated
            ):
                status.http_status_code = 200
                if not status.message:
                    status.message = (
                        '{0}: object updated'.format(status.username)
                    )

            elif (
                data.generic_status_code ==
                GenericFailureCodes.FailedToUpdateObject
            ):
                status.http_status_code = 409
                if not status.message:
                    status.message = (
                        '{0}: failed to update object'.format(status.username)
                    )

            elif (
                data.generic_status_code == GenericCodes.ObjectDeleted or
                data.generic_status_code == GenericCodes.ObjectsDeleted
            ):
                status.http_status_code = 200
                if not status.message:
                    status.message = (
                        '{0}: object deleted'.format(status.username)
                    )

            elif (
                data.generic_status_code ==
                GenericFailureCodes.FailedToDeleteObject
            ):
                status.http_status_code = 409
                if not status.message:
                    status.message = (
                        '{0}: failed to delete object'.format(status.username)
                    )

            elif (
                data.generic_status_code == GenericCodes.ObjectUnchanged or
                data.generic_status_code == GenericCodes.ObjectsUnchanged
            ):
                status.http_status_code = 200
                if not status.message:
                    status.message = (
                        '{0}: object unchanged'.format(status.username)
                    )

            elif (
                data.generic_status_code == GenericCodes.InvalidId or
                data.generic_status_code == GenericFailureCodes.InvalidId or
                data.generic_status_code == GenericCodes.InvalidValue or
                data.generic_status_code == GenericFailureCodes.InvalidFilterKey or
                data.generic_status_code == GenericFailureCodes.InvalidFields
            ):
                status.http_status_code = 404
                if not status.message:
                    status.message = (
                        '{0}: invalid object'.format(status.username)
                    )

            elif data.generic_status_code == GenericCodes.DoesNotExist:
                status.http_status_code = 409
                if not status.message:
                    status.message = (
                        '{0}: object does not exist'.format(status.username)
                    )
            else:
                status.http_status_code = 200

        else:
            status = ExternalApiResults()
            status.username = tornado_handler.get_current_user()
            status.uri = tornado_handler.request.uri
            status.http_method = tornado_handler.request.method
            status.http_status_code = 404
            if not status.message:
                status.message = '{0}: invalid instance'.format(type(data))

        return status

    return wraps(fn)(db_wrapper)

def catch_it(return_value):
    """wrap non external calls in a try catch exception
    Args:
        return_value (ANYTHING): This is the value you want to return,
            if an exception is caught by this decorator.
    """
    def wrapper(fn):
        def wrapped(*args, **kwargs):
            try:
                data = fn(*args, **kwargs)
            except Exception as e:
                data = return_value
                results = ApiResults()
                results.fill_in_defaults()
                results.generic_status_code = GenericCodes.SomethingBroke
                results.vfense_status_code = GenericCodes.SomethingBroke
                results.http_status_code = 500
                results.errors.append(e)
                results.message = (
                    'Something broke while calling {0}: {1}'
                    .format(fn.__name__, e)
                )
                logger.exception(results.to_dict_non_null())

            return data
        return wraps(fn)(wrapped)

    return wrapper

def api_catch_it(fn):
    """wrap all external api calls in a try catch exception"""
    def wrapper(*args, **kwargs):
        tornado_handler = args[0]
        try:
            results = fn(*args, **kwargs)
        except Exception as e:
            results = ExternalApiResults()
            results.fill_in_defaults()
            results.generic_status_code = GenericCodes.SomethingBroke
            results.vfense_status_code = GenericCodes.SomethingBroke
            results.uri = tornado_handler.request.uri
            results.http_method = tornado_handler.request.method
            results.username = tornado_handler.get_current_user()
            results.http_status_code = 500
            results.errors.append(e)
            results.message = (
                'Something broke while calling {0}: {1}'
                .format(fn.__name__, e)
            )
            logger.exception(results.to_dict_non_null())
            tornado_handler.set_status(results.http_status_code)
            tornado_handler.set_header('Content-Type', 'application/json')
            tornado_handler.write(json.dumps(results.to_dict_non_null(), indent=4))

        return results

    return wraps(fn)(wrapper)

def time_it(fn):
    """Return the status of the db_call, plus the number of documents"""
    def db_wrapper(*args, **kwargs):
        start_time = datetime.now()
        output = fn(*args, **kwargs)
        end_time = datetime.now()
        total_time_to_complete = end_time - start_time
        message = (
            ':%s: took %s seconds to run' %
            (fn.func_name, total_time_to_complete.total_seconds())
        )
        logger.debug(message)

        return(output)

    return wraps(fn)(db_wrapper)

def authenticated_request(method):
    """ Decorator that handles authenticating the request. Uses secure cookies.
    In the spirit of the tornado.web.authenticated decorator.
    """
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        # Get the access token argument. If nothing is provided, string will be
        # "Invalid". Chose this way instead of using "try" and catching
        # HttpError 400 which get_argument throws
        #access_token = str(self.get_argument("access_token", default="Invalid"))

        # Check if an access token is legit.
        # if access_token != "Invalid":
        #     return method(self, *args, **kwargs)

        # If the access token is not provided, assumes is the main ui client.
        if not self.current_user:
            if self.request.method in ("GET", "HEAD", "POST"):
                url = self.get_login_url()
                # if "?" not in url:
                #     if urlparse.urlsplit(url).scheme:
                #         if login url is absolute, make next absolute too
                        # next_url = {'next': self.request.full_url()}
                    # else:
                    #     next_url = {'next': self.request.uri}
                    # url += "?" + urllib.urlencode(next_url)
                self.redirect(url)
                return
            raise HTTPError(403)

        return method(self, *args, **kwargs)

    return wrapper

def convert_json_to_arguments(fn):
    @wraps(fn)
    def wrapper(self, *args, **kwargs):
        content_type = self.request.headers.get("Content-Type", "")
        if content_type.startswith("application/json"):
            try:
                self.arguments = json.loads(self.request.body)
            except Exception as e:
                self.arguments = {}

            return fn(self, *args, **kwargs)

        else:
            self.set_status(415)
            self.write("Content-type application/json is expected.")

    return wrapper
