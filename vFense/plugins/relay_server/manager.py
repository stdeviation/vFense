
from vFense.core.results import ApiResults
from vFense.core.status_codes import DbCodes
from vFense.plugins.relay_server.status_codes import (
    RelayServerCodes, RelayServerFailureCodes
)
from vFense.plugins.relay_server import RelayServer
from vFense.plugins.relay_server._db import (
    fetch_relay, add_relay, delete_relay, fetch_all_relays, update_relay
)

def get_all_relay_server(view_name=None):
    results = ApiResults()
    results.fill_in_defaults()
    results.data = fetch_all_relays(view_name)
    results.generic_status_code = RelayServerCodes.InformationRetrieved
    results.vfense_status_code = RelayServerCodes.InformationRetrieved
    return results

def get_relay_server(relay_name=None):
    results = ApiResults()
    results.fill_in_defaults()
    results.data = fetch_relay(relay_name)
    results.generic_status_code = RelayServerCodes.InformationRetrieved
    results.vfense_status_code = RelayServerCodes.InformationRetrieved
    return results


class RelayServerManager(object):
    def __init__(self, relay_name=None):
        self.relay_name = relay_name
        self.properties = self._relay_attributes()

    def _relay_attributes(self):
        relay = RelayServer()
        if self.relay_name:
            relay_data = fetch_relay(self.relay_name)
            if relay_data:
                relay = RelayServer(**relay_data)

        return relay

    def create(self, relay):
        """Add a relay server into vFense.
        Args:
            relay (RelayServer): An instance of RelayServer.

        Basic Usage:
            >>> from vFense.plugins.relay_server.manager import RelayServerManager
            >>> from vFense.plugins.relay_server import RelayServer
            >>> relay = RelayServer(relay_name='remote_vfense_repo',
                                    address='relay_server.local',
                                    views=['global'])
            >>> manager = RelayServerManager()
            >>> results = manager.create(relay)
            >>> results.generated_ids
            u'remote_vfense_repo'

        Returns:
            ApiResults instance
            Check vFense.core.results for all the attributes and methods
            for the instance.
        """
        results = ApiResults()
        results.fill_in_defaults()
        if isinstance(relay, RelayServer):
            invalid_fields = relay.get_invalid_fields()
            relay.fill_in_defaults()
            if not invalid_fields:
                status_code, _, _, generated_ids = (
                    add_relay(relay.to_dict_non_null())
                )
                if status_code == DbCodes.Inserted:
                    self.properties = self._relay_attributes()
                    msg = (
                        'Relay server {0} was added successfully'
                        .format(relay.name)
                    )
                    results.generic_status_code = (
                        RelayServerCodes.ObjectCreated
                    )
                    results.vfense_status_code = (
                        RelayServerCodes.RelayServerCreated
                    )
                    results.message = msg
                    results.data.append(relay.to_dict())
                    results.generated_ids.append(self.relay_name)

                else:
                    msg = (
                        'Failed to add relay server {0}.'
                        .format(relay.relay_name)
                    )
                    results.generic_status_code = (
                        RelayServerFailureCodes.FailedToCreateObject
                    )
                    results.vfense_status_code = (
                        RelayServerFailureCodes.FailedToAddRelayServer
                    )
                    results.message = msg
                    results.data.append(relay.to_dict())

            else:
                msg = (
                    'Failed to add relay_server, invalid fields were passed'
                )
                results.generic_status_code = (
                    RelayServerFailureCodes.FailedToCreateObject
                )
                results.vfense_status_code = (
                    RelayServerFailureCodes.FailedToAddRelayServer
                )
                results.message = msg
                results.errors = invalid_fields
                results.data.append(relay.to_dict())

        else:
            msg = (
                'Invalid {0} Instance, must pass an instance of Agent.'
                .format(type(relay))
            )
            results.generic_status_code = (
                RelayServerCodes.FailedToCreateObject
            )
            results.vfense_status_code = (
                RelayServerFailureCodes.FailedToAddRelayServer
            )
            results.message = msg

        return results

    def update_address(self, address):
        """Update the address of the relay server

        Basic Usage:
            >>> from vFense.plugins.relay_server.manager import RelayServerManager
            >>> manager = RelayServerManager(relay_name='nyc_vfense.local')
            >>> manager.update_address('10.0.0.1')

        Returns:
            ApiResults instance
        """
        relay = RelayServer(address=address)
        results = self.__edit_properties(relay)
        return results

    def __edit_properties(self, relay):
        """ Edit the properties of this relay.
        Args:
            relay (RelayServer): The RelayServer instance with all of its
                properties.

        Basic Usage:
            >>> from vFense.plugins.relay_server import RelayServer
            >>> from vFense.plugins.relay_server.manager import RelayServerManager
            >>> relay = (
                    RelayServer(address='10.0.0.1', views=['test view 1])
                )
            >>> manager = RelayServerManager('nyc_vfense_relay')
            >>> manager.__edit_properties(relay)

        Return:
            ApiResults instance
        """

        results = ApiResults()
        results.fill_in_defaults()
        if isinstance(relay, RelayServer):
            if self.properties.relay_name:
                invalid_fields = relay.get_invalid_fields()
                if not invalid_fields:
                    object_status, count, errors, _ = (
                        update_relay(self.relay_name, relay.to_dict_non_null())
                    )

                    if object_status == DbCodes.Replaced:
                        results.message = (
                            'Relay server {0} was updated'
                            .format(self.relay_name)
                        )
                        results.generic_status_code = (
                            RelayServerCodes.ObjectUpdated
                        )
                        results.vfense_status_code = (
                            RelayServerCodes.RelayServerUpdated
                        )
                        results.updated_ids.append(self.relay_name)
                        results.data.append(relay.to_dict_non_null())

                    elif object_status == DbCodes.Unchanged:
                        results.message = (
                            'Agent {0} was not updated'
                            .format(self.relay_name)
                        )
                        results.generic_status_code = (
                            RelayServerCodes.ObjectUnchanged
                        )
                        results.vfense_status_code = (
                            RelayServerCodes.RelayServerUnchanged
                        )
                        results.unchanged_ids.append(self.relay_name)
                        results.data.append(relay.to_dict_non_null())

                else:
                    results.generic_status_code = RelayServerCodes.InvalidId
                    results.vfense_status_code = (
                        RelayServerFailureCodes.FailedToUpdateRelayServer
                    )
                    results.message = (
                        'Relay server {0} properties were invalid'
                        .format(self.relay_name)
                    )
                    results.unchanged_ids.append(self.relay_name)
                    results.errors = invalid_fields
                    results.data.append(relay.to_dict_non_null())

            else:
                results.generic_status_code = RelayServerCodes.InvalidId
                results.vfense_status_code = (
                    RelayServerFailureCodes.RelayServerDoesNotExist
                )
                results.message = (
                    'Relay server {0} does not exist'.format(self.relay_name)
                )
                results.unchanged_ids.append(self.relay_name)

        else:
            results.generic_status_code = RelayServerCodes.InvalidId
            results.vfense_status_code = (
                RelayServerFailureCodes.InvalidInstanceType
            )
            results.message = (
                'Relay server {0} is not of instance RelayServer, instanced passed {1}'
                .format(self.relay_name, type(relay))
            )
            results.unchanged_ids.append(self.relay_name)

        return results

    def remove(self):
        """Remove relay server from the system.

        Basic Usage:
            >>> from vFense.plugins.relay_server import RelayServer
            >>> from vFense.plugins.relay_server.manager import RelayServerManager
            >>> manager = RelayServerManager(relay_name='remote_vfense_repo')
            >>> manager.remove()

        Return:
            ApiResults instance
        """

        results = ApiResults()
        results.fill_in_defaults()
        if self.properties.relay_name:
            status_code, _, _, _ = delete_relay(self.relay_name)
            if status_code == DbCodes.Deleted:
                msg = (
                    'Relay Server {0} was deleted'.format(self.relay_name)
                )
                results.message = msg
                results.generic_status_code = RelayServerCodes.ObjectDeleted
                results.vfense_status_code = (
                    RelayServerCodes.RelayServerRemoved
                )
                results.deleted_ids.append(self.relay_name)

            else:
                msg = (
                    'Invalid relay name {0}'.format(self.relay_name )
                )
                results.message = msg
                results.generic_status_code = RelayServerCodes.InvalidId
                results.vfense_status_code = RelayServerCodes.InvalidId
                results.unchanged_ids.append(self.relay_name)

        else:
            msg = 'Invalid relay name {0}'.format(self.relay_name)
            results.message = msg
            results.generic_status_code = RelayServerCodes.InvalidId
            results.vfense_status_code = RelayServerCodes.InvalidId
            results.unchanged_ids.append(self.relay_name)

        return results
