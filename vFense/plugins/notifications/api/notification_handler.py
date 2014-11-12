import simplejson as json

from vFense.core.api.base import BaseHandler
from vFense.core.decorators import (
    authenticated_request, convert_json_to_arguments, results_message,
    api_catch_it
)
#from vFense.notifications.search_alerts import AlertSearcher
from vFense.plugins.notifications.notification_manager import (
    NotificationManager, get_valid_fields
)
from vFense.core.api._constants import ApiArguments
from vFense.core.permissions._constants import Permissions
from vFense.core.operations._admin_constants import AdminActions
from vFense.core.operations._constants import vFenseObjects
from vFense.core.operations.decorators import log_operation
from vFense.core.permissions.decorators import check_permissions
from vFense.core.results import ApiResults

from vFense.core.user import UserKeys
from vFense.core.user.manager import UserManager
from vFense.core.status_codes import GenericCodes
from vFense.plugins.notifications import Notification
from vFense.plugins.notifications._db import fetch_all_notifications


class GetAllValidFieldsForNotifications(BaseHandler):
    @api_catch_it
    @authenticated_request
    def get(self):
        output = self.get_argument(ApiArguments.OUTPUT, 'json')
        username = self.get_current_user().encode('utf-8')
        view_name = UserManager(username).properties.current_view
        results = self.get_fields(view_name)
        self.set_status(results.http_status_code)
        self.modified_output(results, output, 'agents')

    @results_message
    @check_permissions(Permissions.READ)
    def get_fields(self, view_name):
        results = get_valid_fields(view_name=view_name)
        return results


class NotificationsHandler(BaseHandler):
    @api_catch_it
    @authenticated_request
    def get(self):
        output = self.get_argument(ApiArguments.OUTPUT, 'json')
        username = self.get_current_user().encode('utf-8')
        view_name = UserManager(username).properties.current_view
        results = self.get_all_notifications(view_name)
        self.set_status(results.http_status_code)
        self.modified_output(results, output, 'agents')

    @results_message
    @check_permissions(Permissions.READ)
    def get_all_notifications(self, view_name):
        results = ApiResults()
        results.fill_in_defaults()
        results.data = fetch_all_notifications(view_name)
        results.generic_status_code = GenericCodes.InformationRetrieved
        results.vfense_status_code = GenericCodes.InformationRetrieved
        return results


    @convert_json_to_arguments
    @authenticated_request
    def post(self):
        username = self.get_current_user().encode('utf-8')
        view_name = UserManager(username).properties.current_view
        rule = Notification()
        rule.fill_in_defaults()
        rule.notification_type = self.arguments.get('operation_type')
        rule.rule_name = self.arguments.get('rule_name')
        rule.rule_description = self.arguments.get('rule_description')
        rule.created_by = username
        rule.modified_by = username
        rule.plugin = self.arguments.get('plugin', 'rv')
        rule.agents = self.arguments.get('agent_ids', [])
        rule.tags = self.arguments.get('tag_ids', [])
        rule.user = self.arguments.get('user', None)
        rule.group =  self.arguments.get('group', None)
        rule.all_agents = self.arguments.get('all_agents', 'true')
        rule.threshold = self.arguments.get('threshold', None)
        rule.file_system = self.arguments.get('file_system', [])
        manager = NotificationManager(view_name)
        results = self.create_rule(manager, rule)
        self.set_status(results.http_status_code)
        self.set_header('Content-Type', 'application/json')
        self.write(json.dumps(results.to_dict_non_null(), indent=4))

    @results_message
    @log_operation(AdminActions.CREATE_NOTIFICATION, vFenseObjects.USER)
    @check_permissions(Permissions.CREATE_NOTIFICATION)
    def create_rule(self, manager, rule):
        results = manager.create(rule)
        return results


