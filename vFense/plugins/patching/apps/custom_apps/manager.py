import logging

from vFense import VFENSE_LOGGING_CONFIG
from vFense.core.agent._db_model import *
from vFense.db.client import r
from vFense.plugins.patching import AppsPerAgent, Files
from vFense.plugins.patching._db_model import *
from vFense.plugins.patching._constants import CommonAppKeys
from vFense.core.agent._db import(
    fetch_agent, fetch_agent_ids_in_views
)
from vFense.core.tag._db_model import *
from vFense.plugins.patching._db_files import fetch_file_data
from vFense.plugins.patching.file_data import add_file_data

from vFense.plugins.patching._db import fetch_app_data, \
    fetch_apps_data_by_os_code, insert_app_data


logging.config.fileConfig(VFENSE_LOGGING_CONFIG)
logger = logging.getLogger('rvapi')

class CustomAppsManager(object):
    def __init__(self):
        self.apps_collection = AppCollections.CustomApps
        self.apps_per_agent_collection = AppCollections.CustomAppsPerAgent

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
                    if object_status == DbCodes.Inserted:
                        add_custom_app_to_agents(
                            username, view_name,
                            file_data,
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

    def add_apps_to_agents(self, file_data=None, views=None, agent_id=None,
                           app_id=None):

        if app_id and not agent_id:
            app_info = (
                fetch_app_data(
                app_id, collection=AppCollections.CustomApps
                )
            )

            agent_ids = (
                self.get_agent_ids(app_info[AgentKeys.OsCode], views)
            )

            if len(agent_ids) > 0:
                for agentid in agent_ids:
                    add_file_data(app_id, file_data, agent_id)
                    agent_info_to_insert = (
                        {
                            CustomAppsPerAgentKey.AgentId: agentid,
                            CustomAppsPerAgentKey.AppId: app_id,
                            CustomAppsPerAgentKey.Status: CommonAppKeys.AVAILABLE,
                            CustomAppsPerAgentKey.InstallDate: r.epoch_time(0.0)
                        }
                    )
                    insert_app_data(
                        agent_info_to_insert,
                        collection=AppCollections.CustomAppsPerAgent
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
                    CustomAppsPerAgentKey.AgentId: agent_id,
                    CustomAppsPerAgentKey.AppId: app_id,
                    CustomAppsPerAgentKey.Status: CommonAppKeys.AVAILABLE,
                    CustomAppsPerAgentKey.InstallDate: r.epoch_time(0.0)
                }

                insert_app_data(
                    agent_info_to_insert, collection=AppCollections.CustomAppsPerAgent
                )


    def store_file_data_in_db(self, file_data, app_ids=None, agent_ids=None):
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
                    invalid_fields = data.get_invalid_fields()
                    if not invalid_fields:
                        data.fill_in_defaults()
                        data_to_insert.append(data.to_dict())

            if data_to_insert:
                data_stored = add_file_data(app_id, file_data, agent_id)

        return data_stored


