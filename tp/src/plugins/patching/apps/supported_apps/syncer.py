import logging
import requests

from time import mktime
from datetime import datetime

from vFense.core._db import delete_all_in_table
from vFense.core.agent import *
from vFense.core.agent.agents import get_agents_info, get_agent_info 

from vFense.errorz.status_codes import PackageCodes

from vFense.plugins.patching import *
from vFense.plugins.patching._constants import CommonAppKeys
from vFense.plugins.patching._db import fetch_apps_data_by_os_code, \
    insert_app_data
from vFense.plugins.patching.utils import build_agent_app_id
from vFense.plugins.patching.file_data import add_file_data
from vFense.plugins.patching.downloader.downloader import \
    download_all_files_in_app

from vFense.db.client import db_connect, r, db_create_close
from vFense.server.hierarchy import Collection, CustomerKey

import redis
from rq import Connection, Queue

rq_host = 'localhost'
rq_port = 6379
rq_db = 0
rq_pkg_pool = redis.StrictRedis(host=rq_host, port=rq_port, db=rq_db)

BASE_URL = 'http://updater2.toppatch.com'
GET_AGENT_UPDATES = '/api/new_updater/rvpkglist'
GET_SUPPORTED_UPDATES = '/api/new_updater/pkglist'

logging.config.fileConfig('/opt/TopPatch/conf/logging.config')
logger = logging.getLogger('rvapi')


