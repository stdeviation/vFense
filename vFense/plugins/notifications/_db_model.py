class NotificationCollections():
    Notifications = 'notifications'
    NotificationsHistory = 'notifications_history'
    NotificationPlugins = 'notification_plugins'


class NotificationKeys():
    NotificationId = 'notification_id'
    NotificationType = 'notification_type'
    RuleName = 'rule_name'
    RuleDescription = 'rule_description'
    CreatedBy = 'created_by'
    CreatedTime = 'created_time'
    ModifiedBy = 'modified_by'
    ModifiedTime = 'modified_time'
    Plugin = 'plugin'
    User = 'user'
    Group = 'group'
    AllAgents = 'all_agents'
    Agents = 'agents'
    Tags = 'tags'
    ViewName = 'view_name'
    Threshold = 'threshold'
    FileSystem = 'file_system'


class NotificationIndexes():
    ViewName = 'view_name'
    RuleNameAndView = 'rule_name_and_view'
    NotificationTypeAndView = 'notification_type_and_view'
    AppThresholdAndView = 'threshold_and_view'
    ThresholdAndFileSystemAndView = (
        'threshold_and_fs_and_view'
    )


class NotificationHistoryKeys():
    Id = 'id'
    NotificationId = 'notification_id'
    AlertSent = 'alert_sent'
    AlertSentTime = 'alert_sent_time'


class NotificationHistoryIndexes():
    NotificationId = 'notification_id'


class NotificationPluginKeys():
    Id = 'id'
    ViewName = 'view_name'
    PluginName = 'plugin_name'
    CreatedTime = 'created_time'
    ModifiedTime = 'modified_time'
    CreatedBy = 'created_by'
    ModifiedBy = 'modified_by'
    UserName = 'username'
    Password = 'password'
    Server = 'server'
    Port = 'port'
    IsTls = 'is_tls'
    IsSsl = 'is_ssl'
    FromEmail = 'from_email'
    ToEmail = 'to_email'


class NotificationPluginIndexes():
    ViewName = 'view_name'
