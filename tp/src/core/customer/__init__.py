from vFense.core._constants import CPUThrottleValues

class CustomerCollections():
    Customers = 'customers'
    CustomersPerUser = 'customers_per_user'


class CustomerKeys():
    CustomerName = 'customer_name'
    Properties = 'properties'
    NetThrottle = 'net_throttle'
    CpuThrottle = 'cpu_throttle'
    PackageUrl = 'package_download_url_base'
    ServerQueueTTL = 'server_queue_ttl' # in minutes
    AgentQueueTTL = 'agent_queue_ttl' # in minutes
    Users = 'users' #Mapped Keys
    Groups = 'groups' #Mapped Keys


class CustomerPerUserKeys():
    CustomerName = 'customer_name'
    UserName = 'user_name'
    Id = 'id'


class CustomerPerUserIndexes():
    CustomerName = 'customer_name'
    UserName = 'user_name'


class Customer(object):
    """Used to represent an instance of a customer."""

    def __init__(
        self, name, net_throttle=None, cpu_throttle=None,
        server_queue_ttl=None, agent_queue_ttl=None,
        package_download_url=None
    ):
        self.name = name
        self.net_throttle = net_throttle
        self.cpu_throttle = cpu_throttle
        self.server_queue_ttl = server_queue_ttl
        self.agent_queue_ttl = agent_queue_ttl
        self.package_download_url = package_download_url

        if net_throttle:
            self.net_throttle = int(net_throttle)

        if server_queue_ttl:
            self.server_queue_ttl = int(server_queue_ttl)

        if agent_queue_ttl:
            self.agent_queue_ttl = int(agent_queue_ttl)

    def get_invalid_fields(self):
        """Check the customer for any invalid fields.
        
        Returns:
            (list): List of key/value pair dictionaries corresponding
                to the invalid fields.
        """
        invalid_fields = []

        if not isinstance(self.name, basestring):
            invalid_fields.append(
                {CustomerKeys.CustomerName: self.name}
            )

        if self.net_throttle:
            if isinstance(self.net_throttle, int):
                if self.net_throttle < 0:
                    invalid_fields.append(
                        {CustomerKeys.NetThrottle: self.net_throttle}
                    )
            else:
                invalid_fields.append(
                    {CustomerKeys.NetThrottle: self.net_throttle}
                )

        if self.cpu_throttle:
            if self.cpu_throttle not in CPUThrottleValues.VALID_VALUES:
                invalid_fields.append(
                    {CustomerKeys.CpuThrottle: self.cpu_throttle}
                )

        if self.server_queue_ttl:
            if isinstance(self.server_queue_ttl, int):
                if self.server_queue_ttl <= 0:
                    invalid_fields.append(
                        {CustomerKeys.ServerQueueTTL: self.server_queue_ttl}
                    )
            else:
                invalid_fields.append(
                    {CustomerKeys.ServerQueueTTL: self.server_queue_ttl}
                )

        if self.agent_queue_ttl:
            if isinstance(self.agent_queue_ttl, int):
                if self.agent_queue_ttl <= 0:
                    invalid_fields.append(
                        {CustomerKeys.AgentQueueTTL: self.agent_queue_ttl}
                    )
            else:
                invalid_fields.append(
                    {CustomerKeys.AgentQueueTTL: self.agent_queue_ttl}
                )

        # TODO: check for invalid package url

        return invalid_fields

    def to_dict(self):
        return {
            CustomerKeys.CustomerName: self.name,
            CustomerKeys.NetThrottle: self.net_throttle,
            CustomerKeys.CpuThrottle: self.cpu_throttle,
            CustomerKeys.ServerQueueTTL: self.server_queue_ttl,
            CustomerKeys.AgentQueueTTL: self.agent_queue_ttl,
            CustomerKeys.PackageUrl: self.package_download_url
        }

    def to_dict_non_null(self):
        """ Use to get non None attributes of customer. Useful when
        filling out just a few fields to update the customer in the db.

        Returns:
            (dict): a dictionary with non None items.
        """
        customer_dict = self.to_dict()

        return {k:customer_dict[k] for k in customer_dict
                if customer_dict[k] != None}


