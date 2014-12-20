import simplejson as json

from vFense.core._constants import DefaultQueryValues
from vFense.core.api._constants import (
    ApiArguments, AgentApiArguments, ApiValues, TagApiArguments
)
from vFense.core.agent._db_model import AgentKeys
from vFense.core.agent.agents import (
    get_supported_os_codes, get_supported_os_strings, get_environments
)
from vFense.core.agent.manager import AgentManager
from vFense.core.agent.operations.store_agent_operations import (
    StoreAgentOperations
)
from vFense.core.agent.scheduler.manager import AgentJobManager
from vFense.core.agent.scheduler.search.search import RetrieveAgentJobs
from vFense.core.agent.search.search import RetrieveAgents
from vFense.core.agent.status_codes import AgentCodes, AgentFailureCodes
from vFense.core.api.base import BaseHandler
from vFense.core.decorators import (
    authenticated_request, convert_json_to_arguments, results_message,
    api_catch_it
)
from vFense.core.operations import AgentOperation
from vFense.core.operations.decorators import log_operation
from vFense.core.operations._admin_constants import AdminActions
from vFense.core.operations._constants import vFenseObjects
from vFense.core.permissions._constants import Permissions
from vFense.core.permissions.decorators import check_permissions
from vFense.core.queue.uris import get_result_uris
from vFense.core.results import ExternalApiResults, ApiResults
from vFense.core.scheduler.api.base import BaseJob
from vFense.core.tag import Tag
from vFense.core.tag.manager import TagManager
from vFense.core.user._db_model import UserKeys
from vFense.core.user.manager import UserManager
from vFense.core.view._db import token_exist_in_current
from vFense.core.view.manager import ViewManager
from vFense.core.view.status_codes import ViewCodes
from vFense.plugins.patching.operations.store_operations import (
    StorePatchingOperation
)



class AgentResultURIs(BaseHandler):
    @api_catch_it
    @authenticated_request
    def get(self, agent_id):
        output = self.get_argument(ApiArguments.OUTPUT, 'json')
        results = self.get_uris(agent_id)
        self.set_status(results.http_status_code)
        self.modified_output(results, output, 'uris')

    @results_message
    @check_permissions(Permissions.READ)
    def get_uris(self, agent_id):
        results = get_result_uris(agent_id)
        results.count = len(results.data)
        return results


class FetchValidEnvironments(BaseHandler):
    @api_catch_it
    @authenticated_request
    def get(self):
        active_user = self.get_current_user().encode('utf-8')
        active_view = UserManager(active_user).properties.current_view
        output = self.get_argument(ApiArguments.OUTPUT, 'json')
        results = self.get_environments(active_view)
        self.set_status(results.http_status_code)
        self.modified_output(results, output, 'environments')

    @results_message
    @check_permissions(Permissions.READ)
    def get_environments(self, active_view):
        results = ExternalApiResults()
        results.fill_in_defaults()
        results.data = get_environments(active_view)
        results.count = len(results.data)
        results.generic_status_code = AgentCodes.InformationRetrieved
        results.vfense_status_code = AgentCodes.InformationRetrieved
        results.http_status_code = 200
        return results


class GenerateUUID(BaseHandler):
    @api_catch_it
    @authenticated_request
    def get(self):
        output = self.get_argument(ApiArguments.OUTPUT, 'json')
        results = self.get_uuid()
        self.set_status(results.http_status_code)
        self.modified_output(results, output, 'environments')

    @results_message
    @check_permissions(Permissions.READ)
    def get_uuid(self):
        results = ExternalApiResults()
        results.fill_in_defaults()
        results.data.append({'uuid': self.gen_uuid()})
        results.count = len(results.data)
        results.generic_status_code = AgentCodes.InformationRetrieved
        results.vfense_status_code = AgentCodes.InformationRetrieved
        results.http_status_code = 200
        return results


