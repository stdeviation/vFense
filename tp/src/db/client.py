import os
import logging
import logging.config
from  functools import wraps
import ConfigParser
import types

from vFense.errorz.status_codes import DbCodes
from vFense.errorz.error_messages import GenericResults
import rethinkdb as r
import redis

logging.config.fileConfig('/opt/TopPatch/conf/logging.config')
logger = logging.getLogger('rvapi')

pool = redis.ConnectionPool(host='localhost', port=6379, db=0)
db_config='/opt/TopPatch/conf/database.conf'
Config = ConfigParser.ConfigParser()
Config.read(db_config)

def db_connect(new_db_config=None):
    conn = None
    if new_db_config:
        if os.path.exists(new_db_config):
            Config.read(new_db_config)
        else:
            logger.error('Config File does not exists: %s' % (new_db_config))
    try:
        host = Config.get('Database', 'host')
        port = int(Config.get('Database', 'driver-port'))
        db = Config.get('Database', 'db-name')
        conn = r.connect(host, port, db)

    except Exception as e:
        logger.error(e)

    return conn


def db_create_close(fn):
    def db_wrapper(*args, **kwargs):

        output = None
        conn = db_connect()
        if len(kwargs) >= 0 and isinstance(kwargs, dict) and\
                len(args) >= 1:

            if isinstance(args[0], types.InstanceType) or\
                    isinstance(args[0], types.MethodType):
                kwargs['conn'] = conn
                fake_self = args[0]

                if args > 1:
                    args = list(args[1:])

                else:
                    args = []

                output = fn(fake_self, *args, **kwargs)
                conn.close()

            else:
                kwargs['conn'] = conn
                output = fn(*args, **kwargs)
                conn.close()

        elif len(kwargs) >= 0 and isinstance(kwargs, dict) and len(args) >= 0:
            kwargs['conn'] = conn
            output = fn(*args, **kwargs)
            conn.close()

        elif len(args) > 0 and isinstance(args, list):
            args.insert(conn)
            output = fn(*args)
            conn.close()

        elif len(args) > 0 and isinstance(args, tuple) and len(kwargs) == 0:

            args = list(args)
            self = args.pop(0)

            if len(args) > 0:

                output = fn(self, conn, args[0])
                conn.close()

            else:

                output = fn(self, conn)
                conn.close()
        else:

            output = fn(conn)
            conn.close()

        return(output)

    return wraps(fn) (db_wrapper)


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

        return(return_code)

    return wraps(fn) (db_wrapper)

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

        return(status)

    return wraps(fn) (db_wrapper)
