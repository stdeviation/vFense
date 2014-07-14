import re
import logging
import logging.config
from vFense import VFENSE_LOGGING_CONFIG
from time import mktime
from datetime import datetime

from vFense.plugins.patching._db_model import (
    AppCollections, AppsKey
)
from vFense.plugins.patching._constants import CommonAppKeys
from vFense.core.operations._db_model import (
    OperationPerAgentKey, AgentOperationKey
)
from vFense.core.operations._constants import (
    AgentOperations, vFensePlugins
)
from vFense.core.operations.agent_operations import AgentOperation
from vFense.plugins.patching.patching import (
    update_app_status_by_agentid_and_appid
)

from vFense.core.queue._db import get_all_expired_jobs, delete_all_expired_jobs

logging.config.fileConfig(VFENSE_LOGGING_CONFIG)
logger = logging.getLogger('admin_scheduler')

def remove_expired_jobs_and_update_operations():
    epoch_time_now = mktime(datetime.now().timetuple())
    expired_jobs = get_all_expired_jobs(epoch_time_now)
    status_code, count, error, generated_ids = (
        delete_all_expired_jobs(epoch_time_now)
    )
    jobs_deleted = count
    msg = 'number of jobs expired: %s' % (str(jobs_deleted))
    logger.info(msg)
    for job in expired_jobs:
        operation = (
            AgentOperation()
        )

        operation.update_operation_expire_time(
            job[OperationPerAgentKey.OperationId],
            job[OperationPerAgentKey.AgentId],
        )

        if job[AgentOperationKey.Plugin] == vFensePlugins.RV_PLUGIN:
            collection = AppCollections.UniqueApplications

            if re.search('^install', job['operation']):
                app_status = {CommonAppKeys.STATUS:  CommonAppKeys.AVAILABLE}
                if job['operation'] == AgentOperations.INSTALL_CUSTOM_APPS:
                    collection = AppCollections.CustomApps

                if job['operation'] == AgentOperations.INSTALL_SUPPORTED_APPS:
                    collection = AppCollections.SupportedApps

                if job['operation'] == AgentOperations.INSTALL_AGENT_UPDATE:
                    collection = AppCollections.vFenseApps

            elif re.search('^uninstall', job['operation']):
                app_status = {CommonAppKeys.STATUS:  CommonAppKeys.INSTALLED}
            for app in job[AppsKey.FileData]:
                update_app_status_by_agentid_and_appid(
                    job[OperationPerAgentKey.AgentId],
                    collection,
                    app[AppsKey.AppId],
                    app_status
                )
