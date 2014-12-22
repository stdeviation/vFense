from uuid import uuid4
import logging
import os
import shutil
from vFense._constants import VFENSE_LOGGING_CONFIG, VFENSE_APP_TMP_PATH
from vFense.core.results import ApiResults
from vFense.plugins.patching.status_codes import (
    PackageCodes, PackageFailureCodes
)
from vFense.utils.common import md5sum
from vFense.plugins.patching import FileUploadData


logging.config.fileConfig(VFENSE_LOGGING_CONFIG)
logger = logging.getLogger('vfense_api')

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
    results = ApiResults()
    results.fill_in_defaults()
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
            file_data = FileUploadData()
            file_data.file_name = file_name
            file_data.file_hash = md5
            file_data.file_size = fsize
            file_data.file_uuid = uuid
            file_data.file_path = full_app_path
            results.generic_status_code = PackageCodes.ObjectCreated
            results.vfense_status_code = PackageCodes.FileUploadedSuccessfully
            results.data = file_data.to_dict()
            results.message = (
                'File {0} successfully uploaded'.format(file_name)
            )

        else:
            results.generic_status_code = (
                PackageFailureCodes.FailedToCreateObject
            )
            results.vfense_status_code = (
                PackageFailureCodes.FileUploadFailed
            )
            results.data = []
            results.message = (
                'File {0} failed to upload'.format(file_name)
            )

    except Exception as e:
        results.generic_status_code = (
            PackageFailureCodes.FailedToCreateObject
        )
        results.vfense_status_code = (
            PackageFailureCodes.FileUploadFailed
        )
        results.data = []
        results.message = (
            'File {0} failed to upload: error {1}'
            .format(file_name, e)
        )
        logger.exception(e)

    return results
