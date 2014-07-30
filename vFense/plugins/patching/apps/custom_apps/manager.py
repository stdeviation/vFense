import os
import logging

from vFense import VFENSE_LOGGING_CONFIG, VFENSE_APP_TMP_PATH
from vFense.plugins.patching import Apps, Files
from vFense.plugins.patching._db_model import (
    AppsKey, AppCollections, DbCommonAppPerAgentKeys, DbCommonAppKeys
)
from vFense.plugins.patching._constants import CommonAppKeys
from vFense.core.agent._db_model import AgentKeys
from vFense.core.agent._db import(
    fetch_agent, fetch_agent_ids_in_views
)
from vFense.core._db_constants import DbTime
from vFense.core.status_codes import DbCodes
from vFense.core.results import ApiResultKeys
from vFense.core.view._db_model import ViewKeys
from vFense.core.view.manager import ViewManager
from vFense.plugins.patching._db_files import fetch_file_data
from vFense.plugins.patching.status_codes import PackageCodes
from vFense.plugins.patching.file_data import add_file_data

from vFense.plugins.patching._db import (
    fetch_app_data, fetch_apps_data_by_os_code, insert_app_data
)


logging.config.fileConfig(VFENSE_LOGGING_CONFIG)
logger = logging.getLogger('rvapi')

class CustomAppsManager(object):
    def __init__(self):
        self.apps_collection = AppCollections.CustomApps
        self.apps_per_agent_collection = AppCollections.DbCommonAppsPerAgent

    def url_path(self, app_id, app_name, view):
        view = ViewManager(view)
        tmp_url = (
            os.path.join(
                view.get_attribute(ViewKeys.PackageUrl),
                app_id, app_name
            )
        )
        return tmp_url

    def url_tmp_path(self, app_id, app_name, view):
        view = ViewManager(view)
        tmp_url = (
            os.path.join(
                view.get_attribute(ViewKeys.PackageUrl),
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
        results = {}
        if isinstance(app, Apps) and isinstance(file_data, list):
            app_invalid_fields = app.get_invalid_fields()
            if not app_invalid_fields:
                app_location = self.local_file_path(app.name, app.app_id)
                app_url = self.url_tmp_path(app.name, app.app_id)
                if os.path.exists(app_location):
                    app.fill_in_defaults()
                    app_data = app.to_dict().copy()
                    app_data[DbCommonAppKeys.ReleaseDate] = (
                        DbTime.epoch_time_to_db_time(app.release_date)
                    )
                    object_status, _, _, _ = (
                        insert_app_data(app_data, self.apps_collection)
                    )
                    self.store_app_in_db(file_data)
                    if object_status == DbCodes.Inserted:
                        msg = 'app %s stored succesfully - ' % (app.name)
                        results[ApiResultKeys.GENERIC_STATUS_CODE] = (
                            PackageCodes.ObjectCreated
                        )
                        results[ApiResultKeys.VFENSE_STATUS_CODE] = (
                            PackageCodes.FileUploadedSuccessfully
                        )
                        results[ApiResultKeys.MESSAGE] = msg
                        results[ApiResultKeys.DATA] = [app.to_dict()]

        return results

    def add_app_to_agent(self, app_id, agent_id, status):
        app_info = (
            fetch_app_data(
                app_id, collection=self.apps_collection,
                fields_to_pluck=[
                    AppsKey.CveIds, AppsKey.VulnerabilityCategories,
                    AppsKey.VulnerabilityId, AppsKey.AppId
                ]
            )
        )

        agent_info = (
            fetch_agent(
                agent_id, keys_to_pluck=[
                    AgentKeys.OsCode, AgentKeys.OsString,
                    AgentKeys.Views, AgentKeys.AgentId
               ]
            )
        )

        if agent_info and app_info:
            data = dict(agent_info.items() + app_info.items())
            data[DbCommonAppPerAgentKeys.Status] = status

            if len(agent_ids) > 0:
                for agentid in agent_ids:
                    add_file_data(app_id, file_data, agent_id)
                    agent_info_to_insert = (
                        {
                            DbCommonAppPerAgentKeys.AgentId: agentid,
                            DbCommonAppPerAgentKeys.AppId: app_id,
                            DbCommonAppPerAgentKeys.Status: CommonAppKeys.AVAILABLE,
                            DbCommonAppPerAgentKeys.InstallDate: r.epoch_time(0.0)
                        }
                    )
                    insert_app_data(
                        agent_info_to_insert,
                        collection=AppCollections.DbCommonAppsPerAgent
                    )

        elif agent_id and not app_id:
            agent_info = fetch_agent(agent_id)
            apps_info = fetch_apps_data_by_os_code(
                agent_info[AgentKeys.OsCode], views,
                collection=AppCollections.CustomApps
            )

            for app_info in apps_info:
                app_id = app_info.get(CustomAppsKey.AppId)
                file_data = fetch_file_data(app_id)
                add_file_data(app_id, file_data, agent_id)

                agent_info_to_insert = {
                    DbCommonAppPerAgentKeys.AgentId: agent_id,
                    DbCommonAppPerAgentKeys.AppId: app_id,
                    DbCommonAppPerAgentKeys.Status: CommonAppKeys.AVAILABLE,
                    DbCommonAppPerAgentKeys.InstallDate: r.epoch_time(0.0)
                }

                insert_app_data(
                    agent_info_to_insert, collection=AppCollections.DbCommonAppsPerAgent
                )


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