#class IncomingSupportedOrAgentApps(object):
class IncomingSupportedApps(object):

    #def __init__(self, table=AppCollections.SupportedApps):
    def __init__(self):
        #self.table = table
        #if table == AppCollections.SupportedApps:
        self.current_apps_collection = AppCollections.SupportedApps
        self.current_apps_per_agent_collection = \
            AppCollections.SupportedAppsPerAgent
        self.current_apps_key = SupportedAppsKey
        self.current_apps_per_agent_key = SupportedAppsPerAgentKey
        self.current_apps_per_agent_indexes = SupportedAppsPerAgentIndexes

        #elif table == AppCollections.vFenseApps:
        #    self.CurrentAppsCollection = AppCollections.vFenseApps
        #    self.current_apps_per_agent_collection = AppCollections.vFenseAppsPerAgent
        #    self.CurrentAppsKey = AgentAppsKey
        #    self.CurrentAppsPerAgentKey = AgentAppsPerAgentKey
        #    self.CurrentAppsPerAgentIndexes = AgentAppsPerAgentIndexes

        last_modified_time = mktime(datetime.now().timetuple())
        self.last_modified_time = r.epoch_time(last_modified_time)

    def sync_supported_updates_to_all_agents(self, apps):
        try:
            conn = db_connect()
            deleted_count = 0
            (
                r
                .table(self.current_apps_per_agent_collection)
                .delete()
                .run(conn)
            )
            conn.close()
            self.update_agents_with_supported(apps)

        except Exception as e:
            logger.exception(e)

    def update_agents_with_supported(self, apps, agents=None):
        try:
            conn = db_connect()
            if agents:
                for agent in agents:
                    (
                        r
                        .table(self.current_apps_per_agent_collection)
                        .get_all(
                            agent[self.current_apps_per_agent_key.AgentId],
                            index=self.current_apps_per_agent_indexes.AgentId
                        )
                        .delete()
                        .run(conn)
                    )
            for app in apps:
                if not agents:
                    agents = get_agents_info(agent_os=app[AgentKey.OsCode])

                file_data = app.get(self.current_apps_key.FileData)
                if agents:
                    for agent in agents:
                        if agent[AgentKey.OsCode] == app[AgentKey.OsCode]:
                            agent[self.current_apps_per_agent_key.AppId] = \
                                app[self.current_apps_per_agent_key.AppId]

                            add_file_data(
                                agent[self.current_apps_per_agent_key.AppId],
                                file_data,
                                agent[self.current_apps_per_agent_key.AgentId],
                            )

                            app_per_agent_props = \
                                self._set_app_per_agent_properties(**agent)
                            agent_has_app = self.check_if_agent_has_app(agent)

                            if not agent_has_app:
                                self.insert_app(
                                    app_per_agent_props
                                )
                            elif agent_has_app:
                                app_per_agent_props[
                                    self.current_apps_per_agent_key.Status
                                ] = CommonAppKeys.INSTALLED

                                self.insert_app(app_per_agent_props)

            conn.close()

        except Exception as e:
            logger.exception(e)

    @db_create_close
    def insert_app(self, app, conn=None):
        try:
            (
                r
                .table(self.current_apps_per_agent_collection)
                .insert(app)
                .run(conn)
            )

        except Exception as e:
            logger.exception(e)

    @db_create_close
    def insert_app_and_delete_old(self, app, lower_apps, conn=None):
        try:
            (
                r
                .table(self.current_apps_per_agent_collection)
                .insert(app)
                .run(conn)
            )
            for lower_app in lower_apps:
                (
                    r
                    .table(AppCollections.AppsPerAgent)
                    .get(lower_app[AppsPerAgentKey.Id])
                    .delete()
                    .run(conn)
                )
        except Exception as e:
            logger.exception(e)

    def _set_app_per_agent_properties(self, **kwargs):
        return(
            {
                self.current_apps_per_agent_key.AgentId:
                kwargs[AgentKey.AgentId],

                self.current_apps_per_agent_key.CustomerName:
                kwargs[AgentKey.CustomerName],

                self.current_apps_per_agent_key.Status: CommonAppKeys.AVAILABLE,

                self.current_apps_per_agent_key.LastModifiedTime:
                self.last_modified_time,

                self.current_apps_per_agent_key.Update:
                PackageCodes.ThisIsAnUpdate,

                self.current_apps_per_agent_key.InstallDate: r.epoch_time(0.0),

                self.current_apps_per_agent_key.AppId:
                kwargs[self.current_apps_per_agent_key.AppId],

                self.current_apps_per_agent_key.Id:
                build_agent_app_id(
                    kwargs[self.current_apps_per_agent_key.AgentId],
                    kwargs[self.current_apps_per_agent_key.AppId]
                )
            }
        )

    @db_create_close
    def app_name_exist(self, app_info,conn=None):
        try:
            app_name_exists= list(
                r
                .table(AppCollections.UniqueApplications)
                .get_all(
                    app_info[AppsKey.Name],
                    index=AppsIndexes.Name
                )
                .run(conn)
                .pluck(
                    self.current_apps_key.AppId,
                    self.current_apps_key.Name,
                    self.current_apps_key.Version,
                    self.current_apps_per_agent_key.AgentId
                )
                .run(conn)
            )
        except Exception as e:
            logger.exception(e)
            app_name_exists = None

        return(app_name_exists)

    @db_create_close
    def lower_version_exists_of_app(self, app, app_info,
                                    status=CommonAppKeys.AVAILABLE, conn=None):
        try:
            lower_version_exists = list(
                r
                .table(AppCollections.UniqueApplications)
                .get_all(
                    app_info[AppsKey.Name],
                    index=AppsIndexes.Name
                )
                .filter(
                    lambda x: x[AppsKey.Version] < app_info[AppsKey.Version]
                )
                .eq_join(
                    lambda y:
                    [
                        app[AgentKey.AgentId],
                        app[AppsPerAgentKey.AppId],
                    ],
                    r.table(AppCollections.AppsPerAgent),
                    index=AppsPerAgentIndexes.AgentId
                )
                .zip()
                .filter(
                    {
                        AppsPerAgentKey.Status: status
                    }
                )
                .pluck(
                    AppsKey.AppId,
                    AppsPerAgentKey.Id,
                    AppsKey.Name,
                    AppsPerAgentKey.AgentId
                )
                .run(conn)
            )

        except Exception as e:
            logger.exception(e)

        return(lower_version_exists)

    @db_create_close
    def check_if_agent_has_app(self, app, conn=None):
        try:
            agent_has_app = list(
                r
                .table(AppCollections.AppsPerAgent)
                .get_all(
                    [
                        app[AppsPerAgentKey.AgentId],
                        app[AppsPerAgentKey.AppId],
                    ],
                    index=AppsPerAgentIndexes.AgentIdAndAppId
                )
                .run(conn)
            )

        except Exception as e:
            logger.exception(e)

        return(agent_has_app)


