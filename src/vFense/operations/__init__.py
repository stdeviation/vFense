class OperationCollections():
    Agent = 'agent_operations'
    OperationPerAgent = 'operation_per_agent'
    OperationPerApp = 'operation_per_app'
    Admin = 'admin_operations'


class AdminOperationKey():
    OperationId = 'operation_id'
    CreatedBy = 'created_by'
    CreatedTime = 'created_time'
    StatusMessage = 'status_message'
    StatusCode = 'status_code'
    Action = 'action'
    ActionPerformedOn = 'action_performed_on'
    IdsCreated = 'ids_created'
    IdsUpdated = 'ids_updated'
    IdsRemoved = 'ids_removed'


class AgentOperationKey():
    OperationId = 'operation_id'
    Operation = 'operation'
    OperationStatus = 'operation_status'
    ActionPerformedOn = 'action_performed_on'
    CreatedTime = 'created_time'
    UpdatedTime = 'updated_time'
    CompletedTime = 'completed_time'
    CreatedBy = 'created_by'
    ViewName = 'view_name'
    AgentsTotalCount = 'agents_total_count'
    AgentsFailedCount = 'agents_failed_count'
    AgentsCompletedCount = 'agents_completed_count'
    AgentsExpiredCount = 'agents_expired_count'
    AgentsPendingResultsCount = 'agents_pending_results_count'
    AgentsPendingPickUpCount = 'agents_pending_pickup_count'
    AgentsCompletedWithErrorsCount = 'agents_completed_with_errors_count'
    Applications = 'applications'
    Agents = 'agents'
    Restart = 'restart'
    TagId = 'tag_id'
    AgentIds = 'agent_ids'
    Plugin = 'plugin'
    CpuThrottle = 'cpu_throttle'
    NetThrottle = 'net_throttle'


class AgentOperationIndexes():
    TagId = 'tag_id'
    AgentIds = 'agent_ids'
    ViewName = 'view_name'
    Operation = 'operation'
    OperationId = 'operation_id'
    OperationAndView = 'operation_and_view'
    PluginAndView = 'plugin_and_view'
    CreatedByAndView = 'createdby_and_view'


class OperationPerAgentKey():
    Id = 'id'
    AgentId = 'agent_id'
    TagId = 'tag_id'
    OperationId = 'operation_id'
    ViewName = 'view_name'
    Status = 'status'
    PickedUpTime = 'picked_up_time'
    ExpiredTime = 'expired_time'
    CompletedTime = 'completed_time'
    AppsTotalCount = 'apps_total_count'
    AppsPendingCount = 'apps_pending_count'
    AppsFailedCount = 'apps_failed_count'
    AppsCompletedCount = 'apps_completed_count'
    Errors = 'errors'


class OperationPerAgentIndexes():
    OperationId = 'operation_id'
    AgentIdAndView = 'agentid_and_view'
    OperationIdAndAgentId = 'operationid_and_agentid'
    TagIdAndView = 'tagid_and_view'
    StatusAndView = 'status_and_view'


class OperationPerAppKey():
    Id = 'id'
    AgentId = 'agent_id'
    AppId = 'app_id'
    AppName = 'app_name'
    AppVersion = 'app_version'
    AppsRemoved = 'apps_removed'
    OperationId = 'operation_id'
    ViewName = 'view_name'
    Results = 'results'
    ResultsReceivedTime = 'results_received_time'
    Errors = 'errors'


class OperationPerAppIndexes():
    OperationId = 'operation_id'
    OperationIdAndAgentId = 'operationid_and_agentid'
    OperationIdAndAgentIdAndAppId = 'operationid_and_agentid_and_appid'