class FetchSupportedOperatingSystems(BaseHandler):
    @api_catch_it
    @authenticated_request
    def get(self):
        active_user = self.get_current_user().encode('utf-8')
        active_view = (
            UserManager(active_user).get_attribute(UserKeys.CurrentView)
        )
        os_code = self.get_argument(AgentApiArguments.OS_CODE, None)
        os_string = self.get_argument(AgentApiArguments.OS_STRING, None)
        output = self.get_argument(ApiArguments.OUTPUT, 'json')

        if os_code and not os_string:
            results = self.get_os_codes()

        else:
            results = self.get_os_strings(active_view)

        self.set_status(results.http_status_code)
        self.modified_output(results, output, 'platforms')

    @results_message
    @check_permissions(Permissions.READ)
    def get_os_codes(self):
        results = ExternalApiResults()
        results.fill_in_defaults()
        results.data = get_supported_os_codes()
        results.count = len(results.data)
        results.generic_status_code = AgentCodes.InformationRetrieved
        results.vfense_status_code = AgentCodes.InformationRetrieved
        results.http_status_code = 200
        return results

    @results_message
    @check_permissions(Permissions.READ)
    def get_os_strings(self, active_view):
        results = ExternalApiResults()
        results.fill_in_defaults()
        results.data = get_supported_os_strings(active_view)
        results.count = len(results.data)
        results.generic_status_code = AgentCodes.InformationRetrieved
        results.vfense_status_code = AgentCodes.InformationRetrieved
        results.http_status_code = 200
        return results


