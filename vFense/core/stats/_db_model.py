class StatsCollections():
    AgentStats = 'agent_stats'


class AgentStatKeys():
    Id = 'id'
    AgentId = 'agent_id'
    StatType = 'stat_type'
    LastUpdated = 'last_updated'


class CpuStatKeys(AgentStatKeys):
    Idle = 'idle'
    System = 'system'
    User = 'user'
    IOWait = 'iowait'
    Total = 'total'


class MemoryStatKeys(AgentStatKeys):
    UsedPercent = 'used_percent'
    FreePercent = 'free_percent'
    Used = 'used'
    Free = 'free'
    Total = 'total'


class FileSystemStatKeys(MemoryStatKeys):
    Name = 'name'
    Mount = 'mount'


class StatsPerAgentIndexes():
    AgentId = 'agent_id'
    StatType = 'stat_type'
    AgentIdAndStatType = 'agent_id_and_stat_type'
