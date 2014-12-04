from vFense.core._db import (
    retrieve_collections, create_collection, retrieve_indexes,
    db_exist, create_db
)

class DbInit(object):
    def __init__(self):
        if not db_exist:
            create_db()
        self.current_collections = retrieve_collections()

    def initialize_indexes(self, collection, indexes):
        pass

    def initialize_collection(self, collection, primary_key):
        if collection not in self.current_collections:
            create_collection(collection, primary_key)

    def initialize(self, collections):
        for collection_info in collections:
            collection, primary_key = collection_info
            self.initialize_collection(collection, primary_key)
            indexes = retrieve_indexes(collection)
            self.initialize_indexes(collection, indexes)
