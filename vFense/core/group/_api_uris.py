from vFense.core.api.group import GroupHandler, GroupsHandler

def api_handlers():
    handlers = [
        ##### New Group API
        (r"/api/v1/group/([a-f0-9]{8}-[a-f0-9]{4}-4[a-f0-9]{3}-[a-f0-9]{4}-[a-f0-9]{12})?", GroupHandler),
        (r"/api/v1/groups?", GroupsHandler),
    ]
    return handlers
