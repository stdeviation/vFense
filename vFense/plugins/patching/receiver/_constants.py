class RefreshAppsResultsKeys(object):
    AgentId = 'agent_id'
    OperationId = 'operation_id'
    Error = 'error'
    Success = 'success'
    AppsData = 'apps_data'
    StatusCode = 'status_code'


class RefreshAppsResultsDefaults(object):
    @staticmethod
    def error():
        return None

    @staticmethod
    def success():
        return 'true'
