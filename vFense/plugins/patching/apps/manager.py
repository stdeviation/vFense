import os
import logging
from time import time

from vFense._constants import VFENSE_LOGGING_CONFIG, VFENSE_APP_TMP_PATH
from vFense.core.agent._db import(
    fetch_agent_ids_in_views
)
from vFense.core.agent.manager import AgentManager
from vFense.core._db import insert_data_in_table
from vFense.core.status_codes import DbCodes
from vFense.core.results import ApiResults
from vFense.core.view.manager import ViewManager
from vFense.db.client import redis_pool
from vFense.plugins.patching import Apps, Files
from vFense.plugins.patching._constants import AppStatuses, CommonAppKeys
from vFense.plugins.patching._db_model import AppCollections, DbCommonAppKeys
from vFense.plugins.patching.status_codes import (
    PackageCodes, PackageFailureCodes
)
from vFense.plugins.patching.file_data import add_file_data
from vFense.plugins.patching._db import (
    fetch_app_data, fetch_apps_data_by_os_code, insert_app_data,
    delete_apps_per_agent_older_than
)
from vFense.plugins.patching.downloader.downloader import (
    download_all_files_in_app
)

import vFense.plugins.vuln.cve.cve as cve
from vFense.plugins.vuln.search.vuln_search import RetrieveVulns

from rq.decorators import job


logging.config.fileConfig(VFENSE_LOGGING_CONFIG)
logger = logging.getLogger('vfense_api')

