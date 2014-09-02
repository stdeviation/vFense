import logging
import logging.config
from vFense import (
    VFENSE_LOGGING_CONFIG, VFENSE_APP_PATH,
    VFENSE_APP_DEP_PATH
)
import os
import re

from urlgrabber import urlgrab

from vFense.plugins.patching.status_codes import PackageCodes
from vFense.utils.common import hash_verify

from vFense.plugins.patching._db_model import AppsKey, AppCollections
from vFense.plugins.patching._db import update_app_data_by_app_id

logging.config.fileConfig(VFENSE_LOGGING_CONFIG)
logger = logging.getLogger('rvapi')


def create_necessary_dirs():
    if not os.path.exists(VFENSE_APP_PATH):
        os.mkdir(VFENSE_APP_PATH)
    if not os.path.exists(VFENSE_APP_DEP_PATH):
        os.mkdir(VFENSE_APP_DEP_PATH)


def check_if_redhat(os_string):
    REDHAT = 'Red Hat Enterprise Linux Server'
    if re.search(REDHAT, os_string, re.IGNORECASE):
        return True

    return False


def download_file(uri, dl_path, throttle):
    if uri.startswith('https://api.github.com/'):
        # TODO: handle 200 and 302 response
        headers = (("Accept", "application/octet-stream"),)
        urlgrab(uri, filename=dl_path, throttle=throttle, http_headers=headers)

    else:
        urlgrab(uri, filename=dl_path, throttle=throttle)


def download_all_files_in_app(app, file_data=None,
        throttle=0, collection=AppCollections.UniqueApplications):

    create_necessary_dirs()
    throttle *= 1024

    if not file_data and check_if_redhat(app.os_string):
        download_status = {
            AppsKey.FilesDownloadStatus: \
                PackageCodes.AgentWillDownloadFromVendor
        }
        update_app_data_by_app_id(app.app_id, download_status, collection)

    elif len(file_data) > 0:
        app_path = os.path.join(VFENSE_APP_PATH, str(app.app_id))
        if not os.path.exists(app_path):
            os.mkdir(app_path)

        num_of_files_to_download = len(file_data)
        num_of_files_downloaded = 0
        num_of_files_mismatch = 0
        num_of_files_failed = 0
        num_of_files_invalid_uri = 0

        new_status = {
            AppsKey.FilesDownloadStatus: PackageCodes.FileIsDownloading
        }

        for file_info in file_data:

            if app.os_code == 'linux':
                file_path = (
                    os.path.join(VFENSE_APP_DEP_PATH, file_info.file_name)
                )
            else:
                file_path = os.path.join(app_path, file_info.file_name)

            symlink_path = os.path.join(app_path, file_info.file_name)
            cmd = 'ln -s %s %s' % (file_path, symlink_path)

            try:
                if file_info.download_url and not os.path.exists(file_path):
                    download_file(file_info.download_url, file_path, throttle)

                    if os.path.exists(file_path):
                        if file_info.file_hash:
                            hash_match = hash_verify(
                                orig_hash=file_info.file_hash,
                                file_path=file_path
                            )

                            if hash_match:
                                num_of_files_downloaded += 1

                                if app.os_code == 'linux':
                                    if not os.path.islink(file_path):
                                        os.system(cmd)
                            else:
                                num_of_files_mismatch += 1

                        elif file_info.file_size and not file_info.file_hash:
                            if (os.path.getsize(file_path) ==
                                    file_info.file_size):
                                num_of_files_downloaded += 1
                            else:
                                num_of_files_mismatch += 1
                    else:
                        num_of_files_failed += 1

                elif os.path.exists(file_path) and app.os_code == 'linux':

                    if not os.path.islink(symlink_path):
                        os.system(cmd)

                    num_of_files_downloaded += 1

                elif os.path.exists(file_path) and app.os_code != 'linux':
                    num_of_files_downloaded += 1

                elif file_info.download_url:
                    num_of_files_invalid_uri += 1

            except Exception as e:
                logger.exception(e)

        if num_of_files_downloaded == num_of_files_to_download:
            new_status[AppsKey.FilesDownloadStatus] = (
                PackageCodes.FileCompletedDownload
            )

        elif num_of_files_mismatch > 0:
            new_status[AppsKey.FilesDownloadStatus] = (
                PackageCodes.FileSizeMisMatch
            )

        elif num_of_files_failed > 0:
            new_status[AppsKey.FilesDownloadStatus] = (
                PackageCodes.FileFailedDownload
            )

        elif num_of_files_invalid_uri > 0:
            new_status[AppsKey.FilesDownloadStatus] = (
                PackageCodes.InvalidUri
            )

        db_update_response = update_app_data_by_app_id(
            app.app_id, new_status, collection
        )

        logger.info(
            '%s, %s, %s, %s' %
            (collection, app.app_id, str(new_status), db_update_response)
        )
