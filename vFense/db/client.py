import os
import logging
import logging.config
import ConfigParser
import types
from  functools import wraps

import rethinkdb as r
import redis
from rq import Queue

from vFense._constants import VFENSE_LOGGING_CONFIG, VFENSE_CONFIG

logging.config.fileConfig(VFENSE_LOGGING_CONFIG)
logger = logging.getLogger('rvapi')

Config = ConfigParser.ConfigParser()
Config.read(VFENSE_CONFIG)

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

def rq_settings():
    """Retrieve the database settings for rq
    Returns:
        Tuple (host, port, db)
    """
    try:
        host = Config.get('Queue', 'host')
        port = int(Config.get('Queue', 'port'))
        db = Config.get('Queue', 'db')

    except Exception as e:
        logger.exception(e)

    return(host, port, db)

def rq_queue(queue_name):
    """Return an instance of Queue of the python-rq module.
    Args:
        queue_name (str): The name of the queue you want to return
    """
    try:
        host = Config.get('Queue', 'host')
        port = int(Config.get('Queue', 'port'))
        db = Config.get('Queue', 'db')
        pool = redis.StrictRedis(host=host, port=port, db=db)
        rv_q = Queue(queue_name, connection=pool)

    except Exception as e:
        logger.error(e)

    return rv_q
