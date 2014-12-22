import logging
import os

from vFense._constants import VFENSE_LOGGING_CONFIG
from vFense.plugins.patching._db_model import (
    AppCollections
)

from vFense.plugins.patching.apps.manager import (
    AppsManager
)
from vFense.core.status_codes import DbCodes
from vFense.core.results import ApiResults
from vFense.plugins.patching import Apps
from vFense.plugins.patching._db import insert_app_data
from vFense.plugins.patching.status_codes import (
    PackageCodes, PackageFailureCodes
)


logging.config.fileConfig(VFENSE_LOGGING_CONFIG)
logger = logging.getLogger('vfense_api')

class CustomAppsManager(AppsManager):
    def __init__(self):
        self.apps_collection = AppCollections.CustomApps
        self.apps_per_agent_collection = AppCollections.DbCommonAppsPerAgent

    def store_app_in_db(self, app, file_data, views=None):
        """Store the uploaded application into the vFense database.
        Args:
            apps (Apps): The App instance that contains all the application
                data.

        Kwargs:
            file_data (list): List of Files instances that contains all the
                file related data.
            views (list): List of views, you want this application to be made
                available.

        Basic Usage:
            >>> from vFense.plugins.patching.uploader.uploader import UploadManager
            >>> from vFense.plugins.patching import Apps, Files


        Returns:
        """
        results = ApiResults()
        if isinstance(app, Apps) and isinstance(file_data, list):
            app_invalid_fields = app.get_invalid_fields()
            if not app_invalid_fields:
                app_location = self.local_file_path(app.name, app.app_id)
                if os.path.exists(app_location):
                    app.fill_in_defaults()
                    object_status, _, _, _ = (
                        insert_app_data(
                            app.to_dict_db_apps(), self.apps_collection
                        )
                    )
                    if object_status == DbCodes.Inserted:
                        self.store_file_data_in_db(file_data)
                        msg = 'app %s uploaded succesfully - ' % (app.name)
                        results.generic_status_code = (
                            PackageCodes.ObjectCreated
                        )
                        results.vfense_status_code = (
                            PackageCodes.FileUploadedSuccessfully
                        )
                        results.message = msg
                        results.data = [app.to_dict()]

                else:
                    msg = (
                        'Failed to upload {0}, file doesnt exist'
                        .format(app.name)
                    )
                    results.generic_status_code = (
                        PackageFailureCodes.FailedToCreateObject
                    )
                    results.vfense_status_code = (
                        PackageFailureCodes.FileUploadFailed
                    )
                    results.message = msg
                    results.data = [app.to_dict_apps()]

            else:
                msg = (
                    'Failed to add {0}, contained invalid_fields {1}'
                    .format(app.name, ', '.join(app_invalid_fields))
                )
                results.errors = app_invalid_fields
                results.generic_status_code = (
                    PackageFailureCodes.FailedToCreateObject
                )
                results.vfense_status_code = (
                    PackageFailureCodes.FileUploadFailed
                )
                results.message = msg
                results.data = [app.to_dict_apps()]

        else:
            msg = (
                'Not a valid Apps {0} or Files {1} instance'
                .format(type(app), type(file_data))
            )
            results.generic_status_code = (
                PackageFailureCodes.FailedToCreateObject
            )
            results.vfense_status_code = (
                PackageFailureCodes.FileUploadFailed
            )
            results.message = msg
            results.data = []

        return results
