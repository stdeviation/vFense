class NotificationCollections():
    Notifications = 'notifications'
    NotificationsHistory = 'notifications_history'


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
    ThresholdAndView = 'threshold_and_view'
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