class AgentsHandler(BaseHandler):
    @api_catch_it
    @authenticated_request
    def get(self):
        active_user = self.get_current_user()
        user = UserManager(active_user)
        active_view = user.get_attribute(UserKeys.CurrentView)
        count = int(
            self.get_argument(ApiArguments.COUNT, DefaultQueryValues.COUNT)
        )
        offset = int(
            self.get_argument(ApiArguments.OFFSET, DefaultQueryValues.OFFSET)
        )
        query = self.get_argument(ApiArguments.QUERY, None)
        fkey = self.get_argument(ApiArguments.FILTER_KEY, None)
        fval = self.get_argument(ApiArguments.FILTER_VAL, None)
        ip = self.get_argument(AgentApiArguments.IP, None)
        mac = self.get_argument(AgentApiArguments.MAC, None)
        sort = (
            self.get_argument(ApiArguments.SORT, DefaultQueryValues.SORT)
        )
        sort_by = (
            self.get_argument(ApiArguments.SORT_BY, AgentKeys.ComputerName)
        )
        output = self.get_argument(ApiArguments.OUTPUT, 'json')

        search = (
            RetrieveAgents(
                view_name=active_view, count=count, offset=offset,
                sort=sort, sort_key=sort_by
            )
        )
        if not ip and not mac and not query and not fkey and not fval:
            results = self.get_all_agents(search)

        elif query and not ip and not mac and not fkey and not fval:
            results = self.get_all_agents_by_name(search, query)

        elif ip and not mac and not query and not fkey and not fval:
            results = self.get_all_agents_by_ip(search, ip)

        elif mac and not ip and not query and not fkey and not fval:
            results = self.get_all_agents_by_mac(search, mac)

        elif fkey and fval and not ip and not mac and not query:
            results = self.get_all_agents_by_key_val(search, fkey, fval)

        elif query and fkey and fval and not mac and not ip:
            results = (
                self.get_all_agents_by_key_val_and_query(
                    search, fkey, fval, query
                )
            )

        elif ip and fkey and fval and not mac and not query:
            results = (
                self.get_all_agents_by_ip_and_filter(search, ip, fkey, fval)
            )

        elif mac and fkey and fval and not ip and not query:
            results = (
                self.get_all_agents_by_mac_and_filter(search, mac, fkey, fval)
            )

        self.set_status(results.http_status_code)
        self.modified_output(results, output, 'agents')

    @results_message
    @check_permissions(Permissions.READ)
    def get_all_agents(self, search):
        results = search.all()
        return results

    @results_message
    @check_permissions(Permissions.READ)
    def get_all_agents_by_name(self, search, name):
        results = search.by_name(name)
        return results

    @results_message
    @check_permissions(Permissions.READ)
    def get_all_agents_by_ip(self, search, ip):
        results = search.by_ip(ip)
        return results

    @results_message
    @check_permissions(Permissions.READ)
    def get_all_agents_by_mac(self, search, mac):
        results = search.by_mac(mac)
        return results

    @results_message
    @check_permissions(Permissions.READ)
    def get_all_agents_by_key_val(self, search, key, val):
        results = search.by_key_and_val(key, val)
        return results

    @results_message
    @check_permissions(Permissions.READ)
    def get_all_agents_by_key_val_and_query(self, search, key, val, query):
        results = search.by_key_and_val(key, val, query)
        return results

    @results_message
    @check_permissions(Permissions.READ)
    def get_all_agents_by_ip_and_filter(self, search, ip, key, val):
        results = search.by_ip_and_filter(ip, key, val)
        return results

    @results_message
    @check_permissions(Permissions.READ)
    def get_all_agents_by_mac_and_filter(self, search, mac, key, val):
        results = search.by_mac_and_filter(mac, key, val)
        return results

    @api_catch_it
    @authenticated_request
    @convert_json_to_arguments
    def put(self):
        active_user = self.get_current_user()
        user = UserManager(active_user)
        active_view = user.get_attribute(UserKeys.CurrentView)
        agent_ids = self.arguments.get(ApiArguments.AGENT_IDS)
        views = self.arguments.get(ApiArguments.VIEWS)
        action = self.arguments.get(ApiArguments.ACTION, ApiValues.ADD)
        token = self.arguments.get(AgentApiArguments.TOKEN, None)
        if not isinstance(agent_ids, list):
            agent_ids = agent_ids.split()

        if not isinstance(views, list):
            views = views.split()

        if action == ApiValues.ADD:
            results = self.add_agents_to_views(agent_ids, views)

        elif action == ApiValues.DELETE:
            results = self.remove_agents_from_views(agent_ids, views)

        elif token:
            operation = StoreAgentOperations(active_user, active_view)
            results = self.new_token(operation, agent_ids, token)

        else:
            results = ExternalApiResults()
            results.fill_in_defaults()
            results.generic_status_code = AgentCodes.IncorrectArguments
            results.vfense_status_code = AgentCodes.IncorrectArguments
            results.message = 'Incorrect arguments:'
            results.uri = self.request.uri
            results.http_method = self.request.method
            results.username = active_user
            results.http_status_code = 400

        self.set_status(results.http_status_code)
        self.set_header('Content-Type', 'application/json')
        self.write(json.dumps(results.to_dict_non_null(), indent=4))

    @results_message
    @check_permissions(Permissions.ASSIGN_NEW_TOKEN)
    @log_operation(AdminActions.ASSIGN_AGENT_TOKEN, vFenseObjects.AGENT)
    def new_token(self, operation, agents, token):
        for agent in agents:
            manager = AgentManager(agent)
            manager.update_token(token)

        results = operation.new_token(token, agents)
        return results


    @results_message
    @check_permissions(Permissions.ADD_AGENTS_TO_VIEW)
    @log_operation(AdminActions.ADD_VIEWS_TO_AGENTS, vFenseObjects.AGENT)
    def add_agents_to_views(self, agents, views):
        end_results = ApiResults()
        end_results.fill_in_defaults()
        views_added = []
        views_unchanged = []
        for view in views:
            manager = ViewManager(view)
            results = manager.add_to_agents(agents)
            if results.vfense_status_code == ViewCodes.AgentsAddedToView:
                views_added.append(view)
            else:
                views_unchanged.append(view)

        end_results.unchanged_ids = views_unchanged
        end_results.updated_ids = views_added

        if views_added and views_unchanged:
            msg = (
                'Agents: {0} added to views: {1}, Unchanged views: {2}'
                .format(
                    ', '.join(agents),
                    ', '.join(views_added),
                    views_unchanged
                )
            )
            end_results.generic_status_code = (
                AgentFailureCodes.FailedToUpdateAllObjects
            )
            end_results.vfense_status_code = (
                AgentFailureCodes.FailedToAddViewsToAgents
            )
            end_results.message = msg

        elif views_added and not views_unchanged:
            msg = (
                'Agents: {0} added to views: {1}'
                .format(', '.join(agents), ', '.join(views_added))
            )
            end_results.generic_status_code = (
                AgentCodes.ObjectsUpdated
            )
            end_results.vfense_status_code = (
                AgentCodes.UsersDeleted
            )
            end_results.message = msg

        elif views_unchanged and not views_added:
            msg = (
                'Agents: {0} failed to add to views: {1}'
                .format(', '.join(agents), ', '.join(views_unchanged))
            )
            end_results.generic_status_code = (
                AgentCodes.ObjectsUnchanged
            )
            end_results.vfense_status_code = (
                AgentFailureCodes.FailedToAddViewsToAgent
            )
            end_results.message = msg

        return end_results

    @results_message
    @check_permissions(Permissions.REMOVE_AGENTS_FROM_VIEW)
    @log_operation(AdminActions.REMOVE_VIEWS_FROM_AGENTS, vFenseObjects.AGENT)
    def remove_agents_from_views(self, agents, views):
        end_results = ApiResults()
        end_results.fill_in_defaults()
        views_removed = []
        views_unchanged = []
        for view in views:
            manager = ViewManager(view)
            results = manager.remove_agents(agents)
            if (results.vfense_status_code
                    == ViewCodes.AgentsRemovedFromView):
                views_removed.append(view)
            else:
                views_unchanged.append(view)

        end_results.unchanged_ids = views_unchanged
        end_results.updated_ids = views_removed

        if views_removed and views_unchanged:
            msg = (
                'Agents: {0} removed from views: {1}, Unchanged views: {2}'
                .format(
                    ', '.join(agents),
                    ', '.join(views_removed),
                    views_unchanged
                )
            )
            end_results.generic_status_code = (
                AgentFailureCodes.FailedToUpdateAllObjects
            )
            end_results.vfense_status_code = (
                AgentFailureCodes.FailedToRemoveViewsFromAgents
            )
            end_results.message = msg

        elif views_removed and not views_unchanged:
            msg = (
                'Agents: {0} removed from views: {1}'
                .format(', '.join(agents), ', '.join(views_removed))
            )
            end_results.generic_status_code = (
                AgentCodes.ObjectsUpdated
            )
            end_results.vfense_status_code = (
                AgentCodes.ViewsRemovedFromAgents
            )
            end_results.message = msg

        elif views_unchanged and not views_removed:
            msg = (
                'Agents: {0} failed to add to views: {1}'
                .format(', '.join(agents), ', '.join(views_unchanged))
            )
            end_results.generic_status_code = (
                AgentCodes.ObjectsUnchanged
            )
            end_results.vfense_status_code = (
                AgentFailureCodes.FailedToAddViewsToAgent
            )
            end_results.message = msg

        return end_results

    @api_catch_it
    @authenticated_request
    @convert_json_to_arguments
    def delete(self):
        active_user = self.get_current_user()
        active_view = (
            UserManager(active_user).get_attribute(UserKeys.CurrentView)
        )
        agent_ids = self.arguments.get('agent_ids')
        if not isinstance(agent_ids, list):
            agent_ids = agent_ids.split()
        delete_oper = StoreAgentOperations(active_user, active_view)
        results = self.delete_agents(agent_ids, delete_oper)
        self.set_status(results.http_status_code)
        self.set_header('Content-Type', 'application/json')
        self.write(json.dumps(results.to_dict_non_null(), indent=4))

    @results_message
    @check_permissions(Permissions.DELETE_AGENT)
    @log_operation(AdminActions.REMOVE_AGENTS, vFenseObjects.AGENT)
    def delete_agents(self, agents, delete_oper):
        end_results = ApiResults()
        end_results.fill_in_defaults()
        agents_deleted = []
        agents_unchanged = []
        for agent_id in agents:
            manager = AgentManager(agent_id)
            results = manager.remove()
            if results.vfense_status_code == AgentCodes.AgentDeleted:
                agents_deleted.append(agent_id)
                agent_operation = AgentOperation()
                agent_operation.agent_ids = [agent_id]
                delete_oper.uninstall_agent(agent_operation)
            else:
                agents_unchanged.append(agent_id)

        end_results.unchanged_ids = agents_unchanged
        end_results.deleted_ids = agents_deleted

        if agents_deleted and agents_unchanged:
            msg = (
                'Agents: {0} deleted and these agents didnt: {1}'
                .format(
                    ', '.join(agents_deleted),
                    ', '.join(agents_unchanged),
                )
            )
            end_results.generic_status_code = (
                AgentFailureCodes.FailedToDeleteAllObjects
            )
            end_results.vfense_status_code = (
                AgentFailureCodes.FailedToDeleteAgents
            )
            end_results.message = msg

        elif agents_deleted and not agents_unchanged:
            msg = (
                'Agents: {0} deleted.'.format(', '.join(agents))
            )
            end_results.generic_status_code = (
                AgentCodes.ObjectsDeleted
            )
            end_results.vfense_status_code = (
                AgentCodes.AgentsDeleted
            )
            end_results.message = msg

        elif agents_unchanged and not agents_deleted:
            msg = (
                'Agents: {0} failed to delete: {1}'
                .format(', '.join(agents), ', '.join(agents_unchanged))
            )
            end_results.generic_status_code = (
                AgentCodes.ObjectsUnchanged
            )
            end_results.vfense_status_code = (
                AgentFailureCodes.FailedToDeleteAgents
            )
            end_results.message = msg

        return end_results


