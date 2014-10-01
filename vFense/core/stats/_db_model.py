class StatsCollections():
    AgentStats = 'agent_stats'

class AgentStatKeys():
    Id = 'id'
    AgentId = 'agent_id'
    StatType = 'stat_type'

class CpuStatKeys(AgentStatKeys):
    Idle = 'idle'
    System = 'system'
    User = 'user'
    IOWait = 'iowait'

class MemoryStatKeys(AgentStatKeys):
    UsedPercent = 'used_percent'
    FreePercent = 'free_percent'
    Used = 'used'
    Free = 'free'

class StatsPerAgentIndexes():
    AgentId = 'agent_id'
    StatType = 'stat_type'
    AgentIdAndStatType = 'agent_id_and_stat_type'
