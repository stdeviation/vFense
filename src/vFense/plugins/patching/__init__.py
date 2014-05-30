import logging, logging.config
from vFense import VFENSE_LOGGING_CONFIG
from vFense.db.client import db_connect, r
from vFense.plugins.patching._db_model import *
from vFense.core._db import (
    retrieve_collections, create_collection, retrieve_indexes
)

logging.config.fileConfig(VFENSE_LOGGING_CONFIG)
logger = logging.getLogger('rvapi')

def initialize_collections(collection, current_collections):
    name, key = collection
    if name not in current_collections:
        create_collection(name, key)

def initialize_indexes(indexes):
try:
    app_collections = [
        (AppCollections.UniqueApplications, AppsKey.AppId),
        (AppCollections.AppsPerAgent, Id),
        (AppCollections.CustomApps, CustomAppsKey.AppId),
        (AppCollections.CustomAppsPerAgent, Id),
        (AppCollections.SupportedApps, SupportedAppsKey.AppId),
        (AppCollections.SupportedAppsPerAgent, Id),
        (AppCollections.vFenseApps, vFenseAppsKey.AppId),
        (AppCollections.vFenseAppsPerAgent, Id),
    ]
    current_collections = retrieve_collections()
    for collection in collections:
        initialize_collections(collection, current_collections)
        indexes = retrieve_indexes(collection)


except Exception as e:
    logger.exception(e)
