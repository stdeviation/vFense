from vFense.plugins.notifications.api.email_api import (
    CreateEmailConfigHandler, GetEmailConfigHandler
)
from vFense.plugins.notifications.api.notification_handler import (
    GetAllValidFieldsForNotifications, NotificationsHandler,
    NotificationHandler
)

def api_handlers():
    handlers = [
        ##### Email API Handlers
        (r"/api/email/config/create?", CreateEmailConfigHandler),
        (r"/api/email/config/list?", GetEmailConfigHandler),
        ##### Notification API
        (r"/api/v1/notifications?", NotificationsHandler),
        (r"/api/v1/notification/([a-f0-9]{8}-[a-f0-9]{4}-4[a-f0-9]{3}-[a-f0-9]{4}-[a-f0-9]{12})?", NotificationHandler),
        (r"/api/v1/notifications/get_valid_fields/?", GetAllValidFieldsForNotifications),
    ]
    return handlers
