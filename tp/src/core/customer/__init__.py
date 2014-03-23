CustomersCollection = 'customers'
CustomersPerUserCollection = 'customers_per_user'
DEFAULT_CUSTOMER = 'default'

class CustomerKeys():
    CustomerName = 'customer_name'
    Properties = 'properties'
    NetThrottle = 'net_throttle'
    CpuThrottle = 'cpu_throttle'
    PackageUrl = 'package_download_url_base'
    OperationTtl = 'operation_ttl'

class CustomerPerUserKeys():
    CustomerName = 'customer_name'
    UserName = 'user_name'
    Id = 'id'

class CustomerPerUserIndexes():
    CustomerName = 'customer_name'
