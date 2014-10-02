import re
from vFense.core.operations._constants import vFensePlugins

VALID_NOTIFICATION_PLUGINS = (
    vFensePlugins.RV_PLUGIN, vFensePlugins.MONITORING_PLUGIN
)
INSTALL = 'install'
UNINSTALL = 'uninstall'
REBOOT = 'reboot'
SHUTDOWN = 'shutdown'
PASS = 'pass'
FAIL = 'fail'
CPU = 'cpu'
MEM = 'mem'
FS = 'filesystem'

VALID_RV_NOTIFICATIONS = (INSTALL, UNINSTALL, REBOOT, SHUTDOWN)
VALID_MONITORING_NOTIFICATIONS = (CPU, MEM, FS)
VALID_NOTIFICATIONS = VALID_RV_NOTIFICATIONS + VALID_MONITORING_NOTIFICATIONS
VALID_STATUSES_TO_ALERT_ON = (PASS, FAIL)


def return_notif_type_from_operation(oper_type):
    if re.search(r'^install', oper_type):
            oper_type = INSTALL

    elif re.search(r'^uninstall', oper_type):
        oper_type = UNINSTALL

    elif oper_type == REBOOT:
        oper_type = REBOOT

    elif oper_type == SHUTDOWN:
        oper_type = SHUTDOWN

    return(oper_type)

class NotifDefaults():
    @staticmethod
    def tags():
        return list()

    @staticmethod
    def agents():
        return list()

    @staticmethod
    def all_agents():
        return False

    @staticmethod
    def user():
        return None

    @staticmethod
    def group():
        return None

    @staticmethod
    def file_system():
        return None
