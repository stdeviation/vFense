from vFense.core.customer import *
import logging
from vFense.db.client import db_create_close, r

logging.config.fileConfig('/opt/TopPatch/conf/logging.config')
logger = logging.getLogger('rvapi')


@db_create_close
def retrieve_object(primary_key, collection, conn=None):
    """
    Retrieve object by primary key and collection.
    :param primary_key:  The primary key that you are doing a get against.
    :param collection:  The table aka collection you are doing the query against.
    Basic Usage::
        >>> from vFense._db import retrieve_object
        >>> collection, = 'users'
        >>> primary_key = 'admin'
        >>> retrieve_object(primary_key, collection)
    """
    data = {}
    try:
        data = (
            r
            .table(collection)
            .get(primary_key)
            .run(conn)
        )

    except Exception as e:
        logger.exception(e)

    return(data)
