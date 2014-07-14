from json import dumps
a = {
    "http_method": "POST",
    "http_status": 200,
    "generated_ids": "f1e2b0fb-5b30-4ed7-89ba-50e65001b525",
    "message": "Agent f1e2b0fb-5b30-4ed7-89ba-50e65001b525 added successfully",
    "vfense_status_code": 3200,
    "uri": "/rvl/v2/core/newagent",
    "data": [
        {
            "operation_id": "",
            "operation": "new_agent_id",
            "agent_id": "f1e2b0fb-5b30-4ed7-89ba-50e65001b525"
        },
        {
            "count": 1,
            "vfense_status_code": 1001,
            "generic_status_code": 1001,
            "message": "get_result_uris - response uris retrieved successfully.",
            "db_status_code": 0,
            "data": {
                "reboot": {
                    "response_uri": "rvl/v1/f1e2b0fb-5b30-4ed7-89ba-50e65001b525/core/results/reboot",
                    "request_method": "PUT"
                },
                "check_in": {
                    "response_uri": "rvl/v1/f1e2b0fb-5b30-4ed7-89ba-50e65001b525/core/checkin",
                    "request_method": "GET"
                },
                "uninstall_agent": {
                    "response_uri": "rvl/v1/f1e2b0fb-5b30-4ed7-89ba-50e65001b525/rv/results/uninstall",
                    "request_method": "PUT"
                },
                "startup": {
                    "response_uri": "rvl/v1/f1e2b0fb-5b30-4ed7-89ba-50e65001b525/core/results/startup",
                    "request_method": "PUT"
                },
                "available_agent_update": {
                    "response_uri": "rvl/v1/rv/available_agent_update",
                    "request_method": "PUT"
                },
                "updatesapplications": {
                    "response_uri": "rvl/v1/f1e2b0fb-5b30-4ed7-89ba-50e65001b525/rv/updatesapplications",
                    "request_method": "PUT"
                },
                "install_os_apps": {
                    "response_uri": "rvl/v1/f1e2b0fb-5b30-4ed7-89ba-50e65001b525/rv/results/install/apps/",
                    "request_method": "PUT"
                },
                "install_supported_apps": {
                    "response_uri": "rvl/v1/f1e2b0fb-5b30-4ed7-89ba-50e65001b525/rv/results/install/apps/supported",
                    "request_method": "PUT"
                },
                "refresh_response_uris": {
                    "response_uri": "rvl/v1/core/uris/response",
                    "request_method": "GET"
                },
                "install_agent_update": {
                    "response_uri": "rvl/v1/f1e2b0fb-5b30-4ed7-89ba-50e65001b525/rv/results/install/apps/agent",
                    "request_method": "PUT"
                },
                "logout": {
                    "response_uri": "rvl/v1/rvl/logout",
                    "request_method": "GET"
                },
                "shutdown": {
                    "response_uri": "rvl/v1/f1e2b0fb-5b30-4ed7-89ba-50e65001b525/core/results/shutdown",
                    "request_method": "PUT"
                },
                "new_agent": {
                    "response_uri": "rvl/v1/core/newagent",
                    "request_method": "POST"
                },
                "login": {
                    "response_uri": "rvl/v1/rvl/login",
                    "request_method": "POST"
                },
                "install_custom_apps": {
                    "response_uri": "rvl/v1/f1e2b0fb-5b30-4ed7-89ba-50e65001b525/rv/results/install/apps/custom",
                    "request_method": "PUT"
                },
                "monitor_data": {
                    "response_uri": "rvl/v1/f1e2b0fb-5b30-4ed7-89ba-50e65001b525/monitoring/monitordata",
                    "request_method": "POST"
                },
                "uninstall": {
                    "response_uri": "rvl/v1/f1e2b0fb-5b30-4ed7-89ba-50e65001b525/rv/results/uninstall",
                    "request_method": "PUT"
                }
            },
            "operation": "refresh_response_uris"
        }
    ]
}
print dumps(a, indent=4)

