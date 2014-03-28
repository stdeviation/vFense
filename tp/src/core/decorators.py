import logging
import logging.config
import json
from datetime import datetime
from functools import wraps

from tornado.web import HTTPError

from vFense.errorz.status_codes import DbCodes
from vFense.errorz.error_messages import GenericResults


logging.config.fileConfig('/opt/TopPatch/conf/logging.config')
logger = logging.getLogger('vFense_stats')


def return_status_tuple(fn):
    """Return the status of the db_call, plus the number of documents"""
    def db_wrapper(*args, **kwargs):
        status = fn(*args, **kwargs)
        return_code = (DbCodes.Nothing, 0, None, [])
        if status['deleted'] > 0:
            return_code = (DbCodes.Deleted, status['deleted'], None, [])

        elif status['errors'] > 0:
            return_code = (
                DbCodes.Errors, status['errors'], status['first_error'], []
            )

        elif status['inserted'] > 0:
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

        elif status['replaced'] > 0:
            return_code = (DbCodes.Replaced, status['replaced'], None, [])

        elif status['skipped'] > 0:
            return_code = (DbCodes.Skipped, status['skipped'], None, [])

        elif status['unchanged'] > 0:
            return_code = (DbCodes.Unchanged, status['unchanged'], None, [])

        else:
            return_code = (DbCodes.DoesntExist, 0, None, [])

        return(return_code)

    return wraps(fn)(db_wrapper)


def results_message(fn):
    """Return the results in the vFense API standard"""
    def db_wrapper(*args, **kwargs):
        data = fn(*args, **kwargs)
        status_code = data[0]
        object_id = data[1]
        object_type = data[2]
        object_data = data[3]
        object_error = data[4]
        username = data[5]
        uri = data[6]
        method = data[7]

        if status_code == DbCodes.Inserted:
            status = (
                GenericResults(
                    username, uri, method
                ).object_created(object_id, object_type, object_data)
            )

        if status_code == DbCodes.Deleted:
            status = (
                GenericResults(
                    username, uri, method
                ).object_deleted(object_id, object_type)
            )

        if status_code == DbCodes.Replaced:
            status = (
                GenericResults(
                    username, uri, method
                ).object_updated(object_id, object_type, object_data)
            )

        elif status_code == DbCodes.Unchanged:
            status = (
                GenericResults(
                    username, uri, method
                ).object_unchanged(object_id, object_type, object_data)
            )

        elif status_code == DbCodes.Skipped:
            status = (
                GenericResults(
                    username, uri, method
                ).invalid_id(object_id, object_type)
            )

        elif status_code == DbCodes.Errors:
            status = (
                GenericResults(
                    username, uri, method
                ).something_broke(object_id, object_type, object_error)
            )

        elif status_code == DbCodes.DoesntExist:
            status = (
                GenericResults(
                    username, uri, method
                ).does_not_exists(object_id, object_type)
            )

        return(status)

    return wraps(fn)(db_wrapper)


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


def agent_authenticated_request(method):
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
            raise HTTPError(403)

        return method(self, *args, **kwargs)

    return wrapper


def convert_json_to_arguments(fn):

    @wraps(fn)
    def wrapper(self, *args, **kwargs):

        content_type = self.request.headers.get("Content-Type", "")

        if content_type.startswith("application/json"):
            self.arguments = json.loads(self.request.body)
            return fn(self, *args, **kwargs)

        else:

            self.set_status(415)
            self.write("Content-type application/json is expected.")

    return wrapper
