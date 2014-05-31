class ViewCollections():
    Views = 'views'
    ViewsPerUser = 'views_per_user'


class ViewKeys():
    ViewName = 'view_name'
    Parent = 'parent'
    Ancestors = 'ancestors'
    Children = 'children'
    Properties = 'properties'
    NetThrottle = 'net_throttle'
    CpuThrottle = 'cpu_throttle'
    PackageUrl = 'package_download_url_base'
    ServerQueueTTL = 'server_queue_ttl' # in minutes
    AgentQueueTTL = 'agent_queue_ttl' # in minutes
    Users = 'users' #Mapped Keys
    Groups = 'groups' #Mapped Keys


class ViewPerUserKeys():
    ViewName = 'view_name'
    UserName = 'user_name'
    Id = 'id'


class ViewPerUserIndexes():
    ViewName = 'view_name'
    UserName = 'user_name'

