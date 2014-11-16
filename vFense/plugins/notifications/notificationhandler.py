import logging
import logging.config
from vFense._constants import VFENSE_LOGGING_CONFIG
from vFense.db.client import db_create_close, r
from vFense.core.operations.status_codes import AgentOperationCodes
from vFense.core.operations._db_model import *
from vFense.notifications import *
from vFense.server.hierarchy import Collection, GroupKey, UserKey, ViewKey

logging.config.fileConfig(VFENSE_LOGGING_CONFIG)
logger = logging.getLogger('vfense_api')


def translate_opercodes_to_notif_threshold(oper_codes):
    threshold = None
    if oper_codes == AgentOperationCodes.ResultsCompleted:
        threshold = 'pass'
    elif oper_codes == AgentOperationCodes.ResultsCompletedFailed:
        threshold = 'fail'
    elif oper_codes == AgentOperationCodes.ResultsCompletedWithErrors:
        threshold = 'fail'

    return(threshold)


def notification_rule_exists(
        notif_handler, oper_plugin,
        oper_type, threshold
        ):

    notif_rules = []
    if threshold:
        if oper_plugin == RV_PLUGIN:
            if oper_type == INSTALL:
                notif_rules = notif_handler.rule_exist_for_install(threshold)

            elif oper_type == UNINSTALL:
                notif_rules = notif_handler.rule_exist_for_uninstall(threshold)

        elif oper_plugin == CORE_PLUGIN:
            if oper_type == REBOOT:
                notif_rules = notif_handler.rule_exist_for_reboot(threshold)

            elif oper_type == SHUTDOWN:
                notif_rules = notif_handler.rule_exist_for_shutdown(threshold)

    return(notif_rules)


class RvNotificationHandler():
    def __init__(self, view_name, operation_id, agent_id):

        self.agent_id = agent_id
        self.operation_id = operation_id
        self.view_name = view_name

    def rule_exist_for_install(self, threshold):
        return(
            self.rule_exist_for_rv_plugin(threshold)
        )

    def rule_exist_for_uninstall(self, threshold):
        return(
            self.rule_exist_for_rv_plugin(threshold)
        )

    def rule_exist_for_reboot(self, threshold):
        return(
            self.rule_exist_for_rv_plugin(
                threshold,
                NotificationIndexes.RebootThresholdAndView
            )
        )

    def rule_exist_for_shutdown(self, threshold):
        return(
            self.rule_exist_for_rv_plugin(
                threshold,
                NotificationIndexes.ShutdownThresholdAndView
            )
        )

    @db_create_close
    def rule_exist_for_rv_plugin(self, threshold,
                                 index_to_use=NotificationIndexes.AppThresholdAndView,
                                 conn=None):
        try:
            rules_exist = list(
                r
                .table(NotificationCollections.Notifications)
                .get_all(
                    [threshold, self.view_name],
                    index=index_to_use
                )
                .run(conn)
            )
        except Exception as e:
            logger.exception(e)

        return(rules_exist)

    @db_create_close
    def get_sending_emails(self, notif_rules, conn=None):
        try:
            email_sender_list = []
            for notif in notif_rules:
                if notif[NotificationKeys.Group]:
                    users_list = (
                        r
                        .table(Collection.Groups)
                        .filter({'name': notif['group']})
                        .filter(
                                lambda x: x['view']['name'] ==
                                notif['view_name']
                            )
                            .map(lambda x: x['users'])
                            .run(conn)
                    )
                    if users_list:
                        users = map(lambda x: x['name'], user_list[0])
                        email_sender_list += (
                            r
                            .expr(users)
                            .map(lambda user: r.table('users').get(user))
                            .map(lambda x: x['email'])
                            .run(conn)
                        )

                elif notif[NotificationKeys.User]:
                    email = (
                        r
                        .table(Collection.Users)
                        .get(notif[NotificationKeys.User])
                        .pluck(UserKey.Email)
                        .run(conn)
                    )
                    if email:
                        email_sender_list.append(email[UserKey.Email])

        except Exception as e:
            logger.exception(e)

        return(email_sender_list)
