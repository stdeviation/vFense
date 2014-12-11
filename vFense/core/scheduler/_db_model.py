class JobCollections():
    Jobs = 'jobs'
    JobsHistory = 'jobs_history'
    AdministrativeJobs = 'administrative_jobs'


class JobKeys():
    Id = 'id'
    Name = 'name'
    Kwargs = 'kwargs'
    Args = 'Args'
    Runs = 'runs'
    Operation = 'operation'
    ViewName = 'view_name'
    StartDate = 'start_date'
    EndDate = 'end_date'
    RunDate = 'run_date'
    TimeZone = 'time_zone'
    NextRunTime = 'next_run_time'
    Trigger = 'trigger'
    JobState = 'job_state'
    CreatedTime = 'created_time'


class JobHistoryKeys(JobKeys):
    pass


class JobKwargKeys():
    Agents = 'agents'
    AgentIds = 'agent_ids'
    AllAgents = 'all_agents'
    Tags = 'tags'
    TagIds = 'tag_ids'
    AllTags = 'all_tags'
    UserName = 'user_name'
    ViewName = 'view_name'

class JobIndexes():
    NextRunTime = 'next_run_time'
    ViewName = 'view_name'


class JobHistoryIndexes(JobIndexes):
    pass