class NotificationHandler(BaseHandler):
    @authenticated_request
    def get(self, notification_id):
        username = self.get_current_user().encode('utf-8')
        view_name = (
            UserManager(username).get_attribute(UserKeys.CurrentView)
        )
        uri = self.request.uri
        method = self.request.method
        try:
            alert = AlertSearcher(username, view_name, uri, method)
            results = alert.get_notification(notification_id)
            self.set_status(results['http_status'])
            self.set_header('Content-Type', 'application/json')
            self.write(json.dumps(results, indent=4))

        except Exception as e:
            results = (
                Results(
                    username, uri, method
                ).something_broke(notification_id, 'notifications', e)
            )
            logger.exception(e)
            self.set_status(results['http_status'])
            self.set_header('Content-Type', 'application/json')
            self.write(json.dumps(results, indent=4))


    @authenticated_request
    def delete(self, notification_id):
        username = self.get_current_user().encode('utf-8')
        view_name = (
            UserManager(username).get_attribute(UserKeys.CurrentView)
        )
        uri = self.request.uri
        method = self.request.method
        try:
            notification = (
                Notifier(
                    username, view_name,
                    uri, method
                )
            )

            results = (
                notification.delete_alerting_rule(notification_id)
            )
            self.set_status(results['http_status'])
            self.set_header('Content-Type', 'application/json')
            self.write(json.dumps(results, indent=4))

        except Exception as e:
            results = (
                Results(
                    username, uri, method
                ).something_broke('delete notification', 'notifications', e)
            )
            logger.exception(e)
            self.set_status(results['http_status'])
            self.set_header('Content-Type', 'application/json')
            self.write(json.dumps(results, indent=4))


    @convert_json_to_arguments
    @authenticated_request
    def put(self, notification_id):
        username = self.get_current_user().encode('utf-8')
        view_name = (
            UserManager(username).get_attribute(UserKeys.CurrentView)
        )
        uri = self.request.uri
        method = self.request.method
        try:
            plugin = self.arguments.get('plugin', 'rv')
            rule_name = self.arguments.get('rule_name')
            rule_description = self.arguments.get('rule_description')
            agent_ids = self.arguments.get('agent_ids', [])
            tag_ids = self.arguments.get('tag_ids', [])
            user = self.arguments.get('user', None)
            group = self.arguments.get('group', None)
            all_agents = self.arguments.get('all_agents', 'true')
            rv_threshold = self.arguments.get('rv_threshold', None)
            operation_type = self.arguments.get('operation_type')
            monitoring_threshold = (
                self.arguments.get('monitoring_threshold', None)
            )
            file_systems = self.arguments.get('file_system', [])
            notification = (
                Notifier(
                    username, view_name,
                    uri, method
                )
            )
            data = (
                {
                    NotificationKeys.NotificationId: notification_id,
                    NotificationKeys.NotificationType: operation_type,
                    NotificationKeys.RuleName: rule_name,
                    NotificationKeys.RuleDescription: rule_description,
                    NotificationKeys.CreatedBy: username,
                    NotificationKeys.ModifiedBy: username,
                    NotificationKeys.Plugin: plugin,
                    NotificationKeys.User: user,
                    NotificationKeys.Group: group,
                    NotificationKeys.AllAgents: all_agents,
                    NotificationKeys.Agents: agent_ids,
                    NotificationKeys.Tags: tag_ids,
                    NotificationKeys.ViewName: view_name,
                    NotificationKeys.AppThreshold: None,
                    NotificationKeys.RebootThreshold: None,
                    NotificationKeys.ShutdownThreshold: None,
                    NotificationKeys.CpuThreshold: None,
                    NotificationKeys.MemThreshold: None,
                    NotificationKeys.FileSystemThreshold: None,
                    NotificationKeys.FileSystem: file_systems,
                }
            )
            if rv_threshold:
                if operation_type == INSTALL:
                    data[NotificationKeys.AppThreshold] = rv_threshold
                    results = notification.modify_alerting_rule(**data)

                elif operation_type == UNINSTALL:
                    data[NotificationKeys.AppThreshold] = rv_threshold
                    results = notification.modify_alerting_rule(**data)

                elif operation_type == REBOOT:
                    data[NotificationKeys.RebootThreshold] = rv_threshold
                    results = notification.modify_alerting_rule(**data)

                elif operation_type == SHUTDOWN:
                    data[NotificationKeys.ShutdownThreshold] = rv_threshold
                    results = notification.modify_alerting_rule(**data)

                else:
                    results = (
                        NotificationResults(
                            username, uri, method
                        ).invalid_notification_type(operation_type)
                    )

            elif monitoring_threshold:
                if operation_type == CPU:
                    data[NotificationKeys.CpuThreshold] = monitoring_threshold
                    results = notification.modify_alerting_rule(**data)

                elif operation_type == MEM:
                    data[NotificationKeys.MemThreshold] = monitoring_threshold
                    results = notification.modify_alerting_rule(**data)

                elif operation_type == FS and file_systems:
                    data[NotificationKeys.FileSystemThreshold] = monitoring_threshold
                    data[NotificationKeys.FileSystem] = file_systems
                    results = notification.modify_alerting_rule(**data)

                else:
                    results = (
                        NotificationResults(
                            username, uri, method
                        ).invalid_notification_type(operation_type)
                    )

            else:
                results = (
                    Results(
                        username, uri, method
                    ).incorrect_arguments()
                )

            self.set_status(results['http_status'])
            self.set_header('Content-Type', 'application/json')
            self.write(json.dumps(results, indent=4))

        except Exception as e:
            results = (
                Results(
                    username, uri, method
                ).something_broke('create notification', 'notifications', e)
            )
            logger.exception(e)
            self.set_status(results['http_status'])
            self.set_header('Content-Type', 'application/json')
            self.write(json.dumps(results, indent=4))