class AppsManager(object):
    def __init__(self):
        self.apps_collection = AppCollections.UniqueApplications
        self.apps_per_agent_collection = AppCollections.AppsPerAgent

    def url_path(self, app_id, app_name, view):
        view = ViewManager(view)
        tmp_url = (
            os.path.join(
                view.properties.package_url,
                app_id, app_name
            )
        )
        return tmp_url

    def url_tmp_path(self, app_id, app_name, view):
        view = ViewManager(view)
        tmp_url = (
            os.path.join(
                view.properties.package_url,
                'tmp', app_id, app_name
            )
        )
        return tmp_url

    def local_file_path(self, uuid, app_name):
        return os.path.join(VFENSE_APP_TMP_PATH, uuid, app_name)

    def get_apps(self, app_id=None, os_code=None, views=None):
        if os_code and views and not app_id:
            apps_info = (
                fetch_apps_data_by_os_code(
                    os_code, views,
                    collection=self.apps_collection
                )
            )

        elif app_id and not os_code and not views:
            apps_info = (
                fetch_app_data(app_id, collection=self.apps_collection)
            )

        return apps_info

    def get_agent_ids(self, os_code, views):
        agent_ids = (
            fetch_agent_ids_in_views(
                views=views, os_code=os_code
            )
        )

        return agent_ids

    def _set_download_status(self, status, file_data=False):
        download_status = None
        if file_data and status == CommonAppKeys.AVAILABLE:
            download_status = PackageCodes.FilePendingDownload

        elif not file_data and status == CommonAppKeys.AVAILABLE:
            download_status = PackageCodes.MissingUri

        elif status == CommonAppKeys.INSTALLED:
            download_status = PackageCodes.FileNotRequired

        return download_status

    def _set_vulnerability_info(self, app):
        """Retrieve the relevant vulnerability for an application if
            it exist. We search by using the kb for Windows and by using the name
            and version for Ubuntu.
        """
        search = RetrieveVulns(app.os_string)
        results = search.by_app_info(app.name, app.version, app.kb)
        vuln_info = results.data

        if vuln_info:
            app.cve_ids = vuln_info.cve_ids
            app.vulnerability_id = vuln_info.vulnerability_id
            for cve_id in app.cve_ids:
                app.vulnerability_categories += (
                    cve.get_vulnerability_categories(cve_id)
                )

            app.vulnerability_categories = (
                list(set(app.vulnerability_categories))
            )

    def store_app_in_db(self, app, file_data, views=None):
        """Store the application into the vFense database.
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
        results.fill_in_defaults()
        if isinstance(app, Apps) and isinstance(file_data, list):
            app_invalid_fields = app.get_invalid_fields()
            if not app_invalid_fields:
                object_status, _, _, _ = (
                    insert_app_data(
                        app.to_dict_db_apps(), self.apps_collection
                    )
                )
                self.store_file_data_in_db(file_data)
                if app.status == AppStatuses.AVAILABLE:
                    self.download_app_files(app, file_data)

                if (object_status == DbCodes.Inserted or
                        object_status == DbCodes.Replaced or
                        object_status == DbCodes.Unchanged):
                    msg = 'App %s stored succesfully' % (app.name)
                    results.generic_status_code = (
                        PackageCodes.ObjectCreated
                    )
                    results.vfense_status_code = (
                        PackageCodes.FileUploadedSuccessfully
                    )
                    results.message = msg
                    results.data = [app.to_dict_apps()]

                else:
                    msg = 'Failed to add app %s' % (app.name)
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

    @job('incoming_updates', connection=redis_pool(), timeout=3600)
    def add_app_to_agents(self, app, now=None, delete_afterwards=False):
        updated = 0
        inserted = 0
        deleted = 0
        if isinstance(app, Apps):
            invalid_keys = app.get_invalid_fields()
            if not invalid_keys:
                agent_ids = self.get_agent_ids(app.os_code, app.views)
                if agent_ids:
                    for agent_id in agent_ids:
                        counts = (
                            self.add_apps_to_agent(
                                agent_id, [app], delete_afterwards=False
                            )
                        )
                        inserted = inserted + counts[0]
                        updated = updated + counts[1]
                        deleted = deleted + counts[2]

        return inserted, updated, deleted

    @job('incoming_updates', connection=redis_pool(), timeout=3600)
    def add_apps_to_agent(self, agent_id, app_list, now=None,
                          delete_afterwards=True):

        updated = 0
        inserted = 0
        deleted = 0
        apps_to_insert = []
        if isinstance(app_list, list):
            for app in app_list:
                if not now:
                    now = time()

                if isinstance(app, Apps):
                    app.last_modified_time = now
                    app.agent_id = agent_id
                    app.fill_in_app_per_agent_defaults()
                    apps_to_insert.append(app.to_dict_db_apps_per_agent())

        if apps_to_insert:
            status_code, count, _, _ = (
                insert_data_in_table(
                    apps_to_insert, self.apps_per_agent_collection
                )
            )

            if isinstance(count, list):
                if len(count) > 1:
                    inserted = count[0]
                    updated = count[1]

            else:
                if status_code == DbCodes.Replaced:
                    updated = count
                elif status_code == DbCodes.Inserted:
                    inserted = count

            if delete_afterwards:
                status_code, deleted_count, _, _ = (
                    delete_apps_per_agent_older_than(
                        agent_id, now, self.apps_per_agent_collection
                    )
                )

                deleted = deleted_count

        return inserted, updated, deleted

    def store_file_data_in_db(self, file_data):
        """Store the uploaded application into the vFense database.
        Args:
            file_data (list): List of Files instances that contains all the
                file related data.
        """
        data_stored = False
        if isinstance(file_data, list):
            data_to_insert = []
            for data in file_data:
                if isinstance(data, Files):
                    if not data.get_invalid_fields():
                        data_to_insert.append(data)

            if data_to_insert:
                data_stored = add_file_data(file_data)

        return data_stored

    def download_app_files(self, app, file_data):
        download_all_files_in_app.delay(
            app, file_data, 0, self.apps_collection
        )

@job('incoming_updates', connection=redis_pool(), timeout=3600)
def incoming_applications_from_agent(agent_id, apps, delete_afterwards=True):
    manager = AppsManager()
    apps_data = []
    now = time()
    agent = AgentManager(agent_id).properties
    if isinstance(apps, list):
        for app in apps:
            files_data = []
            files = app.pop(DbCommonAppKeys.FileData, None)
            app_data = Apps(**app)
            app_data.fill_in_defaults()
            app_data.views = agent.views
            app_data.os_code = agent.os_code
            app_data.os_string = agent.os_string
            app_data.agent_id = agent_id
            if isinstance(files, list):
                for file_data in files:
                    fd = Files(**file_data)
                    fd.fill_in_defaults()
                    fd.download_url = str(fd.download_url)
                    fd.agent_ids.append(agent_id)
                    fd.app_ids.append(app_data.app_id)
                    files_data.append(fd)

            apps_data.append(app_data)
            manager._set_vulnerability_info(app_data)
            manager.store_app_in_db(app_data, files_data)

        manager.add_apps_to_agent(agent_id, apps_data, now, delete_afterwards)
