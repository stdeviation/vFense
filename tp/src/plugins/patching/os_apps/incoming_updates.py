import re
import logging
import logging.config

from vFense.db.client import r
from vFense.errorz.status_codes import PackageCodes
from vFense.core._db_constants import DbTime

from vFense.plugins.patching import AppsKey, AppsPerAgentKey
from vFense.plugins.patching.utils import build_app_id, build_agent_app_id
from vFense.plugins.patching.patching import add_or_update_apps_per_agent, \
    unique_application_updater
from vFense.plugins.patching.downloader.downloader import \
    download_all_files_in_app

import redis
from rq import Connection, Queue

RQ_HOST = 'localhost'
RQ_PORT = 6379
RQ_DB = 0
RQ_PKG_POOL = redis.StrictRedis(host=RQ_HOST, port=RQ_PORT, db=RQ_DB)

logging.config.fileConfig('/opt/TopPatch/conf/logging.config')
logger = logging.getLogger('rvapi')



class IncomingApplications():

    def __init__(self, username, agent_id, customer_name, os_code, os_string):
        self.username = username
        self.agent_id = agent_id
        self.customer_name = customer_name
        self.os_code = os_code
        self.os_string = os_string
        self.inserted_count = 0
        self.updated_count = 0
        self.modified_time = DbTime.time_now()

    def add_or_update_applications(self, app_list, delete_afterwards=True):
        rv_q = Queue('downloader', connection=RQ_PKG_POOL)
        index_with_no_name = list()
        good_app_list = list()
        #start_time = datetime.now()
        #print start_time, 'add all apps to app_table'
        for i in range(len(app_list)):
            if not app_list[i][AppsKey.Name]:
                index_with_no_name.append(i)
                continue

            if len(app_list[i][AppsKey.Name]) < 1:
                index_with_no_name.append(i)
                continue

            app_list[i] = self._set_app_per_node_parameters(app_list[i])
            app_list[i][AppsKey.AppId] = self.build_app_id(app_list[i])
            agent_app = self.set_specific_keys_for_agent_app(app_list[i])
            file_data = app_list[i].get(AppsKey.FileData)
            counts = unique_application_updater(
                self.customer_name, app_list[i], self.os_string
            )
            self.inserted_count += counts[0]
            self.updated_count += counts[1]

            if agent_app[AppsPerAgentKey.Status] == 'available':
                rv_q.enqueue_call(
                    func=download_all_files_in_app,
                    args=(
                        app_list[i][AppsKey.AppId],
                        self.os_code, self.os_string,
                        file_data,
                    ),
                    timeout=86400
                )
            good_app_list.append(agent_app)

        inserted, updated, deleted = (
            add_or_update_apps_per_agent(
                self.agent_id, good_app_list,
                self.modified_time, delete_afterwards
            )
        )
        #end_time = datetime.now()
        #print end_time, 'finished adding  all apps to app_table'
        #print 'total time took %s' % (str(end_time - start_time))
        print (("Added or updated apps per agent: "
               "inserted: {0}, updated: {1}, deleted: {2}")
               .format(inserted, updated, deleted))

        #logger.info(msg)

    def set_specific_keys_for_agent_app(self, app):
        only_these_keys_are_needed = {
            AppsPerAgentKey.AppId: app[AppsPerAgentKey.AppId],
            AppsPerAgentKey.AgentId: app[AppsPerAgentKey.AgentId],
            AppsPerAgentKey.InstallDate: app.pop(AppsPerAgentKey.InstallDate),
            AppsPerAgentKey.AgentId: self.agent_id,
            AppsPerAgentKey.CustomerName: self.customer_name,
            AppsPerAgentKey.Status: app[AppsPerAgentKey.Status],
            AppsPerAgentKey.Dependencies: app.pop(AppsPerAgentKey.Dependencies),
            AppsPerAgentKey.Update: PackageCodes.ThisIsAnUpdate,
            AppsPerAgentKey.LastModifiedTime: self.modified_time,
            AppsPerAgentKey.Id: self.build_agent_app_id(
                app[AppsPerAgentKey.AppId]
            )
        }

        return(only_these_keys_are_needed)

    def _set_app_per_node_parameters(self, app):
        app[AppsPerAgentKey.AgentId] = self.agent_id
        app[AppsKey.OsCode] = self.os_code
        app[AppsKey.RvSeverity] = (
            self.sev_generator(
                app[AppsKey.VendorSeverity]
            )
        )

        app[AppsKey.ReleaseDate] = (
            r.epoch_time(app[AppsKey.ReleaseDate])
        )

        app[AppsPerAgentKey.InstallDate] = (
            r.epoch_time(app[AppsPerAgentKey.InstallDate])
        )

        return(app)

    def sev_generator(self, sev):

        tp_sev = ''
        if re.search(r'Critical|Important|Security', sev, re.IGNORECASE):
            tp_sev = 'Critical'

        elif re.search(r'Recommended|Moderate|Low|Bugfix', sev, re.IGNORECASE):
            tp_sev = 'Recommended'

        else:
            tp_sev = 'Optional'

        return (tp_sev)


def incoming_applications_from_agent(username, agent_id, customer_name,
        os_code, os_string, apps, delete_afterwards=True):

        app = IncomingApplications(
            username, agent_id, customer_name, os_code, os_string
        )
        app.add_or_update_applications(apps, delete_afterwards)
