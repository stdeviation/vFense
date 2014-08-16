import logging

from vFense import VFENSE_LOGGING_CONFIG
from vFense.plugins.patching._db_model import (
    AppCollections
)

from vFense.plugins.patching.apps.manager import (
    AppsManager
)


logging.config.fileConfig(VFENSE_LOGGING_CONFIG)
logger = logging.getLogger('rvapi')

class CustomAppsManager(AppsManager):
    def __init__(self):
        self.apps_collection = AppCollections.CustomApps
        self.apps_per_agent_collection = AppCollections.DbCommonAppsPerAgent
