import re
from vFense import Base
from vFense.core._db_constants import DbTime
from vFense.core.agent._constants import agent_regex
from vFense.core._constants import CommonKeys
from vFense.core.results import ApiResultKeys
from vFense.core.status_codes import GenericCodes
from vFense.core.queue._db_model import AgentQueueKey
from vFense.core.queue._constants import AgentQueueOperationDefaults


class AgentQueue(Base):
    """Used to represent an instance of an AgentQueue."""

    def __init__(self, id=None, agent_id=None, view_name=None, plugin=None,
                 request_method=None, response_uri=None, order_id=None,
                 created_time=None, expire_minutes=None, operation_id=None,
                 server_queue_ttl=None, agent_queue_ttl=None, operation=None,
                 **kwargs
                 ):
        """
        Kwargs:
            id (str): The primary key of this queue instance.
            agent_id (str): The id of the agent.
            view_name (str): The name of the view this operation belongs to.
            request_method (str): PUT, POST, DELETE, GET, UPDATE
            response_uri (str): The full url, this agent will send the
                results too.
            order_id (int): The order in thw queue, this operation belongs in.
            created_time (float): The time in epoch.
            expire_minutes (int): The number of minutes, until this operation
                is considered invalid.
            server_queue_ttl (float): The time in epoch, when this operation
                is considered expired on the server.
            agent_queue_ttl (float): The time in epoch, when this operation
                is considered expired on the agent.
            operation (str): The operation type
            operation_id  (str): The 36 Character UUID of the operation.
            plugin (str): The name of the plugin this operation belongs too.
        """
        super(AgentQueue, self).__init__(**kwargs)
        self.id = id
        self.agent_id = agent_id
        self.view_name = view_name
        self.request_method = request_method
        self.response_uri = response_uri
        self.order_id = order_id
        self.created_time = created_time
        self.expire_minutes = expire_minutes
        self.server_queue_ttl = server_queue_ttl
        self.agent_queue_ttl = agent_queue_ttl
        self.operation = operation
        self.operation_id = operation_id
        self.plugin = plugin


    def get_invalid_fields(self):
        """Check for any invalid fields.
        Returns:
            (list): List of invalid fields
        """
        invalid_fields = []

        if self.agent_id:
            if not isinstance(self.agent_id, str):
                invalid_fields.append(
                    {
                        AgentQueueKey.AgentId: self.agent_id,
                        CommonKeys.REASON: 'Must be a String',
                        ApiResultKeys.VFENSE_STATUS_CODE: (
                            GenericCodes.InvalidValue
                        )
                    }
                )

            elif not re.search(agent_regex(), self.agent_id):
                invalid_fields.append(
                    {
                        AgentQueueKey.AgentId: self.agent_id,
                        CommonKeys.REASON: 'Not a valid agent id',
                        ApiResultKeys.VFENSE_STATUS_CODE: (
                            GenericCodes.InvalidValue
                        )
                    }
                )

        if self.order_id:
            if not isinstance(self.order_id, int):
                invalid_fields.append(
                    {
                        AgentQueueKey.OrderId: self.order_id,
                        CommonKeys.REASON: 'Must be an intenger',
                        ApiResultKeys.VFENSE_STATUS_CODE: (
                            GenericCodes.InvalidValue
                        )
                    }
                )

        if self.created_time:
            if (not isinstance(self.created_time, float) and
                    not isinstance(self.created_time, int)):
                invalid_fields.append(
                    {
                        AgentQueueKey.CreatedTime: self.created_time,
                        CommonKeys.REASON: 'Must be an integer or a float',
                        ApiResultKeys.VFENSE_STATUS_CODE: (
                            GenericCodes.InvalidValue
                        )
                    }
                )

        if self.server_queue_ttl:
            if (not isinstance(self.server_queue_ttl, float) and
                    not isinstance(self.server_queue_ttl, int)):
                invalid_fields.append(
                    {
                        AgentQueueKey.ServerQueueTTL: self.server_queue_ttl,
                        CommonKeys.REASON: 'Must be an integer or a float',
                        ApiResultKeys.VFENSE_STATUS_CODE: (
                            GenericCodes.InvalidValue
                        )
                    }
                )

        if self.agent_queue_ttl:
            if (not isinstance(self.agent_queue_ttl, float) and
                    not isinstance(self.agent_queue_ttl, int)):
                invalid_fields.append(
                    {
                        AgentQueueKey.AgentQueueTTL: self.agent_queue_ttl,
                        CommonKeys.REASON: 'Must be an integer or a float',
                        ApiResultKeys.VFENSE_STATUS_CODE: (
                            GenericCodes.InvalidValue
                        )
                    }
                )

        if self.expire_minutes:
            if not isinstance(self.expire_minutes, int):
                invalid_fields.append(
                    {
                        AgentQueueKey.ExpireMinutes: self.expire_minutes,
                        CommonKeys.REASON: 'Must be an intenger',
                        ApiResultKeys.VFENSE_STATUS_CODE: (
                            GenericCodes.InvalidValue
                        )
                    }
                )

        if self.expired:
            if not isinstance(self.expired, bool):
                invalid_fields.append(
                    {
                        AgentQueueKey.Expired: self.expired,
                        CommonKeys.REASON: 'Must be a bool',
                        ApiResultKeys.VFENSE_STATUS_CODE: (
                            GenericCodes.InvalidValue
                        )
                    }
                )


        return invalid_fields

    def to_dict(self):
        """ Turn the fields into a dictionary.

        Returns:
            (dict): A dictionary with the fields.
        """

        return {
            AgentQueueKey.AgentId: self.agent_id,
            AgentQueueKey.OrderId: self.order_id,
            AgentQueueKey.OperationId: self.operation_id,
            AgentQueueKey.CreatedTime: self.created_time,
            AgentQueueKey.ServerQueueTTL: self.server_queue_ttl,
            AgentQueueKey.AgentQueueTTL: self.agent_queue_ttl,
            AgentQueueKey.ExpireMinutes: self.expire_minutes,
            AgentQueueKey.ViewName: self.view_name,
            AgentQueueKey.Operation: self.operation,
            AgentQueueKey.Plugin: self.plugin,
            AgentQueueKey.RequestMethod: self.request_method,
            AgentQueueKey.ResponseURI: self.response_uri,
        }

    def to_dict_db(self):
        """ Turn the fields into a dictionary, with db related fields.

        Returns:
            (dict): A dictionary with the fields.

        """

        data = {
            AgentQueueKey.CreatedTime: (
                DbTime.epoch_time_to_db_time(self.created_time)
            ),
            AgentQueueKey.ServerQueueTTL: (
                DbTime.epoch_time_to_db_time(self.server_queue_ttl)
            ),
            AgentQueueKey.AgentQueueTTL: (
                DbTime.epoch_time_to_db_time(self.agent_queue_ttl)
            ),
        }

        combined_data = dict(self.to_dict_non_null().items() + data.items())
        return combined_data


