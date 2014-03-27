from datetime import datetime
import logging
import logging.config
from functools import wraps

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
