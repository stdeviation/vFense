#!/usr/bin/env python

from vFense.db.client import db_connect, r
from vFense.plugins.mightymouse import *

Id = 'id'
def initialize_indexes_and_create_tables():
    tables = [
        (FileCollections.FileServers, FileServerKeys.FileServerName),
    ]
    conn = db_connect()
#################################### If Collections do not exist, create them #########################
    list_of_current_tables = r.table_list().run(conn)
    for table in tables:
        if table[0] not in list_of_current_tables:
            r.table_create(table[0], primary_key=table[1]).run(conn)

#################################### Get All Indexes ###################################################
    file_server_list = r.table(FileCollections.FileServers).index_list().run(conn)

#################################### File Server Indexes ###################################################
    if not FileServerIndexes.ViewName in file_server_list:
        r.table(FileCollections.FileServers).index_create(FileServerIndexes.ViewName).run(conn)

#################################### Close Database Connection ###################################################
    conn.close()