class AgentHandler(BaseHandler):
    @api_catch_it
    @authenticated_request
    @check_permissions(Permissions.READ)
    def get(self, agent_id):
        active_user = self.get_current_user()
        active_view = (
            UserManager(active_user).get_attribute(UserKeys.CurrentView)
        )
        output = self.get_argument(ApiArguments.OUTPUT, 'json')
        search = (
            RetrieveAgents(view_name=active_view)
        )
        results = self.get_agent_by_id(search, agent_id)
        self.modified_output(results, output, 'agent')

    @results_message
    @check_permissions(Permissions.READ)
    def get_agent_by_id(self, search, agent_id):
        results = search.by_id(agent_id)
        if results.count > 0:
            results.data = results.data.pop()
        return results

    @api_catch_it
    @authenticated_request
    @convert_json_to_arguments
    def put(self, agent_id):
        active_user = self.get_current_user()
        action = self.arguments.get(ApiArguments.ACTION, None)
        displayname = self.arguments.get(AgentApiArguments.DISPLAY_NAME, None)
        environment = self.arguments.get(AgentApiArguments.ENVIRONMENT, None)
        views = self.arguments.get(AgentApiArguments.VIEWS, None)
        manager = AgentManager(agent_id)

        if displayname and not environment and not views and not action:
            results = self.edit_display_name(manager, displayname)

        elif environment and not displayname and not views and not action:
                results = self.edit_environment(manager, environment)

        elif action and views and not environment and not displayname:
            if action == ApiValues.ADD:
                results = self.add_agent_to_views(manager, views)

            elif action == ApiValues.DELETE:
                results = self.remove_agent_from_views(manager, views)

            else:
                results = ExternalApiResults()
                results.fill_in_defaults()
                results.generic_status_code = AgentCodes.IncorrectArguments
                results.vfense_status_code = AgentCodes.IncorrectArguments
                results.message = 'Incorrect arguments:'
                results.uri = self.request.uri
                results.http_method = self.request.method
                results.username = active_user
                results.http_status_code = 400

        self.set_status(results.http_status_code)
        self.set_header('Content-Type', 'application/json')
        self.write(json.dumps(results.to_dict_non_null(), indent=4))

    @results_message
    @check_permissions(Permissions.EDIT_AGENT)
    @log_operation(AdminActions.EDIT_AGENT_DISPLAY_NAME, vFenseObjects.AGENT)
    def edit_display_name(self, manager, display_name):
        results = manager.edit_display_name(display_name)
        return results

    @results_message
    @check_permissions(Permissions.EDIT_AGENT)
    @log_operation(AdminActions.EDIT_AGENT_ENVIRONMENT, vFenseObjects.AGENT)
    def edit_environment(self, manager, environment):
        results = manager.edit_environment(environment)
        return results

    @results_message
    @check_permissions(Permissions.EDIT_AGENT)
    @log_operation(AdminActions.ADD_VIEWS_TO_AGENT, vFenseObjects.AGENT)
    def add_agent_to_views(self, manager, views):
        results = manager.add_to_views(views)
        return results

    @results_message
    @check_permissions(Permissions.EDIT_AGENT)
    @log_operation(AdminActions.REMOVE_VIEWS_FROM_AGENT, vFenseObjects.AGENT)
    def remove_agent_from_views(self, manager, views):
        results = manager.remove_from_views(views)
        return results

    @api_catch_it
    @authenticated_request
    def delete(self, agent_id):
        active_user = self.get_current_user()
        active_view = (
            UserManager(active_user).get_attribute(UserKeys.CurrentView)
        )
        agent = AgentManager(agent_id)
        operation = AgentOperation(agent_ids=[agent_id])
        delete_oper = StoreAgentOperations(active_user, active_view)
        delete_oper.uninstall_agent(operation)
        results = self.remove_agent(agent)
        self.set_status(results.http_status_code)
        self.set_header('Content-Type', 'application/json')
        self.write(json.dumps(results.to_dict_non_null(), indent=4))

    @results_message
    @check_permissions(Permissions.DELETE_AGENT)
    @log_operation(AdminActions.REMOVE_AGENT, vFenseObjects.AGENT)
    def remove_agent(self, manager):
        results = manager.remove()
        return results

    @api_catch_it
    @authenticated_request
    @convert_json_to_arguments
    def post(self, agent_id):
        active_user = self.get_current_user()
        active_view = (
            UserManager(active_user).get_attribute(UserKeys.CurrentView)
        )
        reboot = self.arguments.get(AgentApiArguments.REBOOT, None)
        shutdown = self.arguments.get(AgentApiArguments.SHUTDOWN, None)
        token = self.arguments.get(AgentApiArguments.TOKEN, None)
        refresh_apps = (
            self.arguments.get(AgentApiArguments.REFRESH_APPS, None)
        )
        operation = StoreAgentOperations(active_user, active_view)
        agent_operation = AgentOperation(agent_ids=[agent_id])
        if reboot:
            results = self.reboot(operation, agent_operation)

        elif shutdown:
            results = self.shutdown(operation, agent_operation)

        elif token:
            agent_operation.token = token
            results = self.new_token(operation, agent_operation)

        elif refresh_apps:
            operation = StorePatchingOperation(active_user, active_view)
            results = self.refresh_apps(operation, agent_operation)

        else:
            results = ExternalApiResults()
            results.fill_in_defaults()
            results.generic_status_code = AgentCodes.IncorrectArguments
            results.vfense_status_code = AgentCodes.IncorrectArguments
            results.message = 'Incorrect arguments:'
            results.uri = self.request.uri
            results.http_method = self.request.method
            results.username = active_user
            results.http_status_code = 400

        self.set_status(results.http_status_code)
        self.set_header('Content-Type', 'application/json')
        self.write(json.dumps(results.to_dict_non_null(), indent=4))

    @check_permissions(Permissions.REBOOT)
    @results_message
    def reboot(self, operation, agent_operation):
        results = operation.reboot(agent_operation)
        return results

    @check_permissions(Permissions.SHUTDOWN)
    @results_message
    def shutdown(self, operation, agent_operation):
        results = operation.shutdown(agent_operation)
        return results

    @check_permissions(Permissions.ASSIGN_NEW_TOKEN)
    @results_message
    def new_token(self, operation, agent_operation):
        if token_exist_in_current(agent_operation.token):
            results = operation.new_token(agent_operation)
        else:
            results = ExternalApiResults()
            results.fill_in_defaults()
            msg = 'Invalid token {0}'.format(agent_operation.token)
            results.message = msg
            results.uri = self.request.uri
            results.http_method = self.request.method
            results.username = self.get_current_user()
            results.invalid_ids.append(agent_operation.token)
            results.generic_status_code = AgentFailureCodes.InvalidToken
            results.vfense_status_code = AgentFailureCodes.InvalidToken
            results.http_status_code = 200
        return results

    @results_message
    def refresh_apps(self, operation, agent_operation):
        results = operation.refresh_apps(agent_operation)
        return results