#def update_supported_and_agent_apps(json_data,
#        table=AppCollections.SupportedApps):
def update_supported_apps(json_data):

    #if table == AppCollections.SupportedApps:
    collection = AppCollections.SupportedApps
    current_apps_key = SupportedAppsKey
    latest_download_collection = DownloadCollections.LatestDownloadedSupported
    app_type = 'supported_apps'

    #elif table == AppCollections.vFenseApps:
    #    CurrentAppsKey = AgentAppsKey
    #    LatestDownloadedCollection = DownloadCollections.LatestDownloadedAgent
    #    AppType = 'agent_apps'

    try:
        rv_q = Queue('downloader', connection=rq_pkg_pool)
        conn = db_connect()

        inserted_count = 0
        all_customers = list(
            r
            .table(Collection.Customers)
            .map(lambda x: x[CustomerKey.CustomerName])
            .run(conn)
        )

        for i in range(len(json_data)):
            json_data[i][current_apps_key.Customers] = all_customers
            json_data[i][current_apps_key.ReleaseDate] = \
                r.epoch_time(json_data[i][current_apps_key.ReleaseDate])
            json_data[i][current_apps_key.FilesDownloadStatus] = \
                PackageCodes.FilePendingDownload
            json_data[i][current_apps_key.Hidden] = 'no'

            insert_app_data(json_data[i], latest_download_collection)
            file_data = json_data[i].get(current_apps_key.FileData)
            add_file_data(json_data[i][current_apps_key.AppId], file_data)
            data_to_update = {
                current_apps_key.Customers: all_customers
            }
            exists = (
                r
                .table(collection)
                .get(json_data[i][current_apps_key.AppId])
                .run(conn)
            )

            if exists:
                updated = (
                    r
                    .table(collection)
                    .get(json_data[i][current_apps_key.AppId])
                    .update(data_to_update)
                    .run(conn)
                )

            else:
                updated = (
                    r
                    .table(collection)
                    .insert(json_data[i])
                    .run(conn)
                )

            rv_q.enqueue_call(
                func=download_all_files_in_app,
                args=(
                    json_data[i][current_apps_key.AppId],
                    json_data[i][current_apps_key.OsCode],
                    None,
                    file_data,
                    0,
                    app_type
                ),
                timeout=86400
            )

            inserted_count += updated['inserted']

        conn.close()

        #update_apps = IncomingSupportedOrAgentApps(table=table)
        update_apps = IncomingSupportedApps()
        update_apps.sync_supported_updates_to_all_agents(json_data)

    except Exception as e:
        logger.exception(e)


#def get_agents_apps():
#    delete_all_in_table(table=DownloadCollections.LatestDownloadedAgent)
#    get_updater_data = requests.get(BASE_URL + GET_AGENT_UPDATES)
#    if get_updater_data.status_code == 200:
#        json_data = get_updater_data.json()
#        update_supported_and_agent_apps(json_data, AppCollections.vFenseApps)
#    else:
#        logger.error(
#            'Failed to connect and download packages from TopPatch Updater server'
#        )


def get_supported_apps():
    delete_all_in_table(
        collection=DownloadCollections.LatestDownloadedSupported
    )
    get_updater_data = requests.get(BASE_URL + GET_SUPPORTED_UPDATES)

    if get_updater_data.status_code == 200:
        json_data = get_updater_data.json()
        #update_supported_and_agent_apps(json_data, AppCollections.SupportedApps)
        update_supported_apps(json_data)

    else:
        logger.error(
            'Failed to connect and download packages from TopPatch Updater server'
        )


def get_all_supported_apps_for_agent(agent_id):
    agent = get_agent_info(agent_id)
    apps = fetch_apps_data_by_os_code(
        agent[AgentKey.OsCode],
        collection=DownloadCollections.LatestDownloadedSupported
    )
    if apps:
        #update_apps = IncomingSupportedOrAgentApps(
        #    table=AppCollections.SupportedApps
        #)
        update_apps = IncomingSupportedApps(
            collection=AppCollections.SupportedApps
        )
        update_apps.update_agents_with_supported(apps, [agent])


#def get_all_vFense_apps_for_agent(agent_id):
#    agent = get_agent_info(agent_id)
#    apps = fetch_apps_data_by_os_code(
#        agent[AgentKey.OsCode], table=DownloadCollections.LatestDownloadedAgent
#    )
#
#    if apps:
#        update_apps = IncomingSupportedOrAgentApps(
#            table=AppCollections.vFenseApps
#        )
#        update_apps.update_agents_with_supported(apps, [agent])
