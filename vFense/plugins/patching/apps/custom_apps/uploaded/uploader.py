from uuid import uuid4
import logging
import os
import shutil
from vFense import VFENSE_LOGGING_CONFIG, VFENSE_APP_TMP_PATH
from vFense.db.client import db_create_close, r
from vFense.core.results import Results
from vFense.plugins.patching.status_codes import (
    PackageCodes, PackageFailureCodes
)
from vFense.utils.common import date_parser, timestamp_verifier, md5sum
from vFense.plugins.patching._db_model import *
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
        >>> from vFense.plugins.patching.apps.custom_apps.uploaded.uploader import move_app_from_tmp
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
                'md5': md5,
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


@db_create_close
def move_packages(username, view_name, uri, method,
                  name=None, path=None, size=None, md5=None,
                  uuid=None, conn=None):

    files_stored = list()
    PKG_DIR = None
    FILE_PATH = None

    if name and uuid and path and size and md5:
        PKG_DIR = TMP_DIR + uuid + '/'
        FILE_PATH = PKG_DIR + name

        if not os.path.exists(PKG_DIR):
            try:
                os.mkdir(PKG_DIR)
            except Exception as e:
                logger.error(e)
        try:
            shutil.move(path, FILE_PATH)
            files_stored.append(
                {
                    'uuid': uuid,
                    'name': name,
                    'size': int(size),
                    'md5': md5,
                    'file_path': FILE_PATH
                }
            )

            results = (
                Results(
                    username, uri, method
                ).file_uploaded(name, files_stored)
            )

        except Exception as e:
            results = (
                Results(
                    username, uri, method
                ).file_failed_to_upload(name, e)
            )
            logger.error(e)

    return(results)


@db_create_close
def store_package_info_in_db(
        username, view_name, uri, method,
        size, md5, operating_system,
        uuid, name, severity, arch, major_version,
        minor_version, release_date=0.0,
        vendor_name=None, description=None,
        cli_options=None, support_url=None,
        kb=None, conn=None):

    PKG_FILE = TMP_DIR + uuid + '/' + name
    URL_PATH = 'https://localhost/packages/tmp/' + uuid + '/'
    url = URL_PATH + name

    if os.path.exists(PKG_FILE):
        if (isinstance(release_date, str) or
            isinstance(release_date, unicode)):

            orig_release_date = release_date
            if (len(release_date.split('-')) == 3 or len(release_date.split('/')) == 3):
                release_date = (
                    r
                    .epoch_time(date_parser(release_date))
                )

            else:
                release_date = (
                    r
                    .epoch_time(
                        timestamp_verifier(release_date)
                    )
                )

        data_to_store = {
            CustomAppsKey.Name: name,
            CustomAppsPerAgentKey.Dependencies: [],
            CustomAppsKey.RvSeverity: severity,
            CustomAppsKey.VendorSeverity: severity,
            CustomAppsKey.ReleaseDate: release_date,
            CustomAppsKey.VendorName: vendor_name,
            CustomAppsKey.Description: description,
            CustomAppsKey.MajorVersion: major_version,
            CustomAppsKey.MinorVersion: minor_version,
            CustomAppsKey.Version: major_version + '.' + minor_version,
            CustomAppsKey.OsCode: operating_system,
            CustomAppsKey.Kb: kb,
            CustomAppsKey.Hidden: 'no',
            CustomAppsKey.CliOptions: cli_options,
            CustomAppsKey.Arch: arch,
            CustomAppsKey.RebootRequired: 'possible',
            CustomAppsKey.SupportUrl: support_url,
            CustomAppsKey.Views: [view_name],
            CustomAppsPerAgentKey.Update: PackageCodes.ThisIsNotAnUpdate,
            CustomAppsKey.FilesDownloadStatus: PackageCodes.FileCompletedDownload,
            CustomAppsKey.AppId: uuid
        }
        file_data = (
            [
                {
                    FilesKey.FileUri: url,
                    FilesKey.FileSize: int(size),
                    FilesKey.FileHash: md5,
                    FilesKey.FileName: name
                }
            ]
        )
        try:
            updated = (
                r
                .table(AppCollections.CustomApps)
                .insert(data_to_store, upsert=True)
                .run(conn)
            )

            add_custom_app_to_agents(
                username, view_name,
                uri, method, file_data,
                app_id=uuid
            )

            data_to_store['release_date'] = orig_release_date
            results = (
                Results(
                    username, uri, method
                ).object_created(uuid, 'custom_app', data_to_store)
            )
            logger.info(results)

        except Exception as e:
            results = (
                Results(
                    username, uri, method
                ).something_broke(uuid, 'custom_app', e)
            )
            logger.exception(e)
    else:
        results = (
            Results(
                username, uri, method
            ).file_doesnt_exist(name, e)
        )
        logger.info(results)

    return(results)
