from uuid import uuid4
import logging
import os
import shutil
from vFense import VFENSE_LOGGING_CONFIG, VFENSE_APP_TMP_PATH
from vFense.core.view.manager import ViewManager
from vFense.core.view import ViewKeys
from vFense.core._db_constants import DbTime
from vFense.plugins.patching.status_codes import (
    PackageCodes, PackageFailureCodes
)
from vFense.utils.common import md5sum
from vFense.plugins.patching import Apps, Files
from vFense.plugins.patching._db_model import (
    AppCollections, DbCommonAppKeys
)
from vFense.plugins.patching.apps.custom_apps.custom_apps import add_custom_app_to_agents
from vFense.core.results import Results, ApiResultKeys


logging.config.fileConfig(VFENSE_LOGGING_CONFIG)
logger = logging.getLogger('rvapi')

TMP_DIR = VFENSE_APP_TMP_PATH

if not os.path.exists(TMP_DIR):
    os.mkdir(TMP_DIR)


def gen_uuid():
    return(str(uuid4()))


def move_app_from_tmp(file_name, tmp_path, uuid):
    """
    Move application from the temporary directory to the
        the var/packages/tmp directory.

    Args
        file_name (str): The name of the file that was uploaded.
        tmp_path (str): The location to where the file was uploaded.
        uuid (str): The generated UUID.

    Basic Usage:
        >>> from vFense.plugins.patching.uploader.uploader import move_app_from_tmp
        >>> file_name = "apps.csv"
        >>> tmp_path = "/tmp/apps/0000001"
        >>> uuid = "bda154f3-c941-465d-ac9b-0c2821d4a4a2"
        >>> move_app_from_tmp(file_name, tmp_path, uuid)

    Returns:
    """
    results = {}
    base_app_dir = os.path.join(TMP_DIR, uuid)
    full_app_path = os.path.join(base_app_dir, file_name)

    if not os.path.exists(base_app_dir):
        try:
            os.mkdir(base_app_dir)
        except Exception as e:
            logger.exception(e)

    try:
        if os.path.exists(tmp_path):
            fsize = os.stat(tmp_path).st_size
            md5 = md5sum(tmp_path)
            shutil.move(tmp_path, full_app_path)
            data = {
                'uuid': uuid,
                'name': file_name,
                'size': fsize,
                'hash': md5,
                'file_path': full_app_path
            }
            results[ApiResultKeys.GENERIC_STATUS_CODE] = (
                PackageCodes.ObjectCreated
            )
            results[ApiResultKeys.VFENSE_STATUS_CODE] = (
                PackageCodes.FileUploadedSuccessfully
            )
            results[ApiResultKeys.DATA] = data
            results[ApiResultKeys.MESSAGE] = (
                'File {0} successfully uploaded'.format(file_name)
            )

        else:
            results[ApiResultKeys.GENERIC_STATUS_CODE] = (
                PackageFailureCodes.FailedToCreateObject
            )
            results[ApiResultKeys.VFENSE_STATUS_CODE] = (
                PackageFailureCodes.FileUploadFailed
            )
            results[ApiResultKeys.DATA] = []
            results[ApiResultKeys.MESSAGE] = (
                'File {0} failed to upload'.format(file_name)
            )

    except Exception as e:
        results[ApiResultKeys.GENERIC_STATUS_CODE] = (
            PackageFailureCodes.FailedToCreateObject
        )
        results[ApiResultKeys.VFENSE_STATUS_CODE] = (
            PackageFailureCodes.FileUploadFailed
        )
        results[ApiResultKeys.DATA] = []
        results[ApiResultKeys.MESSAGE] = (
            'File {0} failed to upload: error {1}'
            .format(file_name, e)
        )
        logger.exception(e)

    return(results)


class UploadManager(object):
    def __init__(self, view):
        self.view = view

    def url_tmp_path(self, uuid, app_name):
        view = ViewManager(self.view)
        tmp_url = (
            os.path.join(
                view.get_attribute(ViewKeys.PackageUrl),
                'tmp', uuid, app_name
            )
        )
        return tmp_url

    def local_file_path(self, uuid, app_name):
        return os.path.join(VFENSE_APP_TMP_PATH, uuid, app_name)

    def store_app_in_db(self, app, file_data, views=None):
        """Store the uploaded application into the vFense database.
        Args:
            apps (Apps): The App instance that contains all the application
                data.
            file_data (Files): The Files instance that contains all the
                file related data.

        Kwargs:
            views (list): List of views, you want this application to be made
                available.

        Basic Usage:
            >>> from vFense.plugins.patching.uploader.uploader import UploadManager
            >>> from vFense.plugins.patching import Apps, Files


        Returns:
        """
        results = {}
        if isinstance(app, Apps) and isinstance(file_data, Files):
            app_invalid_fields = app.get_invalid_fields()
            file_invalid_fields = file_data.get_invalid_fields()
            if not app_invalid_fields and not file_invalid_fields:
                app_location = self.local_file_path(app.name, app.app_id)
                app_url = self.url_tmp_path(app.name, app.app_id)
                if os.path.exists(app_location):
                    app.fill_in_defaults()
                    app_data = app.to_dict().copy()
                    app_data[DbCommonAppKeys.ReleaseDate] = (
                        DbTime.epoch_time_to_db_time(app.release_date)
                    )
                    object_status, _, _, _ = (
                        insert_app_data(app_data, AppCollections.CustomApps)
                    )
                    if object_status == DbCodes.Inserted:
                        add_custom_app_to_agents(
                            username, view_name,
                            uri, method, file_data,
                            app_id=uuid
                        )
                        msg = 'app %s uploaded succesfully - ' % (app.name)
                        results[ApiResultKeys.GENERIC_STATUS_CODE] = (
                            PackageCodes.ObjectCreated
                        )
                        results[ApiResultKeys.VFENSE_STATUS_CODE] = (
                            PackageCodes.FileUploadedSuccessfully
                        )
                        results[ApiResultKeys.MESSAGE] = msg
                        results[ApiResultKeys.DATA] = [app.to_dict()]

        return results
