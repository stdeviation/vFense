from vFense.plugins.mightymouse.api.relay_servers import (
    RelayServerHandler, RelayServersHandler
)

def api_handlers():
    handlers = [
        ##### MightyMouse API Handlers
        (r'/api/v1/relay/([A-Za-z0-9:,"_ ]+.*)?', RelayServerHandler),
        (r"/api/v1/relay", RelayServersHandler)
    ]
    return handlers