class AgentQueueOperation(Base):
    """Used to represent an instance of an admin operation."""

    def __init__(self, agent_id=None, operation=None, operation_id=None,
                 plugin=None, data=None, **kwargs
                 ):
        """
        Kwargs:
            agent_id (str): The id of the agent.
            operation (str): The operation that is to be performed.
                example.. reboot, shutdown, install, refresh_apps, etc..
            operation_id (str): The operation id, this operation belongs too.
            plugin (str): rv, core, vuln, etc ..
        """
        super(AgentQueueOperation, self).__init__(**kwargs)
        self.agent_id = agent_id
        self.operation = operation
        self.operation_id = operation_id
        self.data = data
        self.plugin = plugin

    def fill_in_defaults(self):
        """Replace all the fields that have None as their value with
        the hardcoded default values.
        """
        if not self.data:
            self.data = AgentQueueOperationDefaults.data()

    def to_dict(self):
        """ Turn the fields into a dictionary.

        Returns:
            (dict): A dictionary with the fields.

        """

        return {
            AgentQueueKey.Operation: self.operation,
            AgentQueueKey.OperationId: self.operation_id,
            AgentQueueKey.AgentId: self.agent_id,
            AgentQueueKey.Plugin: self.plugin,
            AgentQueueKey.Data: self.data,
        }
