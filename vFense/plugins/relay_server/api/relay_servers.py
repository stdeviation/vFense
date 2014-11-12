from vFense.core.api.base import BaseHandler
from vFense.core.decorators import (
    authenticated_request, convert_json_to_arguments, results_message,
    api_catch_it
)
from vFense.core.results import ApiResults

from vFense.core.permissions.decorators import check_permissions
from vFense.core.permissions._constants import Permissions
from vFense.core.view._constants import DefaultViews
from vFense.plugins.relay_server import RelayServer
from vFense.plugins.relay_server.manager import (
    RelayServerManager, get_all_relay_server, get_relay_server
)
from vFense.plugins.relay_server.status_codes import (
    RelayServerCodes, RelayServerFailureCodes
)

from vFense.core.user.manager import UserManager

class RelayServersHandler(BaseHandler):
    @api_catch_it
    @authenticated_request
    def get(self):
        username = self.get_current_user()
        active_view = UserManager(username).properties.current_view
        view_name = self.arguments.get('view_name', None)
        output = self.arguments.get('output', 'json')
        results = self.get_relays(active_view, view_name)
        self.set_status(results.http_status_code)
        self.modified_output(results, output, 'relay_servers')

    @results_message
    @check_permissions(Permissions.READ)
    def get_relays(self, active_view, view_name):
        if not view_name and active_view == DefaultViews.GLOBAL:
            results = get_all_relay_server(view_name=None)
        elif view_name == DefaultViews.GLOBAL:
            results = get_all_relay_server(view_name=None)
        elif view_name and view_name != DefaultViews.GLOBAL:
            results = get_all_relay_server(view_name=view_name)
        else:
            results = get_all_relay_server(view_name=active_view)

        return results

    @api_catch_it
    @authenticated_request
    def delete(self):
        username = self.get_current_user()
        view_name = UserManager(username).properties.current_view
        relay_servers = self.arguments.get('relay_servers')
        output = self.arguments.get('output', 'json')
        results = self.delete_relays(relay_servers, view_name)
        self.set_status(results.http_status_code)
        self.modified_output(results, output, 'relay_servers')

    @results_message
    @check_permissions(Permissions.READ)
    def delete_relays(self, relay_servers, view_name):
        results = ApiResults()
        results.fill_in_defaults()
        deleted_relay_servers = []
        failed_to_delete_relay_servers = []
        for relay_server in relay_servers:
            manager = RelayServerManager()
            current_results = manager.remove()
            if (current_results.generic_status_code ==
                    RelayServerCodes.ObjectsDeleted):
                deleted_relay_servers.deleted_ids.append(relay_server)
            else:
                failed_to_delete_relay_servers.append(relay_server)
        if len(deleted_relay_servers) == len(relay_servers):
            results.generic_status_code = RelayServerCodes.ObjectDeleted
            results.vfense_status_code = RelayServerCodes.RelayServerRemoved
        else:
            results.generic_status_code = (
                RelayServerFailureCodes.FailedToDeleteObject
            )
            results.vfense_status_code = (
                RelayServerFailureCodes.FailedToRemoveRelayServer
            )
        return results

    @api_catch_it
    @authenticated_request
    @convert_json_to_arguments
    def post(self):
        relay = RelayServer()
        username = self.get_current_user()
        view_name = UserManager(username).properties.current_view
        output = self.arguments.get('output', 'json')
        relay.relay_name = self.arguments.get('name')
        relay.address = self.arguments.get('address')
        relay.views = self.arguments.get('views', [])
        relay.views = list(set(relay.views).union(view_name))
        manager = RelayServerManager(relay_name=relay.relay_name)
        results = self.add_relay(manager, relay)
        self.set_status(results.http_status_code)
        self.modified_output(results, output, 'relay_servers')

    @results_message
    @check_permissions(Permissions.READ)
    def add_relay(self, manager, relay):
        results = manager.create(relay)
        return results


class RelayServerHandler(BaseHandler):
    @api_catch_it
    @authenticated_request
    def get(self, relay_name):
        results = self.get_relay(relay_name)
        output = self.arguments.get('output', 'json')
        self.set_status(results.http_status_code)
        self.modified_output(results, output, 'relay_servers')

    @results_message
    @check_permissions(Permissions.READ)
    def get_relay(self, relay_name):
        results = get_relay_server(relay_name)
        return results

    @api_catch_it
    @authenticated_request
    @convert_json_to_arguments
    def put(self, relay_name):
        relay = RelayServer()
        relay.address = self.arguments.get('address', None)
        relay.views = self.arguments.get('views', None)
        results = self.update_relay(relay_name, relay)
        output = self.arguments.get('output', 'json')
        self.set_status(results.http_status_code)
        self.modified_output(results, output, 'relay_servers')

    @results_message
    @check_permissions(Permissions.READ)
    def update_relay(self, relay_name, relay):
        manager = RelayServerManager(relay_name=relay_name)
        results = manager.__edit_properties(relay)
        return results

    @api_catch_it
    @authenticated_request
    def delete(self, relay_name):
        output = self.arguments.get('output', 'json')
        results = self.delete_relay(relay_name)
        self.set_status(results.http_status_code)
        self.modified_output(results, output, 'relay_servers')

    @results_message
    @check_permissions(Permissions.READ)
    def delete_relay(self, relay_name ):
        manager = RelayServerManager(relay_name=relay_name)
        results = manager.remove()
        return results
