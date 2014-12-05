from vFense.db.client import db_create_close
from vFense.core._db import (
    retrieve_collections, create_collection, retrieve_indexes,
    db_exist, create_db
)

class DbInit(object):
    """Initiliaze the database and its collections and the secondary
        indexes of those collections.

    Attributes:
    self.current_collections (list): List of tables in rethinkdb.

    Methods:
        initialize
        initialize_indexes
        initialize_collection
    """
    def __init__(self):
        if not db_exist:
            create_db()
        self.current_collections = retrieve_collections()

    @db_create_close
    def initialize_indexes(self, secondary_indexes, conn=None):
        """Initialize all indexes for a collection
        Args:
            secondary_indexes (list of tuples):
                [(collection_name, index_name, rql query)]
                Example... [(agents, os_code, rql_secondary_index)]
        """
        for secondary_index in secondary_indexes:

            collection, index_name, index = secondary_index
            indexes = retrieve_indexes(collection)
            if index_name not in indexes:
                index.run(conn)

    def initialize_collection(self, collection, primary_key):
        """Create a collection and assign the primary key of this collection.
        Args:
            collection(str): The name of the collection you are creating.
            primary_key (str): The name of the primary key.
        """
        if collection not in self.current_collections:
            create_collection(collection, primary_key)

    def initialize(self, collections, secondary_indexes):
        """Create and or Update collections and secondary indexes
        Args:
            collections (list of tuples): [(collection_name, primary_key)]
                Example.. [(agents, agent_id)]
            secondary_indexes (list of tuples):
                [(collection_name, index_name, rql query)]
                Example... [(agents, os_code, rql_secondary_index)]
        """
        for collection_info in collections:
            collection, primary_key = collection_info
            self.initialize_collection(collection, primary_key)
            self.initialize_indexes(secondary_indexes)