class AgentTagHandler(BaseHandler):
    @api_catch_it
    @authenticated_request
    @check_permissions(Permissions.READ)
    def get(self, agent_id):
        active_user = self.get_current_user()
        active_view = (
            UserManager(active_user).get_attribute(UserKeys.CurrentView)
        )
        name = self.get_argument(ApiArguments.QUERY, None)
        output = self.get_argument(ApiArguments.OUTPUT, 'json')
        search = RetrieveAgents(view_name=active_view)
        if name:
            results = self.search_tags_by_name(search, name)
        else:
            results = self.get_tags_by_agent_id(search, agent_id)

        self.modified_output(results, output, 'agent')

    @results_message
    def get_tags_by_agent_id(self, search, agent_id):
        results = search.by_agent_id(agent_id)
        return results

    @results_message
    def search_tags_by_name(self, search, name):
        results = search.by_name(name)
        return results

    @api_catch_it
    @authenticated_request
    def put(self, agent_id):
        active_user = self.get_current_user()
        active_view = (
            UserManager(active_user).get_attribute(UserKeys.CurrentView)
        )
        tag_ids = self.get_argument(TagApiArguments.TAG_IDS)
        tag_name = self.get_argument(TagApiArguments.TAG_NAME, None)
        action = self.get_argument(ApiArguments.ACTION, ApiValues.ADD)
        manager = AgentManager(agent_id)
        if action == ApiValues.ADD:
            if not tag_name:
                results = self.add_tags(manager, tag_ids)
            else:
                results = self.create_tag(tag_name, agent_id, active_view)
        else:
            results = self.remove_tags(manager, tag_ids)

        self.set_status(results.http_status_code)
        self.set_header('Content-Type', 'application/json')
        self.write(json.dumps(results.to_dict_non_null(), indent=4))


    @results_message
    @check_permissions(Permissions.ADD_AGENTS_TO_TAG)
    def add_tags(self, manager, tag_ids):
        results = manager.add_to_tags(tag_ids)
        return results

    @results_message
    @check_permissions(Permissions.REMOVE_AGENTS_FROM_TAG)
    def remove_tags(self, manager, tag_ids):
        results = manager.remove_from_tags(tag_ids)
        return results

    @results_message
    @check_permissions(Permissions.CREATE_TAG)
    def create_tag(self, tag_name, agent_id, active_view):
        environment = (
            AgentManager(agent_id).get_attribute(AgentKeys.Environment)
        )
        tag = (
            Tag(
                tag_name=tag_name, environment=environment,
                view_name=active_view, agents=[agent_id]
            )
        )
        manager = TagManager()
        results = manager.create(tag)
        return results


class AgentJobsHandler(BaseJob):
    @authenticated_request
    @check_permissions(Permissions.READ)
    def get(self, agent_id):
        self.get_search_arguments()
        search = (
            RetrieveAgentJobs(
                agent_id=agent_id, view_name=self.active_view,
                count=self.count, offset=self.offset, sort=self.sort,
                sort_key=self.sort_by
            )
        )
        results = self.apply_search(search)

        self.set_status(results.http_status_code)
        self.modified_output(results, self.output, 'jobs')


class AgentSchedulerReboot(BaseHandler):
    @api_catch_it
    @authenticated_request
    @convert_json_to_arguments
    @check_permissions(Permissions.REBOOT)
    def post(self, agent_id):
        active_user = self.get_current_user().encode('utf-8')
        active_view = UserManager(active_user).properties.current_view
        sched = self.application.scheduler
        job = AgentJobManager(sched, active_view)
        run_date = self.arguments.get('run_date')
        job_name = self.arguments.get('job_name')
        timezone = self.arguments.get('timezone', None)
        results = (
            job.reboot_once(
                run_date, job_name, user_name=active_user,
                agent_ids=[agent_id], time_zone=timezone
            )
        )
        self.set_status(results.http_status_code)
        self.set_header('Content-Type', 'application/json')
        self.write(json.dumps(results.to_dict_non_null(), indent=4))
